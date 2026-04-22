/*
 * SecureBank APT Detection Engine — pybind11 Bindings
 * File   : bindings.cpp
 * Author : Generated for SecureBank APT Engine v4.0
 *
 * ─── COMPILE ────────────────────────────────────────────────────────────────
 *
 *  Linux / macOS:
 *    c++ -O3 -Wall -shared -std=c++14 -fPIC \
 *        $(python3 -m pybind11 --includes) \
 *        bindings.cpp -o apt_engine$(python3-config --extension-suffix)
 *
 *  Windows (MSVC):
 *    cl /O2 /std:c++14 /EHsc /LD \
 *       /I%PYTHON_INCLUDE% /I%PYBIND11_INCLUDE% \
 *       bindings.cpp /link /OUT:apt_engine.pyd
 *
 *  Prerequisites:
 *    pip install pybind11
 *    Both bindings.cpp and apt_interactive.cpp must be in the same directory.
 *    apt_interactive.cpp is compiled ONLY via this file (via #include);
 *    do NOT compile apt_interactive.cpp separately when building the .so.
 *
 * ─── USAGE ──────────────────────────────────────────────────────────────────
 *
 *  import apt_engine
 *  engine = apt_engine.APTEngine()
 *  engine.loadConfig("config.txt")
 *  users  = engine.getUsers()
 *  result = engine.analyzeSession("RAJAN", [
 *      {"device": "WS-OPS-02",    "date": "2025-04-16", "hour": 22, "minute": 10},
 *      {"device": "INTRA-SRV-01", "date": "2025-04-16", "hour": 22, "minute": 47},
 *      {"device": "AUDIT-SRV-01", "date": "2025-04-17", "hour":  0, "minute": 15},
 *      {"device": "VAULT-DB-01",  "date": "2025-04-17", "hour":  1, "minute": 50},
 *  ])
 *  print(result)
 * ────────────────────────────────────────────────────────────────────────────
 */

// ── 1.  Pull in the original engine WITHOUT compiling its main() ─────────────
// We define APT_BINDINGS_BUILD so that apt_interactive.cpp can optionally
// guard its main() with  #ifndef APT_BINDINGS_BUILD … #endif.
// Even without that guard this file works because we never call main().
#define APT_BINDINGS_BUILD
#include "apt_detection.cpp"          // brings in all classes & helpers

// ── 2.  pybind11 ─────────────────────────────────────────────────────────────
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>               // automatic vector/map conversions
namespace py = pybind11;

// ── 3.  RAII output-capture helper ───────────────────────────────────────────
//
//  Usage:
//    {
//        OutputCapture cap;
//        someFunction();               // writes to std::cout
//        std::string text = cap.get(); // everything that was printed
//    }                                 // std::cout restored automatically
//
class OutputCapture {
public:
    OutputCapture()
        : old_(std::cout.rdbuf(buf_.rdbuf())) {}

    ~OutputCapture() {
        std::cout.rdbuf(old_);          // always restore, even on exception
    }

    std::string get() const { return buf_.str(); }

private:
    std::ostringstream buf_;
    std::streambuf*    old_;
};

// ── 4.  Data-conversion helpers ───────────────────────────────────────────────

// Python dict  →  C++ SessionEvent
static SessionEvent dictToSessionEvent(const py::dict& d) {
    SessionEvent ev;
    ev.device = d["device"].cast<std::string>();
    ev.date   = d["date"].cast<std::string>();
    // Accept hour/minute as int or string
    if (py::isinstance<py::int_>(d["hour"]))
        ev.hour = d["hour"].cast<int>();
    else
        ev.hour = std::stoi(d["hour"].cast<std::string>());
    if (py::isinstance<py::int_>(d["minute"]))
        ev.minute = d["minute"].cast<int>();
    else
        ev.minute = std::stoi(d["minute"].cast<std::string>());
    // Clamp to valid range
    ev.hour   = std::max(0, std::min(23, ev.hour));
    ev.minute = std::max(0, std::min(59, ev.minute));
    return ev;
}

