// SecureBank APT Detection Engine v4.0
// Build: g++ -std=c++14 -o apt_interactive apt_interactive.cpp

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <algorithm>
#include <ctime>
#include <sstream>
#include <iomanip>
#include <cstdlib>
#include <set>
#include <cstring>
#include <limits>

using namespace std;

// ─────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────
const string ALERT_EMAIL     = "preksha.kothari@cumminscollege.in";
const int    EMAIL_THRESHOLD = 30;
const int    WEEKEND_SCORE   = 10;
const int    HOLIDAY_SCORE   = 10;

const set<string> BANK_HOLIDAYS = {
    "2025-01-14","2025-01-26","2025-03-14","2025-04-10","2025-04-14",
    "2025-04-18","2025-05-12","2025-06-07","2025-08-15","2025-10-02",
    "2025-10-20","2025-10-21","2025-11-05","2025-12-25",
    "2024-01-26","2024-03-25","2024-04-14","2024-04-17","2024-05-23",
    "2024-06-17","2024-08-15","2024-10-02","2024-10-13","2024-11-01",
    "2024-11-15","2024-12-25"
};

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────
string currentTimestamp() {
    time_t now = time(NULL);
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
    return string(buf);
}

string toUpper(const string& s) {
    string result = s;
    transform(result.begin(), result.end(), result.begin(), ::toupper);
    return result;
}

bool parseDate(const string& d, struct tm& t) {
    memset(&t, 0, sizeof(t));
    if (d.size() != 10) return false;
    t.tm_year = stoi(d.substr(0,4)) - 1900;
    t.tm_mon  = stoi(d.substr(5,2)) - 1;
    t.tm_mday = stoi(d.substr(8,2));
    mktime(&t);
    return true;
}

string fmtDate(const struct tm& t) {
    char buf[16];
    strftime(buf, sizeof(buf), "%Y-%m-%d", &t);
    return string(buf);
}

int weekdayOf(const string& dateStr) {
    struct tm t;
    if (!parseDate(dateStr, t)) return -1;
    return t.tm_wday;
}

bool isWeekend(const string& dateStr) {
    int wd = weekdayOf(dateStr);
    return (wd == 0 || wd == 6);
}

bool isBankHoliday(const string& dateStr) {
    return BANK_HOLIDAYS.count(dateStr) > 0;
}

string weekdayName(int wd) {
    const char* names[] = {"Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"};
    if (wd < 0 || wd > 6) return "Unknown";
    return names[wd];
}

// ─────────────────────────────────────────────────────────────
// ENUMS
// ─────────────────────────────────────────────────────────────
enum class SecurityLevel { LOW, MEDIUM, HIGH, UNKNOWN_SL };

string slToString(SecurityLevel sl) {
    switch (sl) {
        case SecurityLevel::LOW:    return "LOW";
        case SecurityLevel::MEDIUM: return "MEDIUM";
        case SecurityLevel::HIGH:   return "HIGH";
        default:                    return "UNKNOWN";
    }
}

SecurityLevel parseSecurityLevel(const string& s) {
    string u = toUpper(s);
    if (u == "LOW")    return SecurityLevel::LOW;
    if (u == "MEDIUM") return SecurityLevel::MEDIUM;
    if (u == "HIGH")   return SecurityLevel::HIGH;
    return SecurityLevel::UNKNOWN_SL;
}

// ─────────────────────────────────────────────────────────────
// EMAIL
// ─────────────────────────────────────────────────────────────
void sendEmailAlert(const string& toAddress,
                    const string& subject,
                    const string& body) {
    string safeBody = body;
    size_t pos = 0;
    while ((pos = safeBody.find('"', pos)) != string::npos) {
        safeBody.replace(pos, 1, "'"); pos++;
    }
    string cmd = "powershell -ExecutionPolicy Bypass -File send_alert.ps1"
                 " -To \""      + toAddress + "\""
                 " -Subject \"" + subject   + "\""
                 " -Body \""    + safeBody  + "\"";
    int result = system(cmd.c_str());
    if (result == 0) cout << "[EMAIL] Alert sent to " << toAddress << "\n";
    else             cout << "[EMAIL] Failed to send alert (code " << result << ")\n";
}

// ─────────────────────────────────────────────────────────────
// ZONE STORE
// ─────────────────────────────────────────────────────────────
struct ZoneInfo { string name; SecurityLevel level; };

