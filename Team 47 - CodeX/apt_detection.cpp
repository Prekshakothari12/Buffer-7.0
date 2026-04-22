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
// SAFE INTEGER INPUT
// ─────────────────────────────────────────────────────────────
int readIntRequired(const string& prompt) {
    int v;
    while (true) {
        cout << prompt;
        if (cin >> v) return v;
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cout << " [ERROR] Invalid input. Please enter a number.\n";
    }
}

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

void hr(char c = '-', int len = 70) { cout << string(len, c) << "\n"; }

string col(const string& s, int w) {
    if ((int)s.size() >= w) return s.substr(0, w);
    return s + string(w - s.size(), ' ');
}

string colR(const string& s, int w) {
    if ((int)s.size() >= w) return s.substr(0, w);
    return string(w - s.size(), ' ') + s;
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
        cout << "  " << col("Zone Name",22) << col("Security Level",16) << "\n";
        cout << "  " << string(38, '-') << "\n";
        for (auto it = zones.begin(); it != zones.end(); ++it)
            cout << "  " << col(it->second.name,22)
                 << col(slToString(it->second.level),16) << "\n";
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
    // Remove all incoming edges pointing TO this node
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
        cout << "  " << col("Node ID",20) << col("Zone",18)
             << col("Security",10) << col("Required Role",16) << "\n";
        cout << "  " << string(66, '-') << "\n";
        for (auto it = nodes.begin(); it != nodes.end(); ++it) {
            SecurityLevel sl = zs.getLevel(it->second.zone);
            cout << "  " << col(it->first,20) << col(it->second.zone,18)
                 << col(slToString(sl),10) << col(it->second.requiredRole,16) << "\n";
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
        cout << "  " << col("Username",18) << col("Role",16)
             << col("Machine",20) << "Allowed Devices\n";
        cout << "  " << string(74, '-') << "\n";
        for (auto it = userRoles.begin(); it != userRoles.end(); ++it) {
            const string& user = it->first;
            cout << "  " << col(user,18) << col(it->second,16)
                 << col(userMachines.count(user) ? userMachines.at(user) : "-", 20);
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
    void log(const string& s) { cout << s << "\n"; alog << s << "\n"; }
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

        cout << "\n"; hr('=', 70);
        cout << " SESSION ANALYSIS\n"; hr('=', 70);
        cout << " Session ID  : " << sid << "\n";
        cout << " User        : " << uuser << "\n";
        cout << " Role        : " << role << "\n";
        cout << " Machine     : " << perms.getMachine(uuser) << "\n";
        cout << " Analysed at : " << currentTimestamp() << "\n";
        hr('-', 70);

        int score = 0;
        vector<ScoreItem> scoreItems;
        vector<string>    visitedPath;
        SegmentTree       segTree;
        string            prevDevice;

        // CHANGE: track scored dates to avoid double-counting weekend+holiday on same day
        set<string> scoredDates;

        cout << "\n EVENT LOG\n"; hr('-', 70);
        cout << " " << col("#",3) << col("Date",12) << col("Time",7)
             << col("Device",22) << col("Day",11) << "Status\n";
        hr('-', 70);

        for (size_t ei = 0; ei < events.size(); ++ei) {
            const SessionEvent& ev = events[ei];
            string udevice = toUpper(ev.device);
            segTree.addEvent(ev.hour);
            ostringstream ts;
            ts << setfill('0') << setw(2) << ev.hour << ":" << setw(2) << ev.minute;
            int wd = weekdayOf(ev.date);
            bool isWE = isWeekend(ev.date), isHoliday = isBankHoliday(ev.date);
            string dayName = weekdayName(wd);

            // CHANGE: score each date only once, and if both weekend and holiday fall
            // on the same date add only one score (the higher of the two, which is equal
            // here, so just add once).
            if (scoredDates.find(ev.date) == scoredDates.end()) {
                if (isWE && isHoliday) {
                    // Same day is both a weekend and a bank holiday -- score only once
                    score += HOLIDAY_SCORE;   // WEEKEND_SCORE == HOLIDAY_SCORE == 10
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
                cout << " " << col(to_string(ei+1),3) << col(ev.date,12)
                     << col(ts.str(),7) << col(udevice,22) << col(dayName,11)
                     << "UNKNOWN DEVICE\n";
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
            // CHANGE: get the security level of this device's zone
            SecurityLevel devSecLevel = SecurityLevel::UNKNOWN_SL;
            if (graph.nodes.count(udevice))
                devSecLevel = zones.getLevel(graph.nodes.at(udevice).zone);

            string authStatus;
            if (auth) {
                // Authorized user -- no score for zone, just report it
                authStatus = "AUTHORIZED";
                if (devSecLevel == SecurityLevel::HIGH)
                    authStatus += " | HIGH-SEC ZONE";
            } else {
                // CHANGE: unauthorized access -- combined score based on zone security level
                string req = graph.nodes.count(udevice) ?
                             graph.nodes.at(udevice).requiredRole : "?";

                if (devSecLevel == SecurityLevel::HIGH) {
                    // Unauthorized + High security zone: score 40
                    score += 40;
                    scoreItems.push_back({"Unauthorized access to HIGH-security zone: " + udevice, 40});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | HIGH-SEC ZONE";
                } else if (devSecLevel == SecurityLevel::MEDIUM) {
                    // Unauthorized + Medium security zone: score 25
                    score += 25;
                    scoreItems.push_back({"Unauthorized access to MEDIUM-security zone: " + udevice, 25});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | MEDIUM-SEC ZONE";
                } else {
                    // Unauthorized + Low security zone (or unknown): score 10
                    score += 10;
                    scoreItems.push_back({"Unauthorized access to LOW-security zone: " + udevice, 10});
                    authStatus = "UNAUTHORIZED (needs " + req + ") | LOW-SEC ZONE";
                }
            }

            cout << " " << col(to_string(ei+1),3) << col(ev.date,12)
                 << col(ts.str(),7) << col(udevice,22) << col(dayName,11)
                 << authStatus << edgeStatus << "\n";
            visitedPath.push_back(udevice); prevDevice = udevice;
        }
        hr('-', 70);

        cout << "\n TRAVERSAL ANALYSIS\n"; hr('-', 70);
        if (visitedPath.size() >= 2) {
            vector<string> bfsPath = bfs.findPath(graph, visitedPath.front(), visitedPath.back());
            int depth = bfsPath.empty() ? -1 : (int)bfsPath.size()-1;
            bool elevated = (role=="SENIOR"||role=="ADMIN");
            int threshold = elevated ? 3 : 1;
            string pathStr;
            for (int i = 0; i < (int)bfsPath.size(); ++i) { if (i) pathStr+=" --> "; pathStr+=bfsPath[i]; }
            if (bfsPath.empty()) pathStr = "(unreachable)";
            cout << " BFS shortest path : " << pathStr << "\n";
            cout << " Depth             : " << depth << "  (allowed: " << threshold << " for " << role << ")\n";
            if (depth > threshold) {
                cout << " Result            : EXCEEDED -- lateral movement suspected\n";
                score += 5;
                scoreItems.push_back({"BFS depth "+to_string(depth)+" exceeds threshold "+to_string(threshold), 5});
            } else { cout << " Result            : OK\n"; }
        } else { cout << " (single-device session -- BFS skipped)\n"; }

        cout << "\n THREAT SIGNATURE CHECK\n"; hr('-', 70);
        string trieMatch = trie.match(visitedPath);
        if (trieMatch.empty()) { cout << " Trie match : No known APT signature matched\n"; }
        else {
            cout << " Trie match : MATCHED -- " << trieMatch << "\n";
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

        cout << "\n TEMPORAL ANALYSIS\n"; hr('-', 70);
        int burst = segTree.offHoursBurst();
        if (burst >= 2) {
            cout << " Off-hours events  : " << burst << "  (23:00 - 04:00)  -- SUSPICIOUS BURST\n";
            score += 20;
            scoreItems.push_back({"Off-hours burst ("+to_string(burst)+" events 23:00-04:00)", 20});
        } else { cout << " Off-hours events  : " << burst << "  (threshold: 2)  -- Normal\n"; }
        // Print weekend/holiday flags based on scoredDates
        for (auto it = scoredDates.begin(); it != scoredDates.end(); ++it) {
            bool isWE = isWeekend(*it), isHol = isBankHoliday(*it);
            int wd = weekdayOf(*it);
            if (isWE && isHol)
                cout << " Weekend+Holiday   : " << weekdayName(wd) << " " << *it << " -- scored once\n";
            else if (isWE)
                cout << " Weekend flag      : " << weekdayName(wd) << " " << *it << " -- activity on non-working day\n";
            else if (isHol)
                cout << " Bank holiday flag : " << *it << " -- activity on public holiday\n";
        }

        cout << "\n RISK SCORE BREAKDOWN\n"; hr('-', 70);
        cout << " " << col("Flag / Reason",50) << colR("Score",7) << "\n"; hr('-', 70);
        for (size_t i = 0; i < scoreItems.size(); ++i)
            cout << " " << col(scoreItems[i].reason,50)
                 << colR("+"+to_string(scoreItems[i].points),7) << "\n";
        hr('-', 70);
        cout << " " << col("TOTAL RISK SCORE",50) << colR(to_string(score),7) << "\n";
        hr('-', 70);

        string verdict = score>=30 ? "*** CRITICAL THREAT ***" : score>=10 ? "SUSPICIOUS" : "CLEAR";
        cout << "\n VERDICT: " << verdict << "\n"; hr('=', 70);

        aulog << "\nSESSION: " << sid << " | User: " << uuser << " | Role: " << role
              << " | Score: " << score << " | " << verdict << " | " << currentTimestamp() << "\n";

        AlertRecord rec;
        rec.user=uuser; rec.role=role; rec.score=score;
        rec.scoreItems=scoreItems; rec.path=visitedPath;
        alerts.push(rec);

    }
};

// ─────────────────────────────────────────────────────────────
// THREAT REPORT
// ─────────────────────────────────────────────────────────────
void printReport(AlertEngine& alerts, ofstream& analysisLog) {
    vector<AlertRecord> sorted = alerts.getSorted();
    if (sorted.empty()) { cout << "\n [INFO] No sessions analysed yet.\n"; return; }
    auto out = [&](const string& s) { cout << s << "\n"; analysisLog << s << "\n"; };
    out(""); out(string(70,'=')); out(" SECUREBANK THREAT INTELLIGENCE REPORT");
    out(" Generated : "+currentTimestamp()); out(string(70,'='));
    for (size_t i = 0; i < sorted.size(); ++i) {
        const AlertRecord& rec = sorted[i];
        string verdict = rec.score>=30?"*** CRITICAL THREAT ***":rec.score>=10?"SUSPICIOUS":"CLEAR";
        out(""); out(" User: "+rec.user+"   Role: "+rec.role+"   Verdict: "+verdict);
        if (!rec.path.empty()) {
            string ps;
            for (int j = 0; j < (int)rec.path.size(); ++j) { if (j) ps+=" --> "; ps+=rec.path[j]; }
            out(" Path  : "+ps);
        }
        out(""); out(" "+col("Flag / Reason",50)+colR("Score",7)); out(" "+string(57,'-'));
        for (size_t j = 0; j < rec.scoreItems.size(); ++j)
            out(" "+col(rec.scoreItems[j].reason,50)+colR("+"+to_string(rec.scoreItems[j].points),7));
        out(" "+string(57,'-')); out(" "+col("TOTAL",50)+colR(to_string(rec.score),7));
    }
    out(""); out(string(70,'-')); out(" SUMMARY"); out(string(70,'-'));
    out(" "+col("User",18)+col("Role",16)+colR("Score",7)+"   Status");
    out(" "+string(65,'-'));
    for (size_t i = 0; i < sorted.size(); ++i) {
        const AlertRecord& r = sorted[i];
        string status = r.score>=30?"CRITICAL THREAT":r.score>=10?"SUSPICIOUS":"CLEAR";
        out(" "+col(r.user,18)+col(r.role,16)+colR(to_string(r.score),7)+"   "+status);
    }
    out(string(70,'-')); out("");
}

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

// ─────────────────────────────────────────────────────────────
// HELPERS: list users / devices
// ─────────────────────────────────────────────────────────────
void listAvailableUsers(const PermissionStore& perms) {
    vector<string> users = perms.getAllUsers();
    if (users.empty()) { cout << " [INFO] No users defined yet.\n"; return; }
    cout << "\n Available Users\n";
    cout << " " << col("Username",20) << col("Role",16) << "Machine\n";
    cout << " " << string(54,'-') << "\n";
    for (size_t i=0;i<users.size();++i)
        cout << " " << col(users[i],20) << col(perms.getRole(users[i]),16)
             << perms.getMachine(users[i]) << "\n";
    cout << "\n";
}

void listAvailableDevices(const NetworkGraph& graph, const ZoneStore& zs) {
    if (graph.nodes.empty()) { cout << " [INFO] No devices defined yet.\n"; return; }
    cout << "\n Available Devices\n";
    cout << " " << col("Node ID",22) << col("Zone",18) << col("Security",10) << "Required Role\n";
    cout << " " << string(66,'-') << "\n";
    for (auto it=graph.nodes.begin();it!=graph.nodes.end();++it) {
        SecurityLevel sl = zs.getLevel(it->second.zone);
        cout << " " << col(it->first,22) << col(it->second.zone,18)
             << col(slToString(sl),10) << it->second.requiredRole << "\n";
    }
    cout << "\n";
}

// ─────────────────────────────────────────────────────────────
// SETUP / ADMIN MENU
// ─────────────────────────────────────────────────────────────
void setupMode(NetworkGraph& graph, PermissionStore& perms,
               ZoneStore& zs, TrieEngine& trie, ofstream& analysisLog) {
    int opt;
    do {
        cout << "\n"; hr('=', 50);
        cout << " SETUP / ADMIN MENU\n"; hr('=', 50);
        cout << " 1. Add zone(s)\n 2. Add node(s)\n 3. Add edge(s)\n";
        cout << " 4. Add user(s)\n 5. Add APT signature(s)\n";
        cout << " 6. View current configuration\n 7. Load config from file\n";
        cout << " 8. Save config to file\n 9. Back to main menu\n";
        hr('-', 50);
        opt = readIntRequired(" Choice: ");
        cout << "\n";

        if (opt == 1) {
            int numZones = readIntRequired(" How many zones to add? ");
            if (numZones <= 0) { cout << " [ERROR] Must be at least 1.\n"; }
            else {
                for (int z = 0; z < numZones; z++) {
                    cout << "\n Zone " << z+1 << " of " << numZones << "\n";
                    string name, lvlStr;
                    cout << "   Zone name : "; cin >> name; name = toUpper(name);
                    SecurityLevel sl = SecurityLevel::UNKNOWN_SL;
                    while (sl == SecurityLevel::UNKNOWN_SL) {
                        cout << "   Security level (LOW / MEDIUM / HIGH) : "; cin >> lvlStr;
                        sl = parseSecurityLevel(lvlStr);
                        if (sl == SecurityLevel::UNKNOWN_SL)
                            cout << "   [ERROR] Invalid value. Please enter LOW, MEDIUM, or HIGH.\n";
                    }
                    zs.addZone(name, sl);
                    cout << "   [OK] Zone '" << name << "' added (" << slToString(sl) << ").\n";
                    analysisLog << "[SETUP] Zone: " << name << " " << slToString(sl) << "\n";
                }
            }

        } else if (opt == 2) {
            int numNodes = readIntRequired(" How many nodes to add? ");
            if (numNodes <= 0) { cout << " [ERROR] Must be at least 1.\n"; }
            else {
                for (int n = 0; n < numNodes; n++) {
                    cout << "\n Node " << n+1 << " of " << numNodes << "\n";
                    string id, req, zone;
                    cout << "   Node ID       : "; cin >> id; id = toUpper(id);
                    if (graph.nodeExists(id))
                        cout << "   [WARN] Node '" << id << "' already exists -- will overwrite.\n";
                    cout << "   Required role : "; cin >> req; req = toUpper(req);
                    if (zs.zones.empty()) { cout << "   [WARN] No zones defined yet.\n"; }
                    else { cout << "   Available zones:\n"; zs.listZones(); }
                    bool validZone = false;
                    while (!validZone) {
                        cout << "   Zone : "; cin >> zone; zone = toUpper(zone);
                        if (zs.zoneExists(zone)) validZone = true;
                        else cout << "   [ERROR] Zone '" << zone << "' does not exist.\n";
                    }
                    graph.addNode(id, id, zone, req);
                    cout << "   [OK] Node '" << id << "' added.\n";
                    analysisLog << "[SETUP] Node: " << id << " zone=" << zone << " role=" << req << "\n";
                }
            }

        } else if (opt == 3) {
            if (graph.nodes.empty()) { cout << " [ERROR] No nodes defined yet. Add nodes first.\n"; }
            else {
                int numEdges = readIntRequired(" How many edges to add? ");
                if (numEdges <= 0) { cout << " [ERROR] Must be at least 1.\n"; }
                else {
                    listAvailableDevices(graph, zs);
                    for (int e = 0; e < numEdges; e++) {
                        cout << "\n Edge " << e+1 << " of " << numEdges << "\n";
                        string from, to;
                        cout << "   Edge FROM (node ID) : "; cin >> from; from = toUpper(from);
                        cout << "   Edge TO   (node ID) : "; cin >> to;   to   = toUpper(to);
                        if (!graph.nodeExists(from))
                            cout << "   [ERROR] Node '" << from << "' does not exist. Skipping.\n";
                        else if (!graph.nodeExists(to))
                            cout << "   [ERROR] Node '" << to << "' does not exist. Skipping.\n";
                        else if (graph.edgeExists(from, to))
                            cout << "   [INFO] Edge already exists. Skipping.\n";
                        else {
                            graph.addEdge(from, to);
                            cout << "   [OK] Edge " << from << " --> " << to << " added.\n";
                            analysisLog << "[SETUP] Edge: " << from << " --> " << to << "\n";
                        }
                    }
                }
            }

        } else if (opt == 4) {
            if (graph.nodes.empty()) { cout << " [ERROR] No nodes defined yet. Add nodes first.\n"; }
            else {
                int numUsers = readIntRequired(" How many users to add? ");
                if (numUsers <= 0) { cout << " [ERROR] Must be at least 1.\n"; }
                else {
                    for (int u = 0; u < numUsers; u++) {
                        cout << "\n User " << u+1 << " of " << numUsers << "\n";
                        string username, machine, role;
                        cout << "   Username : "; cin >> username; username = toUpper(username);
                        if (perms.userExists(username))
                            cout << "   [WARN] User '" << username << "' already exists -- will overwrite.\n";
                        listAvailableDevices(graph, zs);
                        bool validMachine = false;
                        while (!validMachine) {
                            cout << "   Assigned machine/node : "; cin >> machine; machine = toUpper(machine);
                            if (graph.nodeExists(machine)) validMachine = true;
                            else cout << "   [ERROR] Node '" << machine << "' does not exist.\n";
                        }
                        cout << "   Role (TELLER/OPS/LOAN/SENIOR/ADMIN or custom) : "; cin >> role; role = toUpper(role);
                        int np = readIntRequired("   How many devices to allow access to? ");
                        if (np < 0) np = 0;
                        vector<string> permitted;
                        for (int i = 0; i < np; i++) {
                            string node; bool valid = false;
                            while (!valid) {
                                cout << "     Device " << i+1 << " : "; cin >> node; node = toUpper(node);
                                if (graph.nodeExists(node)) valid = true;
                                else cout << "     [ERROR] Node '" << node << "' does not exist.\n";
                            }
                            permitted.push_back(node);
                        }
                        perms.addUser(username, role, machine, permitted);
                        cout << "   [OK] User '" << username << "' (" << role << ") added with "
                             << permitted.size() << " permission(s).\n";
                        analysisLog << "[SETUP] User: " << username << " role=" << role << "\n";
                    }
                }
            }

        } else if (opt == 5) {
            int numSigs = readIntRequired(" How many APT signatures to add? ");
            if (numSigs <= 0) { cout << " [ERROR] Must be at least 1.\n"; }
            else {
                for (int s = 0; s < numSigs; s++) {
                    cout << "\n Signature " << s+1 << " of " << numSigs << "\n";
                    int pathLen = readIntRequired("   Number of nodes in APT path : ");
                    if (pathLen <= 0) { cout << "   [ERROR] Path must have at least 1 node. Skipping.\n"; }
                    else {
                        vector<string> path;
                        for (int i = 0; i < pathLen; i++) {
                            string node; cout << "     Step " << i+1 << " node ID : "; cin >> node;
                            path.push_back(toUpper(node));
                        }
                        string sigName;
                        cout << "   Signature name : "; cin.ignore(); getline(cin, sigName);
                        trie.insert(path, sigName);
                        cout << "   [OK] Signature '" << sigName << "' added. Total: " << trie.count() << "\n";
                        analysisLog << "[SETUP] APT: " << sigName << "\n";
                    }
                }
            }

        } else if (opt == 6) {
            cout << " ZONES\n"; hr('-', 50); zs.listZones();
            cout << "\n NODES\n"; hr('-', 50); graph.listNodes(zs);
            cout << "\n EDGES\n"; hr('-', 50); graph.listEdges();
            cout << "\n USERS\n"; hr('-', 50); perms.listUsers();
            cout << "\n APT SIGNATURES : " << trie.count() << " loaded\n";

        } else if (opt == 7) {
            string fname; cout << " Config filename : "; cin >> fname;
            loadConfig(fname, graph, perms, trie, zs);

        } else if (opt == 8) {
            string fname; cout << " Save to filename : "; cin >> fname;
            saveConfig(fname, graph, perms, zs);

        } else if (opt != 9) {
            cout << " [ERROR] Invalid choice. Enter 1-9.\n";
        }
    } while (opt != 9);
}

// ─────────────────────────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────────────────────────
int main(int argc, char* argv[]) {
    ofstream analysisLog("securebank_apt.log");
    ofstream auditLog("securebank_audit.log");
    auditLog << string(70,'=') << "\nSECUREBANK LTD.  --  ACCESS AUDIT LOG\nGenerated : "
             << currentTimestamp() << "\n" << string(70,'=') << "\n";

    cout << "\n"; hr('=', 70);
    cout << " SecureBank APT Detection Engine  v4.0\n";
    cout << " Graph . Hash Table . BFS . Trie . Segment Tree . Priority Queue\n";
    hr('=', 70); cout << "\n";

    NetworkGraph graph; PermissionStore perms;
    ZoneStore zones; TrieEngine trie; AlertEngine alerts;
    DetectionEngine engine(graph, perms, zones, trie, alerts, analysisLog, auditLog);

    string defaultConfig = "config.txt";
    if (argc >= 2) loadConfig(argv[1], graph, perms, trie, zones);
    else           loadConfig(defaultConfig, graph, perms, trie, zones);

    int choice;
    do {
        cout << "\n"; hr('=', 50);
        cout << " MAIN MENU\n"; hr('=', 50);
        cout << " 1. Analyse a user session\n 2. View Threat Report\n";
        cout << " 3. Setup / Admin\n 4. List current users\n";
        cout << " 5. List current network devices\n 6. Exit\n";
        hr('-', 50);
        choice = readIntRequired(" Choice: ");

        if (choice == 1) {
            if (perms.getAllUsers().empty()) {
                cout << "\n [ERROR] No users defined. Go to Setup (option 3) first.\n"; continue;
            }
            if (graph.nodes.empty()) {
                cout << "\n [ERROR] No network nodes defined. Go to Setup (option 3) first.\n"; continue;
            }
            listAvailableUsers(perms);
            string username; cout << " Enter username : "; cin >> username;
            username = toUpper(username);
            if (!perms.userExists(username)) {
                cout << " [ERROR] User '" << username << "' not found.\n"; continue;
            }
            int n = readIntRequired(" Number of device access events : ");
            if (n <= 0) { cout << " [ERROR] Must be at least 1.\n"; continue; }
            listAvailableDevices(graph, zones);
            cout << " (Enter a device ID not listed above to simulate an unknown access.)\n\n";
            vector<SessionEvent> events;
            for (int i = 0; i < n; i++) {
                SessionEvent ev;
                cout << " Event " << i+1 << "\n";
                bool validDate = false;
                while (!validDate) {
                    cout << "   Date   (YYYY-MM-DD) : "; cin >> ev.date;
                    struct tm tmp;
                    if (ev.date.size()==10 && parseDate(ev.date,tmp)) validDate = true;
                    else cout << "   [ERROR] Invalid date format. Use YYYY-MM-DD.\n";
                }
                ev.hour   = readIntRequired("   Hour   (0-23)      : ");
                ev.minute = readIntRequired("   Minute (0-59)      : ");
                if (ev.hour   < 0 || ev.hour   > 23) { cout<<"   [WARN] Hour clamped.\n";   ev.hour  =max(0,min(23,ev.hour));   }
                if (ev.minute < 0 || ev.minute > 59) { cout<<"   [WARN] Minute clamped.\n"; ev.minute=max(0,min(59,ev.minute)); }
                cout << "   Device ID          : "; cin >> ev.device; ev.device = toUpper(ev.device);
                events.push_back(ev); cout << "\n";
            }
            engine.analyseSession(username, events);

        } else if (choice == 2) { printReport(alerts, analysisLog);
        } else if (choice == 3) { setupMode(graph, perms, zones, trie, analysisLog);
        } else if (choice == 4) { listAvailableUsers(perms);
        } else if (choice == 5) {
            listAvailableDevices(graph, zones);
            cout << " EDGES\n"; hr('-', 50); graph.listEdges();
        } else if (choice != 6) {
            cout << " [ERROR] Invalid choice. Enter 1-6.\n";
        }
    } while (choice != 6);

    cout << "\n Analysis log : securebank_apt.log\n Audit log    : securebank_audit.log\n\n";
    analysisLog.close(); auditLog.close();
    return 0;
}