// Python list of dicts  →  vector<SessionEvent>
static std::vector<SessionEvent> eventsFromList(const py::list& lst) {
    std::vector<SessionEvent> out;
    out.reserve(py::len(lst));
    for (auto item : lst)
        out.push_back(dictToSessionEvent(item.cast<py::dict>()));
    return out;
}

// C++ ScoreItem  →  Python dict
static py::dict scoreItemToDict(const ScoreItem& si) {
    py::dict d;
    d["reason"] = si.reason;
    d["points"] = si.points;
    return d;
}

// C++ AlertRecord  →  Python dict
static py::dict alertRecordToDict(const AlertRecord& rec) {
    py::dict d;
    d["user"]  = rec.user;
    d["role"]  = rec.role;
    d["score"] = rec.score;
    d["verdict"] = rec.score >= 30 ? "CRITICAL THREAT"
                 : rec.score >= 10 ? "SUSPICIOUS"
                                   : "CLEAR";
    // path as list of strings
    py::list path;
    for (const auto& n : rec.path) path.append(n);
    d["path"] = path;
    // score breakdown as list of dicts
    py::list items;
    for (const auto& si : rec.scoreItems) items.append(scoreItemToDict(si));
    d["score_items"] = items;
    return d;
}

// ── 5.  Wrapper class ─────────────────────────────────────────────────────────
class APTEngineWrapper {
public:
    APTEngineWrapper()
        : analysisLog_("securebank_apt.log",   std::ios::app)
        , auditLog_   ("securebank_audit.log",  std::ios::app)
        , engine_(graph_, perms_, zones_, trie_, alerts_,
                  analysisLog_, auditLog_)
    {
        auditLog_ << std::string(70, '=')
                  << "\nSECUREBANK LTD.  --  ACCESS AUDIT LOG\nGenerated : "
                  << currentTimestamp()
                  << "\n" << std::string(70, '=') << "\n";
    }

    ~APTEngineWrapper() {
        if (analysisLog_.is_open()) analysisLog_.close();
        if (auditLog_.is_open())    auditLog_.close();
    }

    // ── loadConfig ───────────────────────────────────────────────────────────
    bool loadConfig(const std::string& filename) {
        try {
            std::ifstream test(filename);
            bool exists = test.good();
            test.close();
            if (!exists) return false;
            // Suppress "loaded N entries" banner from cout
            OutputCapture cap;
            ::loadConfig(filename, graph_, perms_, trie_, zones_);
            return true;
        } catch (...) { return false; }
    }

    // ── analyzeSession ───────────────────────────────────────────────────────
    std::string analyzeSession(const std::string& user,
                               const py::list&    events)
    {
        try {
            std::string uuser = toUpper(user);
            if (!perms_.userExists(uuser))
                return "[ERROR] User '" + uuser + "' not found. "
                       "Check getUsers() for valid usernames.";

            std::vector<SessionEvent> evVec = eventsFromList(events);
            if (evVec.empty())
                return "[ERROR] No events provided. "
                       "Pass at least one event dictionary.";

            OutputCapture cap;
            engine_.analyseSession(uuser, evVec);
            return cap.get();
        }
        catch (const std::exception& e) {
            return std::string("[EXCEPTION] ") + e.what();
        }
        catch (...) {
            return "[EXCEPTION] Unknown error during session analysis.";
        }
    }

    // ── getUsers ─────────────────────────────────────────────────────────────
    py::list getUsers() {
        py::list result;
        for (const auto& username : perms_.getAllUsers()) {
            py::dict d;
            d["username"] = username;
            d["role"]     = perms_.getRole(username);
            d["machine"]  = perms_.getMachine(username);
            // Permitted devices
            py::list devList;
            auto it = perms_.userPermissions.find(username);
            if (it != perms_.userPermissions.end())
                for (const auto& dev : it->second)
                    devList.append(dev);
            d["permitted_devices"] = devList;
            result.append(d);
        }
        return result;
    }