class ZoneStore {
public:
    unordered_map<string, ZoneInfo> zones;

    void addZone(const string& name, SecurityLevel level) {
        string key = toUpper(name);
        zones[key] = { key, level };
    }
    bool zoneExists(const string& name) const { return zones.count(toUpper(name)) > 0; }
    SecurityLevel getLevel(const string& name) const {
        auto it = zones.find(toUpper(name));
        return it == zones.end() ? SecurityLevel::UNKNOWN_SL : it->second.level;
    }
    void listZones() const {
        if (zones.empty()) { cout << "  (no zones defined yet)\n"; return; }
        cout << "  " << "Zone Name" << "  " << "Security Level" << "\n";
        for (auto it = zones.begin(); it != zones.end(); ++it)
            cout << "  " << it->second.name << "  " << slToString(it->second.level) << "\n";
    }

    bool removeZone(const string& name) {
        string key = toUpper(name);
        if (!zones.count(key)) return false;
        zones.erase(key);
        return true;
    }
};

// ─────────────────────────────────────────────────────────────
// NETWORK GRAPH
// ─────────────────────────────────────────────────────────────
struct NetworkNode { string description, zone, requiredRole; };

class NetworkGraph {
public:
    unordered_map<string, vector<string>> adjList;
    unordered_map<string, NetworkNode>   nodes;

    void addNode(const string& id, const string& desc,
                 const string& zone, const string& req) {
        string uid = toUpper(id);
        nodes[uid] = { desc, toUpper(zone), toUpper(req) };
        if (!adjList.count(uid)) adjList[uid] = vector<string>();
    }
    void addEdge(const string& from, const string& to) {
        string uf = toUpper(from), ut = toUpper(to);
        adjList[uf].push_back(ut);
        if (!adjList.count(ut)) adjList[ut] = vector<string>();
    }
    bool edgeExists(const string& from, const string& to) const {
        auto it = adjList.find(toUpper(from));
        if (it == adjList.end()) return false;
        return find(it->second.begin(), it->second.end(), toUpper(to)) != it->second.end();
    }
    bool isCriticalZone(const string& nodeId, const ZoneStore& zs) const {
        auto it = nodes.find(toUpper(nodeId));
        if (it == nodes.end()) return false;
        return zs.getLevel(it->second.zone) == SecurityLevel::HIGH;
    }
    bool nodeExists(const string& id) const { return nodes.count(toUpper(id)) > 0; }

    bool removeNode(const string& id) {
        string uid = toUpper(id);
        if (!nodes.count(uid)) return false;
        nodes.erase(uid);
        adjList.erase(uid);
        for (auto& kv : adjList) {
            auto& vec = kv.second;
            vec.erase(remove(vec.begin(), vec.end(), uid), vec.end());
        }
        return true;
    }

    bool removeEdge(const string& from, const string& to) {
        string uf = toUpper(from), ut = toUpper(to);
        auto it = adjList.find(uf);
        if (it == adjList.end()) return false;
        auto& vec = it->second;
        auto pos = find(vec.begin(), vec.end(), ut);
        if (pos == vec.end()) return false;
        vec.erase(pos);
        return true;
    }

    void listNodes(const ZoneStore& zs) const {
        if (nodes.empty()) { cout << "  (no nodes defined yet)\n"; return; }
        for (auto it = nodes.begin(); it != nodes.end(); ++it) {
            SecurityLevel sl = zs.getLevel(it->second.zone);
            cout << "  " << it->first << "  " << it->second.zone << "  "
                 << slToString(sl) << "  " << it->second.requiredRole << "\n";
        }
    }
    void listEdges() const {
        bool any = false;
        for (auto it = adjList.begin(); it != adjList.end(); ++it)
            for (size_t i = 0; i < it->second.size(); ++i) {
                cout << "  " << it->first << "  -->  " << it->second[i] << "\n";
                any = true;
            }
        if (!any) cout << "  (no edges defined yet)\n";
    }
};

// ─────────────────────────────────────────────────────────────
// PERMISSION STORE
// ─────────────────────────────────────────────────────────────
class PermissionStore {
public:
    unordered_map<string, vector<string>> userPermissions;
    unordered_map<string, string>         userRoles;
    unordered_map<string, string>         userMachines;

