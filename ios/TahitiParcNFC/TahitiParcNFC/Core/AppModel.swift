import Foundation
import SwiftUI

enum Phase: Equatable {
    case loading, login, changePassword(forced: Bool), ready
}

/// État de l'application : session, données du parc et actions sur le serveur.
@MainActor
@Observable
final class AppModel {
    var phase: Phase = .loading
    var me: Me?
    var state: AppState?
    var toast: String?
    var errorMessage: String?
    var busy = false

    private let api = APIClient.shared
    private var toastTask: Task<Void, Never>?

    // MARK: Rôles

    var isStaff: Bool { me.map { $0.role == "admin" || $0.role == "equipe" } ?? false }
    var isAdmin: Bool { me?.role == "admin" }
    var isPharmacy: Bool { me?.role == "pharmacie" }
    var today: String { state?.today ?? Fmt.iso(Date()) }

    var roleLabel: String {
        switch me?.role {
        case "admin": return "Administrateur"
        case "equipe": return "Équipe du parc"
        case "pharmacie": return me?.pharmacy?.name ?? "Pharmacie"
        default: return ""
        }
    }

    // MARK: Session

    func start() async {
        guard phase == .loading else { return }
        do {
            let r: MeResponse = try await api.get("me")
            me = r.me
            if r.me.mustChange { phase = .changePassword(forced: true) } else { try await loadState(); phase = .ready }
        } catch {
            phase = .login
        }
    }

    func login(_ login: String, _ password: String) async {
        await run {
            let r: MeResponse = try await self.api.post("login", ["login": login, "password": password], as: MeResponse.self)
            self.me = r.me
            if r.me.mustChange {
                self.phase = .changePassword(forced: true)
            } else {
                try await self.loadState()
                self.phase = .ready
            }
        }
    }

    func changePassword(current: String, next: String) async -> Bool {
        var ok = false
        await run {
            let r: MeResponse = try await self.api.post("password", ["current": current, "next": next], as: MeResponse.self)
            self.me = r.me
            try await self.loadState()
            self.phase = .ready
            self.show("Mot de passe enregistré")
            ok = true
        }
        return ok
    }

    func logout() async {
        _ = try? await api.post("logout")
        api.clearSession()
        me = nil
        state = nil
        phase = .login
    }

    // MARK: Données

    func loadState() async throws {
        let s: AppState = try await api.get("state")
        state = s
        me = s.me
    }

    func refresh() async {
        do { try await loadState() } catch { handle(error) }
    }

    var equipment: [Equipment] { state?.equipment ?? [] }

    func equipment(id: Int) -> Equipment? { equipment.first { $0.id == id } }
    func patient(_ id: Int?) -> Patient? { id.flatMap { pid in state?.patients.first { $0.id == pid } } }
    func pharmacy(_ id: Int?) -> Pharmacy? { id.flatMap { pid in state?.pharmacies.first { $0.id == pid } } }

    /// Retrouve l'équipement à partir du contenu d'une puce (lien complet ou référence seule).
    func equipment(fromTag text: String) -> Equipment? {
        let clean = text.trimmingCharacters(in: .whitespacesAndNewlines)
        let norm = { (s: String) in s.lowercased().trimmingCharacters(in: CharacterSet(charactersIn: "/")) }
        if let e = equipment.first(where: { ($0.link ?? "").isEmpty == false && norm($0.link!) == norm(clean) }) { return e }
        let last = clean.split(separator: "/").last.map(String.init) ?? clean
        let ref = (last.removingPercentEncoding ?? last).uppercased()
        return equipment.first { $0.ref.uppercased() == ref }
    }

    func count(_ s: EquipmentState) -> Int { equipment.filter { $0.state == s }.count }

    /// Jours avant la fin prévue (négatif : retour en retard).
    func daysLeft(_ e: Equipment) -> Int? { Fmt.days(from: today, to: e.plannedEnd) }
    func daysRented(_ e: Equipment) -> Int? { Fmt.days(from: e.since, to: today) }
    func daysToCheck(_ e: Equipment) -> Int? { Fmt.days(from: today, to: e.nextCheck) }

    /// Jours restants de validité de l'ordonnance (nil : pas d'ordonnance vérifiée).
    func prescriptionDaysLeft(_ e: Equipment) -> Int? { e.prescription?.valid.flatMap { Fmt.days(from: today, to: $0) } }