    // ── getDevices ───────────────────────────────────────────────────────────
    py::list getDevices() {
        py::list result;
        for (const auto& kv : graph_.nodes) {
            py::dict d;
            d["id"]            = kv.first;
            d["description"]   = kv.second.description;
            d["zone"]          = kv.second.zone;
            d["required_role"] = kv.second.requiredRole;
            d["security_level"] =
                slToString(zones_.getLevel(kv.second.zone));
            result.append(d);
        }
        return result;
    }

    // ── getEdges ─────────────────────────────────────────────────────────────
    py::list getEdges() {
        py::list result;
        for (const auto& kv : graph_.adjList)
            for (const auto& dest : kv.second) {
                py::dict d;
                d["from"] = kv.first;
                d["to"]   = dest;
                result.append(d);
            }
        return result;
    }

    // ── getZones ─────────────────────────────────────────────────────────────
    py::list getZones() {
        py::list result;
        for (const auto& kv : zones_.zones) {
            py::dict d;
            d["name"]           = kv.second.name;
            d["security_level"] = slToString(kv.second.level);
            result.append(d);
        }
        return result;
    }

    // ── getThreatReport ──────────────────────────────────────────────────────
    py::list getThreatReport() {
        py::list result;
        for (const auto& rec : alerts_.getSorted())
            result.append(alertRecordToDict(rec));
        return result;
    }

    // ── addZone ──────────────────────────────────────────────────────────────
    bool addZone(const std::string& name, const std::string& level) {
        try {
            SecurityLevel sl = parseSecurityLevel(level);
            if (sl == SecurityLevel::UNKNOWN_SL) return false;
            zones_.addZone(name, sl);
            return true;
        } catch (...) { return false; }
    }

    // ── addNode ──────────────────────────────────────────────────────────────
    bool addNode(const std::string& id,
                 const std::string& zone,
                 const std::string& requiredRole)
    {
        try {
            if (!zones_.zoneExists(zone)) return false;
            graph_.addNode(id, id, zone, requiredRole);
            return true;
        } catch (...) { return false; }
    }

    // ── addEdge ──────────────────────────────────────────────────────────────
    bool addEdge(const std::string& from, const std::string& to) {
        try {
            if (!graph_.nodeExists(from) || !graph_.nodeExists(to))
                return false;
            if (graph_.edgeExists(from, to)) return true; // already exists
            graph_.addEdge(from, to);
            return true;
        } catch (...) { return false; }
    }

    // ── addUser ──────────────────────────────────────────────────────────────
    bool addUser(const std::string&              username,
                 const std::string&              role,
                 const std::string&              machine,
                 const std::vector<std::string>& permittedDevices)
    {
        try {
            if (!graph_.nodeExists(machine)) return false;
            for (const auto& dev : permittedDevices)
                if (!graph_.nodeExists(dev)) return false;
            perms_.addUser(username, role, machine, permittedDevices);
            return true;
        } catch (...) { return false; }
    }

    // ── addAPTSignature ──────────────────────────────────────────────────────
    bool addAPTSignature(const std::vector<std::string>& path,
                         const std::string&              name)
    {
        try {
            if (path.empty()) return false;
            trie_.insert(path, name);
            return true;
        } catch (...) { return false; }
    }

    // ── removeUser ───────────────────────────────────────────────────────────
bool removeUser(const std::string& username) {
    try {
        return perms_.removeUser(username);
    } catch (...) { return false; }
}

// ── removeNode ───────────────────────────────────────────────────────────
bool removeNode(const std::string& id) {
    try {
        return graph_.removeNode(id);
    } catch (...) { return false; }
}

// ── removeEdge ───────────────────────────────────────────────────────────
bool removeEdge(const std::string& from, const std::string& to) {
    try {
        return graph_.removeEdge(from, to);
    } catch (...) { return false; }
}

// ── removeZone ───────────────────────────────────────────────────────────
bool removeZone(const std::string& name) {
    try {
        return zones_.removeZone(name);
    } catch (...) { return false; }
}

    // ── getConfigSummary ─────────────────────────────────────────────────────
    py::dict getConfigSummary() {
        py::dict d;
        d["users"]          = (int)perms_.getAllUsers().size();
        d["devices"]        = (int)graph_.nodes.size();
        d["zones"]          = (int)zones_.zones.size();
        d["apt_signatures"] = trie_.count();
        d["sessions_analysed"] = (int)alerts_.getSorted().size();
        return d;
    }