    void addUser(const string& user, const string& role,
                 const string& machine, const vector<string>& permitted) {
        string uuser = toUpper(user);
        userRoles[uuser]    = toUpper(role);
        userMachines[uuser] = toUpper(machine);
        vector<string> up;
        for (size_t i = 0; i < permitted.size(); ++i) up.push_back(toUpper(permitted[i]));
        userPermissions[uuser] = up;
    }
    bool isAuthorized(const string& user, const string& node) const {
        auto it = userPermissions.find(toUpper(user));
        if (it == userPermissions.end()) return false;
        return find(it->second.begin(), it->second.end(), toUpper(node)) != it->second.end();
    }
    string getRole(const string& user) const {
        auto it = userRoles.find(toUpper(user));
        return it == userRoles.end() ? "UNKNOWN" : it->second;
    }
    string getMachine(const string& user) const {
        auto it = userMachines.find(toUpper(user));
        return it == userMachines.end() ? "" : it->second;
    }
    bool userExists(const string& user) const { return userRoles.count(toUpper(user)) > 0; }
    void listUsers() const {
        if (userRoles.empty()) { cout << "  (no users defined yet)\n"; return; }
        for (auto it = userRoles.begin(); it != userRoles.end(); ++it) {
            const string& user = it->first;
            cout << "  " << user << "  " << it->second << "  "
                 << (userMachines.count(user) ? userMachines.at(user) : "-") << "  ";
            auto pit = userPermissions.find(user);
            if (pit != userPermissions.end() && !pit->second.empty()) {
                for (size_t i = 0; i < pit->second.size(); ++i) {
                    if (i) cout << ", ";
                    cout << pit->second[i];
                }
            } else cout << "(none)";
            cout << "\n";
        }
    }
    vector<string> getAllUsers() const {
        vector<string> r;
        for (auto it = userRoles.begin(); it != userRoles.end(); ++it)
            r.push_back(it->first);
        return r;
    }

    bool removeUser(const string& user) {
        string u = toUpper(user);
        if (!userRoles.count(u)) return false;
        userRoles.erase(u);
        userMachines.erase(u);
        userPermissions.erase(u);
        return true;
    }
};

// ─────────────────────────────────────────────────────────────
// BFS ANALYZER
// ─────────────────────────────────────────────────────────────
class BFSAnalyzer {
public:
    vector<string> findPath(NetworkGraph& graph,
                            const string& start, const string& target) {
        queue<pair<string, vector<string>>> q;
        unordered_set<string> visited;
        vector<string> init; init.push_back(toUpper(start));
        q.push(make_pair(toUpper(start), init));
        while (!q.empty()) {
            string node         = q.front().first;
            vector<string> path = q.front().second;
            q.pop();
            if (node == toUpper(target)) return path;
            if (visited.count(node)) continue;
            visited.insert(node);
            const vector<string>& nb = graph.adjList[node];
            for (size_t i = 0; i < nb.size(); ++i) {
                vector<string> np = path;
                np.push_back(nb[i]);
                q.push(make_pair(nb[i], np));
            }
        }
        return vector<string>();
    }
};

// ─────────────────────────────────────────────────────────────
// TRIE ENGINE
// ─────────────────────────────────────────────────────────────
struct TrieNode {
    unordered_map<string, TrieNode*> children;
    bool isEnd; string patternName;
    TrieNode() : isEnd(false) {}
};

class TrieEngine {
    TrieNode* root; int sigCount;
public:
    TrieEngine() : root(new TrieNode()), sigCount(0) {}
    void insert(const vector<string>& path, const string& name) {
        TrieNode* cur = root;
        for (size_t i = 0; i < path.size(); ++i) {
            string key = toUpper(path[i]);
            if (!cur->children.count(key)) cur->children[key] = new TrieNode();
            cur = cur->children[key];
        }
        cur->isEnd = true; cur->patternName = name; sigCount++;
    }
    string match(const vector<string>& path) const {
        TrieNode* cur = root;
        for (size_t i = 0; i < path.size(); ++i) {
            auto it = cur->children.find(toUpper(path[i]));
            if (it == cur->children.end()) return "";
            cur = it->second;
        }
        return cur->isEnd ? cur->patternName : "";
    }
    int count() const { return sigCount; }
};