    var monthlyRevenue: Int {
        equipment.filter { $0.state == .loc }.reduce(0) { $0 + Int((Double($1.weekPrice) * 30.0 / 7.0).rounded()) }
    }

    var alerts: [AlertItem] {
        var list: [AlertItem] = []
        for e in equipment {
            if e.state == .loc, let d = daysLeft(e) {
                if d < 0 {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: "Retour en retard de \(Fmt.duration(-d))", tag: "Retard", level: .crit))
                } else if d <= 3 {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: d == 0 ? "Fin de location aujourd'hui" : "Fin de location dans \(Fmt.duration(d))", tag: "Fin proche", level: .warn))
                }
            }
            if e.state == .loc {
                if e.prescription == nil {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: "Ordonnance non vérifiée par la pharmacie", tag: "Ordonnance", level: isPharmacy ? .crit : .info))
                } else if let v = prescriptionDaysLeft(e), v <= 15 {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: v < 0 ? "Ordonnance expirée : nouvelle ordonnance à demander" : "Ordonnance valable encore \(Fmt.duration(v))", tag: "Renouvellement", level: v < 0 ? .crit : .warn))
                }
            }
            if isStaff {
                if e.state == .maint {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: "En maintenance depuis le \(Fmt.date(e.since))", tag: "Atelier", level: .warn))
                } else if let c = daysToCheck(e), c <= 30 {
                    list.append(AlertItem(equipmentId: e.id, title: "\(e.name) · \(e.ref)", detail: c < 0 ? "Contrôle de sécurité dépassé" : "Contrôle de sécurité dans \(Fmt.duration(c))", tag: "Contrôle", level: c < 0 ? .crit : .info))
                }
            }
        }
        let order: (AlertLevel) -> Int = { $0 == .crit ? 0 : $0 == .warn ? 1 : 2 }
        return list.sorted { order($0.level) < order($1.level) }
    }

    // MARK: Demandes

    var requests: [RequestItem] { state?.requests ?? [] }
    var openRequests: [RequestItem] { requests.filter(\.isOpen) }
    var catalog: [CatalogItem] { state?.catalog ?? [] }
    var reasons: [(String, String)] {
        let order = ["panne", "bruit", "casse", "piles", "autre"]
        let r = state?.reasons ?? [:]
        return order.compactMap { k in r[k].map { (k, $0) } }
    }
    func request(_ id: Int) -> RequestItem? { requests.first { $0.id == id } }
    func openRequests(for e: Equipment) -> [RequestItem] { openRequests.filter { $0.equipmentId == e.id } }

    func requestTitle(_ r: RequestItem) -> String {
        r.type.label + " · " + (r.equipmentId.flatMap { equipment(id: $0)?.name } ?? r.product)
    }

    func requestSubtitle(_ r: RequestItem) -> String {
        var parts: [String] = []
        if isStaff, let f = pharmacy(r.pharmacyId) { parts.append(f.name) }
        if let p = patient(r.patientId) { parts.append(p.name + (p.commune.map { " (\($0))" } ?? "")) } else if !r.patient.isEmpty { parts.append(r.patient) }
        if let e = r.equipmentId.flatMap({ equipment(id: $0) }) { parts.append(e.ref) }
        switch r.state {
        case .planifiee: if let d = r.planned { parts.append("passage le " + Fmt.date(d)) }
        case .nouvelle:
            if let d = r.wanted { parts.append("souhaitée le " + Fmt.date(d)) }
            else if r.type == .prolongation, let d = r.days { parts.append("+ " + Fmt.duration(d)) }
        default: if !r.answer.isEmpty { parts.append(r.answer) }
        }
        return parts.joined(separator: " · ")
    }

    func isUrgent(_ r: RequestItem) -> Bool {
        r.state == .nouvelle && (Fmt.days(from: today, to: r.wanted) ?? 1) <= 0
    }

    /// Crée une demande (body : kind, et selon le type product/patient/days/wanted/equipment/reason/note).
    func createRequest(_ body: [String: Any]) async -> Bool {
        await mutate("requests", body, isStaff ? "Demande enregistrée" : "Demande envoyée au parc")
    }

    /// Traite une demande : plan, refuse, done, cancel.
    func requestAction(_ r: RequestItem, action: String, planned: String? = nil, answer: String = "", equipment: Int? = nil, fault: Bool = false) async -> Bool {
        var body: [String: Any] = ["action": action, "answer": answer]
        if let planned { body["planned"] = planned }
        if let equipment { body["equipment"] = equipment }
        if fault { body["fault"] = true }
        let msg = ["plan": "Passage planifié", "refuse": "Demande refusée", "done": fault ? "Matériel envoyé à l'atelier" : "Demande traitée", "cancel": "Demande annulée"][action] ?? "Enregistré"
        return await mutate("requests/\(r.id)", body, msg)
    }

    struct PlanItem: Identifiable {
        let id: String
        let day: Int
        let late: Bool
        let title: String
        let detail: String
        let commune: String
        let symbol: String
        let toPlan: Bool
        let requestId: Int?
        let equipmentId: Int?
    }

    /// Planning des tournées : livraisons et reprises demandées, fins de location sur 14 jours.
    var planItems: [PlanItem] {
        var out: [PlanItem] = []
        for r in openRequests where r.type != .prolongation {
            let date = r.state == .planifiee ? r.planned : r.wanted
            guard let d = Fmt.days(from: today, to: date) else { continue }
            let p = patient(r.patientId)
            out.append(PlanItem(id: "r\(r.id)", day: max(d, -1), late: d < 0, title: (r.type == .location ? "Livraison" : r.type == .reprise ? "Reprise" : "Intervention"),
                                detail: [requestTitle(r).components(separatedBy: " · ").dropFirst().joined(separator: " · "), p?.name ?? "", pharmacy(r.pharmacyId)?.name ?? ""].filter { !$0.isEmpty }.joined(separator: " · "),
                                commune: p?.commune ?? "", symbol: r.type.symbol, toPlan: r.state == .nouvelle, requestId: r.id, equipmentId: nil))
        }
        for e in equipment where e.state == .loc {
            guard let d = daysLeft(e), d <= 14 else { continue }
            if openRequests(for: e).contains(where: { $0.type == .reprise || $0.type == .prolongation }) { continue }
            let p = patient(e.patientId)
            out.append(PlanItem(id: "e\(e.id)", day: max(d, -1), late: d < 0, title: d < 0 ? "Retour en retard" : "Fin de location",
                                detail: [e.name + " · " + e.ref, p?.name ?? "", pharmacy(e.pharmacyId)?.name ?? ""].filter { !$0.isEmpty }.joined(separator: " · "),
                                commune: p?.commune ?? "", symbol: "arrow.uturn.backward", toPlan: false, requestId: nil, equipmentId: e.id))
        }
        return out.sorted { ($0.day, $0.commune) < ($1.day, $1.commune) }
    }

    struct PharmacyStats {
        let rented: Int, weekly: Int, late: Int, soon: Int, prescriptions: Int, requests: Int, beneficiaries: Int
    }

    func stats(for f: Pharmacy) -> PharmacyStats {
        let it = equipment.filter { $0.state == .loc && $0.pharmacyId == f.id }
        return PharmacyStats(rented: it.count, weekly: it.reduce(0) { $0 + $1.weekPrice },
                             late: it.filter { (daysLeft($0) ?? 0) < 0 }.count,
                             soon: it.filter { (0...14).contains(daysLeft($0) ?? -1) }.count,
                             prescriptions: it.filter { $0.prescription == nil || (prescriptionDaysLeft($0) ?? 99) <= 15 }.count,
                             requests: openRequests.filter { $0.pharmacyId == f.id }.count,
                             beneficiaries: Set(it.compactMap(\.patientId)).count)
    }

    // MARK: Actions

    func action(_ e: Equipment, _ action: String, message: String) async {
        await mutate("equipment/\(e.id)/action", ["action": action], message)
    }

    func rent(_ e: Equipment, patient: Int, pharmacy: Int, days: Int) async -> Bool {
        await mutate("rentals", ["equipment": e.id, "patient": patient, "pharmacy": pharmacy, "days": days], "Location enregistrée")
    }

    func extend(_ e: Equipment, days: Int) async {
        await mutate("rentals/extend", ["equipment": e.id, "days": days], "Location prolongée de \(Fmt.duration(days))")
    }

    func addPatient(name: String, commune: String, address: String, phone: String) async -> Int? {
        var id: Int?
        await run {
            let r: CreatedID = try await self.api.post("patients", ["name": name, "commune": commune, "address": address, "phone": phone], as: CreatedID.self)
            try await self.loadState()
            id = r.id
        }
        return id
    }

    func verifyPrescription(_ e: Equipment, date: String, validUntil: String, ref: String) async -> Bool {
        guard let rid = e.rentalId else { return false }
        return await mutate("rentals/\(rid)/prescription", ["date": date, "valid_until": validUntil, "ref": ref, "attest": true], "Ordonnance vérifiée")
    }

    func cancelPrescription(_ e: Equipment) async {
        guard let rid = e.rentalId else { return }
        await mutate("rentals/\(rid)/prescription/delete", [:], "Vérification annulée")
    }

    func setLink(_ e: Equipment, link: String) async -> Bool {
        await mutate("equipment/\(e.id)/link", ["link": link], link.isEmpty ? "Puce retirée" : "Puce associée à \(e.ref)")
    }

    /// Enregistre un passage (scan NFC ou saisie) avec la position si elle est connue.
    func recordScan(_ e: Equipment, source: String, location: LocationFix?) async {
        var body: [String: Any] = ["equipment": e.id, "source": source]
        if let location {
            body["lat"] = location.latitude
            body["lon"] = location.longitude
            body["accuracy"] = location.accuracy
        }
        await mutate("scans", body, location == nil ? "Passage enregistré (sans position)" : "Passage et position enregistrés")
    }

    func uploadPhoto(_ e: Equipment, jpeg: Data, kind: String, location: LocationFix?) async -> Bool {
        var headers = ["X-Kind": kind]
        if let location {
            headers["X-Lat"] = String(location.latitude)
            headers["X-Lon"] = String(location.longitude)
            headers["X-Acc"] = String(location.accuracy)
        }
        var ok = false
        await run {
            try await self.api.upload("equipment/\(e.id)/photos", data: jpeg, contentType: "image/jpeg", headers: headers)
            try await self.loadState()
            self.show("Photo horodatée enregistrée")
            ok = true
        }
        return ok
    }

    func deletePhoto(_ id: Int) async {
        await mutate("photos/\(id)/delete", [:], "Photo supprimée")
    }

    func detail(_ e: Equipment) async -> EquipmentDetail? {
        do { return try await api.get("equipment/\(e.id)") } catch { handle(error); return nil }
    }

    func billing(month: String, pharmacy: Int?) async -> Billing? {
        var path = "billing?month=\(month)"
        if let pharmacy { path += "&pharmacy=\(pharmacy)" }
        do { return try await api.get(path) } catch { handle(error); return nil }
    }

    func billingCSV(month: String, pharmacy: Int?) async -> URL? {
        var path = "billing.csv?month=\(month)"
        if let pharmacy { path += "&pharmacy=\(pharmacy)" }
        do { return try await api.download(path, filename: "Facturation-\(month).csv") } catch { handle(error); return nil }
    }

    func guide(_ name: String) async -> URL? {
        let title = ["pharmacie": "Guide-portail-pharmacie", "administrateur": "Guide-grossiste", "technicien": "Guide-technicien", "iphone": "Guide-application-iPhone"][name] ?? "Guide"
        do { return try await api.download("guides/\(name).pdf", filename: title + ".pdf") } catch { handle(error); return nil }
    }

    // MARK: Outils

    @discardableResult
    private func mutate(_ path: String, _ body: [String: Any], _ message: String) async -> Bool {
        var ok = false
        await run {
            try await self.api.post(path, body)
            try await self.loadState()
            self.show(message)
            ok = true
        }
        return ok
    }

    private func run(_ work: @escaping () async throws -> Void) async {
        busy = true
        defer { busy = false }
        do { try await work() } catch { handle(error) }
    }

    private func handle(_ error: Error) {
        if let e = error as? APIError, e.status == 401, phase != .login {
            api.clearSession()
            phase = .login
            errorMessage = "Votre session a expiré. Reconnectez-vous."
            return
        }
        if let e = error as? APIError, e.status == 403, e.message.contains("mot de passe provisoire") {
            phase = .changePassword(forced: true)
            return
        }
        errorMessage = error.localizedDescription
    }

    func show(_ text: String) {
        toastTask?.cancel()
        withAnimation { toast = text }
        toastTask = Task {
            try? await Task.sleep(for: .seconds(2.4))
            if !Task.isCancelled { withAnimation { self.toast = nil } }
        }
    }
}