    // ── getRiskThreshold ─────────────────────────────────────────────────────
    int getRiskThreshold() const { return EMAIL_THRESHOLD; }

    // ── getVersion ───────────────────────────────────────────────────────────
    std::string getVersion() const { return "4.0"; }

    // ── getBuildInfo ─────────────────────────────────────────────────────────
    std::string getBuildInfo() const {
        return std::string("Built: ") + __DATE__ + " " + __TIME__;
    }

    // ── clearAlerts ──────────────────────────────────────────────────────────
    void clearAlerts() {
        // Replace the AlertEngine with a fresh one
        alerts_ = AlertEngine();
    }

    // ── isBankHoliday / isWeekend (convenience) ──────────────────────────────
    bool checkIsBankHoliday(const std::string& dateYYYYMMDD) const {
        return ::isBankHoliday(dateYYYYMMDD);
    }

    bool checkIsWeekend(const std::string& dateYYYYMMDD) const {
        return ::isWeekend(dateYYYYMMDD);
    }

    // ── analyzeMultipleSessions ──────────────────────────────────────────────
    py::list analyzeMultipleSessions(const py::list& sessions) {
        py::list results;
        for (auto item : sessions) {
            py::dict session = item.cast<py::dict>();
            std::string user   = session["user"].cast<std::string>();
            py::list    events = session["events"].cast<py::list>();

            py::dict result;
            result["user"]   = user;
            result["output"] = analyzeSession(user, events);

            // Pull latest score from alert engine
            auto sorted = alerts_.getSorted();
            if (!sorted.empty()) {
                const AlertRecord& latest = sorted.front(); // highest score
                result["score"]   = latest.score;
                result["verdict"] = latest.score >= 30 ? "CRITICAL THREAT"
                                  : latest.score >= 10 ? "SUSPICIOUS"
                                                       : "CLEAR";
            } else {
                result["score"]   = 0;
                result["verdict"] = "CLEAR";
            }
            results.append(result);
        }
        return results;
    }

private:
    // Core engine objects — order matters: logs must outlive engine_
    std::ofstream   analysisLog_;
    std::ofstream   auditLog_;
    NetworkGraph    graph_;
    PermissionStore perms_;
    ZoneStore       zones_;
    TrieEngine      trie_;
    AlertEngine     alerts_;
    DetectionEngine engine_;   // holds refs to the objects above
};