// ─────────────────────────────────────────────────────────────
// SEGMENT TREE
// ─────────────────────────────────────────────────────────────
class SegmentTree {
    int n; vector<int> tree;
public:
    SegmentTree(int size = 24) : n(size), tree(4 * size, 0) {}
    void update(int node, int s, int e, int idx, int val) {
        if (s == e) { tree[node] += val; return; }
        int mid = (s + e) / 2;
        if (idx <= mid) update(2*node, s, mid, idx, val);
        else            update(2*node+1, mid+1, e, idx, val);
        tree[node] = tree[2*node] + tree[2*node+1];
    }
    int query(int node, int s, int e, int l, int r) const {
        if (r < s || e < l) return 0;
        if (l <= s && e <= r) return tree[node];
        int mid = (s + e) / 2;
        return query(2*node,s,mid,l,r) + query(2*node+1,mid+1,e,l,r);
    }
    void addEvent(int hour) { update(1, 0, n-1, hour, 1); }
    int offHoursBurst() const { return query(1,0,n-1,23,23)+query(1,0,n-1,0,4); }
    bool isOffHour(int hour) const { return hour >= 23 || hour <= 4; }
};

// ─────────────────────────────────────────────────────────────
// ALERT ENGINE
// ─────────────────────────────────────────────────────────────
struct ScoreItem { string reason; int points; };

struct AlertRecord {
    string user, role; int score;
    vector<ScoreItem> scoreItems; vector<string> path;
    bool operator<(const AlertRecord& o) const { return score < o.score; }
};

class AlertEngine {
    priority_queue<pair<int, AlertRecord>> pq;
public:
    void push(const AlertRecord& r) { pq.push(make_pair(r.score, r)); }
    vector<AlertRecord> getSorted() {
        priority_queue<pair<int, AlertRecord>> tmp = pq;
        vector<AlertRecord> res;
        while (!tmp.empty()) { res.push_back(tmp.top().second); tmp.pop(); }
        return res;
    }
    bool empty() const { return pq.empty(); }
};

// ─────────────────────────────────────────────────────────────
// SESSION EVENT
// ─────────────────────────────────────────────────────────────
struct SessionEvent { string device, date; int hour, minute; };

// ─────────────────────────────────────────────────────────────
// DETECTION ENGINE
// ─────────────────────────────────────────────────────────────
class DetectionEngine {
    NetworkGraph& graph; PermissionStore& perms; ZoneStore& zones;
    BFSAnalyzer bfs; TrieEngine& trie; AlertEngine& alerts;
    ofstream& alog; ofstream& aulog; int sessionCounter;
    void log(const string& s) { alog << s << "\n"; }
public:
    DetectionEngine(NetworkGraph& g, PermissionStore& p, ZoneStore& z,
                    TrieEngine& t, AlertEngine& a, ofstream& al, ofstream& aul)
        : graph(g), perms(p), zones(z), trie(t), alerts(a),
          alog(al), aulog(aul), sessionCounter(0) {}

    void analyseSession(const string& user, const vector<SessionEvent>& events) {
        sessionCounter++;
        string sidNum = to_string(sessionCounter);
        string sid    = "S-" + string(3-min(3,(int)sidNum.size()),'0') + sidNum;
        string uuser  = toUpper(user);
        string role   = perms.getRole(uuser);

        int score = 0;
        vector<ScoreItem> scoreItems;
        vector<string>    visitedPath;
        SegmentTree       segTree;
        string            prevDevice;

        set<string> scoredDates;

        for (size_t ei = 0; ei < events.size(); ++ei) {
            const SessionEvent& ev = events[ei];
            string udevice = toUpper(ev.device);
            segTree.addEvent(ev.hour);
            ostringstream ts;
            ts << setfill('0') << setw(2) << ev.hour << ":" << setw(2) << ev.minute;
            int wd = weekdayOf(ev.date);
            bool isWE = isWeekend(ev.date), isHoliday = isBankHoliday(ev.date);
            string dayName = weekdayName(wd);

            if (scoredDates.find(ev.date) == scoredDates.end()) {
                if (isWE && isHoliday) {
                    score += HOLIDAY_SCORE;
                    scoreItems.push_back({"Activity on weekend & bank holiday (" + dayName + " " + ev.date + ")", HOLIDAY_SCORE});
                    scoredDates.insert(ev.date);
                } else if (isWE) {
                    score += WEEKEND_SCORE;
                    scoreItems.push_back({"Activity on weekend (" + dayName + " " + ev.date + ")", WEEKEND_SCORE});
                    scoredDates.insert(ev.date);
                } else if (isHoliday) {
                    score += HOLIDAY_SCORE;
                    scoreItems.push_back({"Activity on bank holiday (" + ev.date + ")", HOLIDAY_SCORE});
                    scoredDates.insert(ev.date);
                }
            }

            if (!graph.nodeExists(udevice)) {
                score += 20;
                scoreItems.push_back({"Unknown device: "+udevice, 20});
                visitedPath.push_back(udevice); prevDevice = udevice; continue;
            }
            string edgeStatus = "";
            if (ei == 0) {
                string userMachine = perms.getMachine(uuser);
                if (!userMachine.empty() && graph.nodeExists(userMachine)) {
                    if (userMachine != udevice && !graph.edgeExists(userMachine, udevice)) {
                        score += 40;
                        scoreItems.push_back({"Initial phantom edge: " + userMachine + " -> " + udevice, 40});
                        edgeStatus = " | PHANTOM EDGE (no path from "+userMachine+")";
                    }
                }
            } else {
                if (!prevDevice.empty() && !graph.edgeExists(prevDevice, udevice)) {
                    score += 40;
                    scoreItems.push_back({"Phantom edge: "+prevDevice+" -> "+udevice, 40});
                    edgeStatus = " | PHANTOM EDGE (no path from "+prevDevice+")";
                }
            }

            bool auth = perms.isAuthorized(uuser, udevice);
            SecurityLevel devSecLevel = SecurityLevel::UNKNOWN_SL;
            if (graph.nodes.count(udevice))
                devSecLevel = zones.getLevel(graph.nodes.at(udevice).zone);

            string authStatus;
            if (auth) {
                authStatus = "AUTHORIZED";
                if (devSecLevel == SecurityLevel::HIGH)
                    authStatus += " | HIGH-SEC ZONE";
            } else {
                string req = graph.nodes.count(udevice) ?
                             graph.nodes.at(udevice).requiredRole : "?";

                if (devSecLevel == SecurityLevel::HIGH) {
                    score += 40;
                    scoreItems.push_back({"Unauthorized access to HIGH-security zone: " + udevice, 40});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | HIGH-SEC ZONE";
                } else if (devSecLevel == SecurityLevel::MEDIUM) {
                    score += 25;
                    scoreItems.push_back({"Unauthorized access to MEDIUM-security zone: " + udevice, 25});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | MEDIUM-SEC ZONE";
                } else {
                    score += 10;
                    scoreItems.push_back({"Unauthorized access to LOW-security zone: " + udevice, 10});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | LOW-SEC ZONE";
                }
            }

            visitedPath.push_back(udevice); prevDevice = udevice;
        }

        if (visitedPath.size() >= 2) {
            vector<string> bfsPath = bfs.findPath(graph, visitedPath.front(), visitedPath.back());
            int depth = bfsPath.empty() ? -1 : (int)bfsPath.size()-1;
            bool elevated = (role=="SENIOR"||role=="ADMIN");
            int threshold = elevated ? 3 : 1;
            if (depth > threshold) {
                score += 5;
                scoreItems.push_back({"BFS depth "+to_string(depth)+" exceeds threshold "+to_string(threshold), 5});
            }
        }

        string trieMatch = trie.match(visitedPath);
        if (!trieMatch.empty()) {
            int unauthorizedCount = 0;
            for (size_t i = 0; i < visitedPath.size(); ++i)
                if (!perms.isAuthorized(uuser, visitedPath[i])) unauthorizedCount++;
            bool elevated = (role == "ADMIN" || role == "SENIOR");
            int aptScore; string aptContext;
            if (unauthorizedCount > 0) {
                aptScore = 30; aptContext = "UNAUTHORIZED APT path: " + trieMatch;
            } else if (!elevated) {
                aptScore = 15; aptContext = "Unusual APT path for role: " + trieMatch;
            } else {
                aptScore = 5;  aptContext = "APT path accessed by admin: " + trieMatch;
            }
            score += aptScore; scoreItems.push_back({aptContext, aptScore});
        }

        int burst = segTree.offHoursBurst();
        if (burst >= 2) {
            score += 20;
            scoreItems.push_back({"Off-hours burst ("+to_string(burst)+" events 23:00-04:00)", 20});
        }

        string verdict = score>=30 ? "*** CRITICAL THREAT ***" : score>=10 ? "SUSPICIOUS" : "CLEAR";

        aulog << "\nSESSION: " << sid << " | User: " << uuser << " | Role: " << role
              << " | Score: " << score << " | " << verdict << " | " << currentTimestamp() << "\n";

        AlertRecord rec;
        rec.user=uuser; rec.role=role; rec.score=score;
        rec.scoreItems=scoreItems; rec.path=visitedPath;
        alerts.push(rec);
    }
};