// ── 6.  Module definition ─────────────────────────────────────────────────────
PYBIND11_MODULE(apt_engine, m) {
    m.doc() = "SecureBank APT Detection Engine — High-performance C++ backend";

    py::class_<APTEngineWrapper>(m, "APTEngine")

        // ── lifecycle ──────────────────────────────────────────────────────
        .def(py::init<>(),
             "Create a new APT engine instance. "
             "Log files (securebank_apt.log, securebank_audit.log) "
             "are opened in append mode.")

        // ── config ─────────────────────────────────────────────────────────
        .def("loadConfig",
             &APTEngineWrapper::loadConfig,
             py::arg("filename"),
             "Load zones, nodes, edges, users and APT signatures from a "
             "config file. Returns True on success, False if file not found.")

        .def("addZone",
             &APTEngineWrapper::addZone,
             py::arg("name"), py::arg("level"),
             "Add a security zone. level must be 'LOW', 'MEDIUM', or 'HIGH'. "
             "Returns True on success.")

        .def("addNode",
             &APTEngineWrapper::addNode,
             py::arg("id"), py::arg("zone"), py::arg("required_role"),
             "Add a network node/device. zone must already exist. "
             "Returns True on success.")

        .def("addEdge",
             &APTEngineWrapper::addEdge,
             py::arg("from_node"), py::arg("to_node"),
             "Add a directed edge between two existing nodes. "
             "Returns True on success (or if edge already exists).")

        .def("addUser",
             &APTEngineWrapper::addUser,
             py::arg("username"), py::arg("role"),
             py::arg("machine"), py::arg("permitted_devices"),
             "Add a user. machine and all permitted_devices must be valid "
             "node IDs. Returns True on success.")

        .def("addAPTSignature",
             &APTEngineWrapper::addAPTSignature,
             py::arg("path"), py::arg("name"),
             "Register an APT traversal signature. "
             "path is a list of node IDs in attack order. "
             "Returns True on success.")

        .def("removeUser",
     &APTEngineWrapper::removeUser,
     py::arg("username"),
     "Delete a user by username. Returns True on success.")

.def("removeNode",
     &APTEngineWrapper::removeNode,
     py::arg("id"),
     "Delete a node/device and all its edges. Returns True on success.")

.def("removeEdge",
     &APTEngineWrapper::removeEdge,
     py::arg("from_node"), py::arg("to_node"),
     "Delete a directed edge. Returns True on success.")

.def("removeZone",
     &APTEngineWrapper::removeZone,
     py::arg("name"),
     "Delete a zone by name. Returns True on success.")     

        // ── analysis ───────────────────────────────────────────────────────
        .def("analyzeSession",
             &APTEngineWrapper::analyzeSession,
             py::arg("username"), py::arg("events"),
             "Analyse a user session.\n\n"
             "events: list of dicts, each with keys:\n"
             "  'device' (str), 'date' (YYYY-MM-DD str),\n"
             "  'hour' (int 0-23), 'minute' (int 0-59)\n\n"
             "Returns the full formatted analysis output as a string.")

        .def("analyzeMultipleSessions",
             &APTEngineWrapper::analyzeMultipleSessions,
             py::arg("sessions"),
             "Analyse multiple sessions in one call.\n\n"
             "sessions: list of dicts, each with keys:\n"
             "  'user' (str), 'events' (list of event dicts)\n\n"
             "Returns list of result dicts with keys:\n"
             "  'user', 'output', 'score', 'verdict'")

        // ── query ──────────────────────────────────────────────────────────
        .def("getUsers",
             &APTEngineWrapper::getUsers,
             "Return list of all registered users.\n"
             "Each dict has: username, role, machine, permitted_devices.")

        .def("getDevices",
             &APTEngineWrapper::getDevices,
             "Return list of all network nodes.\n"
             "Each dict has: id, description, zone, required_role, "
             "security_level.")

        .def("getEdges",
             &APTEngineWrapper::getEdges,
             "Return list of all directed graph edges.\n"
             "Each dict has: from, to.")

        .def("getZones",
             &APTEngineWrapper::getZones,
             "Return list of all security zones.\n"
             "Each dict has: name, security_level.")

        .def("getThreatReport",
             &APTEngineWrapper::getThreatReport,
             "Return all analysed sessions sorted by risk score (highest first).\n"
             "Each dict has: user, role, score, verdict, path, score_items.")

        .def("getConfigSummary",
             &APTEngineWrapper::getConfigSummary,
             "Return a summary dict with counts of users, devices, zones, "
             "apt_signatures, sessions_analysed.")

        // ── utilities ──────────────────────────────────────────────────────
        .def("getRiskThreshold",
             &APTEngineWrapper::getRiskThreshold,
             "Return the email-alert risk threshold (default 30).")

        .def("getVersion",
             &APTEngineWrapper::getVersion,
             "Return engine version string.")

        .def("getBuildInfo",
             &APTEngineWrapper::getBuildInfo,
             "Return compile-time build date and time string.")

        .def("clearAlerts",
             &APTEngineWrapper::clearAlerts,
             "Clear all recorded session alerts from the engine.")

        .def("isBankHoliday",
             &APTEngineWrapper::checkIsBankHoliday,
             py::arg("date_yyyymmdd"),
             "Return True if the given YYYY-MM-DD date is a configured "
             "bank holiday.")

        .def("isWeekend",
             &APTEngineWrapper::checkIsWeekend,
             py::arg("date_yyyymmdd"),
             "Return True if the given YYYY-MM-DD date falls on a weekend.")
        ;
}