// ─────────────────────────────────────────────────────────────
// CONFIG LOADER / SAVER
// ─────────────────────────────────────────────────────────────
void loadConfig(const string& filename, NetworkGraph& graph,
                PermissionStore& perms, TrieEngine& trie, ZoneStore& zs) {
    ifstream f(filename);
    if (!f) { cout << " [CONFIG] File '"+filename+"' not found -- skipping.\n"; return; }
    int loaded=0, errors=0; string line;
    while (getline(f, line)) {
        size_t start = line.find_first_not_of(" \t\r\n");
        if (start==string::npos||line[start]=='#') continue;
        line = line.substr(start);
        istringstream ss(line); string cmd; ss >> cmd; cmd = toUpper(cmd);
        if (cmd=="ZONE") {
            string name, lvl; ss >> name >> lvl;
            SecurityLevel sl = parseSecurityLevel(lvl);
            if (sl==SecurityLevel::UNKNOWN_SL){errors++;continue;}
            zs.addZone(name,sl); loaded++;
        } else if (cmd=="NODE") {
            string id,desc,zone,req; ss >> id;
            char c; ss >> c;
            if (c=='"') getline(ss,desc,'"'); else { desc=string(1,c); string r; ss>>r; desc+=r; }
            ss >> zone >> req;
            if (id.empty()||zone.empty()){errors++;continue;}
            graph.addNode(id,desc,zone,req); loaded++;
        } else if (cmd=="EDGE") {
            string from,to; ss >> from >> to;
            if (from.empty()||to.empty()){errors++;continue;}
            graph.addEdge(from,to); loaded++;
        } else if (cmd=="USER") {
            string user,role,machine; ss >> user >> role >> machine;
            vector<string> permitted; string p;
            while (ss >> p) permitted.push_back(p);
            perms.addUser(user,role,machine,permitted); loaded++;
        } else if (cmd=="APT") {
            string sigName; char c; ss >> c;
            if (c=='"') getline(ss,sigName,'"'); else { sigName=string(1,c); string r; ss>>r; sigName+=r; }
            vector<string> path; string p;
            while (ss >> p) path.push_back(p);
            if (!path.empty()){trie.insert(path,sigName);loaded++;} else errors++;
        } else { errors++; }
    }
    cout << " [CONFIG] Loaded " << loaded << " entries from '" << filename << "'";
    if (errors) cout << " (" << errors << " errors)";
    cout << "\n";
}

void saveConfig(const string& filename, const NetworkGraph& graph,
                const PermissionStore& perms, const ZoneStore& zs) {
    ofstream f(filename);
    if (!f) { cout << " [ERROR] Cannot write '"+filename+"'\n"; return; }
    f << "# SecureBank APT Engine -- saved config\n# " << currentTimestamp() << "\n\n";
    f << "# ZONES\n";
    for (auto it=zs.zones.begin();it!=zs.zones.end();++it)
        f << "ZONE " << it->second.name << " " << slToString(it->second.level) << "\n";
    f << "\n# NODES\n";
    for (auto it=graph.nodes.begin();it!=graph.nodes.end();++it)
        f << "NODE " << it->first << " \"" << it->second.description << "\" "
          << it->second.zone << " " << it->second.requiredRole << "\n";
    f << "\n# EDGES\n";
    for (auto it=graph.adjList.begin();it!=graph.adjList.end();++it)
        for (size_t i=0;i<it->second.size();++i)
            f << "EDGE " << it->first << " " << it->second[i] << "\n";
    f << "\n# USERS\n";
    for (auto it=perms.userRoles.begin();it!=perms.userRoles.end();++it) {
        const string& u = it->first;
        f << "USER " << u << " " << it->second << " "
          << (perms.userMachines.count(u)?perms.userMachines.at(u):"-");
        auto pit = perms.userPermissions.find(u);
        if (pit!=perms.userPermissions.end())
            for (size_t i=0;i<pit->second.size();++i) f << " " << pit->second[i];
        f << "\n";
    }
    cout << " [CONFIG] Saved to '" << filename << "'\n";
}