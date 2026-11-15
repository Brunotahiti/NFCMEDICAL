import SwiftUI

extension RequestKind {
    var color: Color {
        switch self {
        case .location: return .tpOK
        case .reprise: return .tpInfo
        case .prolongation: return .tpWarn
        case .probleme: return .tpCrit
        }
    }
}

extension RequestStatus {
    var color: Color {
        switch self {
        case .nouvelle: return .tpWarn
        case .planifiee: return .tpInfo
        case .faite: return .tpOK
        case .refusee: return .tpCrit
        case .annulee: return .tpMuted
        }
    }
}

/// Une ligne de demande.
struct RequestRow: View {
    @Environment(AppModel.self) private var model
    let r: RequestItem

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: r.type.symbol)
                .font(.system(size: 17, weight: .semibold))
                .foregroundStyle(r.type.color)
                .frame(width: 42, height: 42)
                .background(r.type.color.opacity(0.13), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            VStack(alignment: .leading, spacing: 3) {
                Text(model.requestTitle(r)).font(.subheadline.weight(.semibold)).foregroundStyle(Color.tpInk).lineLimit(2)
                Text(model.requestSubtitle(r)).font(.caption).foregroundStyle(Color.tpMuted).lineLimit(2)
            }
            Spacer(minLength: 4)
            if model.isUrgent(r) { Tag(text: "Urgent", color: .tpCrit) } else { Tag(text: r.state.label, color: r.state.color) }
        }
        .padding(.vertical, 2)
    }
}

/// Les quatre boutons « Nouvelle demande ».
struct NewRequestGrid: View {
    var onPick: (RequestKind) -> Void
    var body: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
            ForEach(RequestKind.allCases) { k in
                Button { onPick(k) } label: {
                    VStack(alignment: .leading, spacing: 4) {
                        Image(systemName: k.symbol).font(.title3).foregroundStyle(k.color)
                            .frame(width: 38, height: 38).background(k.color.opacity(0.13), in: RoundedRectangle(cornerRadius: 11, style: .continuous))
                        Text(k.label).font(.subheadline.bold()).foregroundStyle(Color.tpInk)
                        Text(k.subtitle).font(.caption).foregroundStyle(Color.tpMuted).multilineTextAlignment(.leading).lineLimit(2)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, minHeight: 118, alignment: .topLeading)
                    .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .shadow(color: .black.opacity(0.05), radius: 8, y: 3)
                }
                .buttonStyle(.plain)
            }
        }
    }
}

/// Feuilles de demande : location (avec produit éventuel) ou demande sur un équipement.
enum RequestSheet: Identifiable {
    case location(String?)
    case pick(RequestKind)
    case onEquipment(RequestKind, Int)
    case detail(Int)
    case catalog
    var id: String {
        switch self {
        case .location(let p): return "loc-" + (p ?? "")
        case .pick(let k): return "pick-" + k.rawValue
        case .onEquipment(let k, let e): return "eq-\(k.rawValue)-\(e)"
        case .detail(let i): return "detail-\(i)"
        case .catalog: return "catalog"
        }
    }
}

struct RequestSheetView: View {
    let sheet: RequestSheet
    init(_ sheet: RequestSheet) { self.sheet = sheet }
    var body: some View {
        switch sheet {
        case .location(let p): NewLocationRequestView(product: p)
        case .pick(let k): PickEquipmentView(kind: k)
        case .onEquipment(let k, let e): EquipmentRequestView(kind: k, equipmentId: e)
        case .detail(let i): RequestDetailView(id: i)
        case .catalog: CatalogView()
        }
    }
}

// MARK: - Liste des demandes

/// Sections de la liste des demandes, à placer dans une List ; le parent présente la feuille.
struct RequestsListView: View {
    @Environment(AppModel.self) private var model
    @State private var history = false
    @Binding var sheet: RequestSheet?
    init(sheet: Binding<RequestSheet?>) { _sheet = sheet }

    var body: some View {
        let open = model.openRequests
        let closed = model.requests.filter { !$0.isOpen }
        Group {
            if !model.isStaff {
                Section("Nouvelle demande") {
                    NewRequestGrid { k in sheet = k == .location ? .location(nil) : .pick(k) }
                        .listRowInsets(EdgeInsets(top: 8, leading: 0, bottom: 8, trailing: 0))
                        .listRowBackground(Color.clear)
                }
            }
            Section {
                Picker("", selection: $history) {
                    Text("En cours · \(open.count)").tag(false)
                    Text("Historique · \(closed.count)").tag(true)
                }
                .pickerStyle(.segmented)
            }
            .listRowBackground(Color.clear)
            if history {
                Section("Demandes clôturées") {
                    if closed.isEmpty { Text("Aucune demande clôturée.").foregroundStyle(.secondary) }
                    ForEach(closed) { r in row(r) }
                }
            } else if model.isStaff {
                let nw = open.filter { $0.state == .nouvelle }, pl = open.filter { $0.state == .planifiee }
                Section("À traiter · \(nw.count)") {
                    if nw.isEmpty { Text("Aucune nouvelle demande.").foregroundStyle(.secondary) }
                    ForEach(nw) { r in row(r) }
                }
                Section("Planifiées · \(pl.count)") {
                    if pl.isEmpty { Text("Aucun passage planifié.").foregroundStyle(.secondary) }
                    ForEach(pl) { r in row(r) }
                }
            } else {
                Section("Mes demandes") {
                    if open.isEmpty { Text("Aucune demande en cours.").foregroundStyle(.secondary) }
                    ForEach(open) { r in row(r) }
                }
            }
        }
    }

    private func row(_ r: RequestItem) -> some View {
        Button { sheet = .detail(r.id) } label: { RequestRow(r: r) }.buttonStyle(.plain)
    }
}

// MARK: - Détail et traitement

struct RequestDetailView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let id: Int
    init(id: Int) { self.id = id }
    @State private var planned = Calendar.current.date(byAdding: .day, value: 1, to: Date())!
    @State private var answer = ""
    @State private var confirmRefuse = false
    @State private var openEquipment: EquipmentLink?

    var body: some View {
        NavigationStack {
            Group {
                if let r = model.request(id) { form(r) } else { ContentUnavailableView("Demande introuvable", systemImage: "tray") }
            }
            .navigationTitle(model.request(id).map { $0.type.label } ?? "Demande")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Fermer") { dismiss() } } }
            .navigationDestination(item: $openEquipment) { EquipmentDetailView(id: $0.id) }
        }
        .onAppear {
            if let r = model.request(id), let d = Fmt.day(r.planned ?? r.wanted), d >= Calendar.current.startOfDay(for: Date()) { planned = d }
        }
    }

    @ViewBuilder
    private func form(_ r: RequestItem) -> some View {
        let p = model.patient(r.patientId), e = r.equipmentId.flatMap { model.equipment(id: $0) }
        Form {
            Section {
                HStack {
                    Image(systemName: r.type.symbol).foregroundStyle(r.type.color)
                    Text(model.requestTitle(r)).font(.headline)
                    Spacer()
                    Tag(text: r.state.label, color: r.state.color)
                }
                line("Pharmacie", model.pharmacy(r.pharmacyId)?.name)
                line("Bénéficiaire", p.map { $0.name + ($0.commune.map { " · " + $0 } ?? "") } ?? (r.patient.isEmpty ? nil : r.patient))
                if let a = p?.address, !a.isEmpty { line("Adresse", a) }
                if model.isStaff, let phone = p?.phone, !phone.isEmpty, let url = URL(string: "tel:" + phone.filter { $0.isNumber || $0 == "+" }) {
                    LabeledContent("Téléphone") { Link(phone, destination: url) }
                }
                line("Matériel", e.map { $0.name + " · " + $0.ref } ?? r.product)
                line("Durée", r.days.map { Fmt.duration($0) })
                line("Souhaitée le", r.wanted.map { Fmt.date($0) })
                line("Passage prévu", r.planned.map { Fmt.date($0) })
                line("Problème", r.reason.isEmpty ? nil : model.state?.reasons?[r.reason])
                if !r.note.isEmpty { VStack(alignment: .leading, spacing: 4) { Text("Précisions").font(.caption).foregroundStyle(.secondary); Text(r.note) } }
                if !r.answer.isEmpty { VStack(alignment: .leading, spacing: 4) { Text("Réponse du parc").font(.caption).foregroundStyle(.secondary); Text(r.answer) } }
                line("Envoyée", Fmt.dateTime(r.createdAt) + " · " + r.createdBy)
            }
            if r.isOpen && model.isStaff { staffActions(r) }
            if r.isOpen && !model.isStaff {
                Section {
                    Button("Annuler la demande", role: .destructive) {
                        Task { if await model.requestAction(r, action: "cancel") { dismiss() } }
                    }
                }
            }
            if let e {
                Section { Button { openEquipment = EquipmentLink(id: e.id) } label: { Label("Ouvrir la fiche du matériel", systemImage: "doc.text.magnifyingglass") } }
            }
        }
    }

    @ViewBuilder
    private func staffActions(_ r: RequestItem) -> some View {
        Section {
            if r.type != .prolongation {
                DatePicker("Date de passage", selection: $planned, in: Calendar.current.startOfDay(for: Date())..., displayedComponents: .date)
            }
            TextField("Message à la pharmacie (obligatoire pour refuser)", text: $answer, axis: .vertical).lineLimit(2...4)
            if r.type != .prolongation {
                Button { act(r, "plan", planned: Fmt.iso(planned)) } label: {
                    Label(r.state == .planifiee ? "Changer la date de passage" : "Planifier le passage", systemImage: "calendar")
                }
            }
        } header: { Text("Traitement") } footer: { Text("La pharmacie est prévenue par e-mail quand la demande est planifiée, effectuée ou refusée.") }

        switch r.type {
        case .location:
            let same = model.equipment.filter { $0.state == .dispo && $0.name == r.product }
            let kind = model.catalog.first { $0.name == r.product }?.kind
            let other = model.equipment.filter { $0.state == .dispo && $0.name != r.product && $0.kind == kind }.prefix(8)
            Section("Livrer · \(same.count) disponible\(same.count > 1 ? "s" : "")") {
                if same.isEmpty && other.isEmpty { Text("Aucun équipement disponible : planifiez la livraison ou proposez un autre matériel.").font(.footnote).foregroundStyle(.secondary) }
                ForEach(same + Array(other)) { e in
                    Button { act(r, "done", equipment: e.id) } label: {
                        HStack(spacing: 12) {
                            EquipmentThumb(photo: e.photo, size: 40)
                            VStack(alignment: .leading) {
                                Text(e.name).font(.subheadline.weight(.semibold)).foregroundStyle(Color.tpInk)
                                Text(e.ref + (e.name != r.product ? " · autre modèle" : "")).font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()
                            Tag(text: "Livrer", color: .tpOK)
                        }
                    }
                }
            }
        case .reprise:
            Section { Button { act(r, "done") } label: { Label("Reprise effectuée", systemImage: "arrow.uturn.backward") } }
        case .prolongation:
            Section { Button { act(r, "done") } label: { Label("Accepter la prolongation (+ \(Fmt.duration(r.days ?? 7)))", systemImage: "clock.arrow.circlepath") } }
        case .probleme:
            Section {
                Button { act(r, "done") } label: { Label("Problème réglé sur place", systemImage: "checkmark.seal") }
                Button { act(r, "done", fault: true) } label: { Label("Reprendre pour réparation", systemImage: "wrench.and.screwdriver") }
            }
        }
        Section {
            Button("Refuser la demande", role: .destructive) {
                if answer.trimmingCharacters(in: .whitespaces).isEmpty { model.errorMessage = "Indiquez le motif du refus : il sera transmis à la pharmacie." } else { confirmRefuse = true }
            }
            .confirmationDialog("Refuser cette demande ?", isPresented: $confirmRefuse, titleVisibility: .visible) {
                Button("Refuser", role: .destructive) { act(r, "refuse") }
            }
        }
    }

    private func act(_ r: RequestItem, _ action: String, planned: String? = nil, equipment: Int? = nil, fault: Bool = false) {
        Task {
            if await model.requestAction(r, action: action, planned: planned, answer: answer, equipment: equipment, fault: fault), action != "plan" { dismiss() }
        }
    }

    @ViewBuilder
    private func line(_ label: String, _ value: String?) -> some View {
        if let value, !value.isEmpty { LabeledContent(label, value: value) }
    }
}

// MARK: - Nouvelles demandes

struct NewLocationRequestView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var product: String
    @State private var patientId: Int?
    @State private var pharmacyId: Int?
    @State private var days = 28
    @State private var wanted = Calendar.current.date(byAdding: .day, value: 1, to: Date())!
    @State private var note = ""
    @State private var addingPatient = false
    init(product: String?) { _product = State(initialValue: product ?? "") }

    var body: some View {
        NavigationStack {
            Form {
                Section("Matériel") {
                    Picker("Produit", selection: $product) {
                        Text("Choisir…").tag("")
                        ForEach(model.catalog) { c in
                            Text(c.name + (c.dispo > 0 ? "" : " (sur demande)")).tag(c.name)
                        }
                    }
                    if let c = model.catalog.first(where: { $0.name == product }) {
                        LabeledContent("Tarif", value: Fmt.xpf(c.weekPrice) + " / semaine")
                    }
                }
                Section("Bénéficiaire") {
                    Picker("Bénéficiaire", selection: $patientId) {
                        Text("Choisir…").tag(Int?.none)
                        ForEach((model.state?.patients ?? []).filter { $0.anonymized != true }) { p in
                            Text(p.name + (p.commune.map { " · " + $0 } ?? "")).tag(Int?.some(p.id))
                        }
                    }
                    Button { addingPatient = true } label: { Label("Nouveau bénéficiaire", systemImage: "person.badge.plus") }
                }
                if model.isStaff {
                    Section("Pharmacie") {
                        Picker("Pharmacie", selection: $pharmacyId) {
                            Text("Choisir…").tag(Int?.none)
                            ForEach(model.state?.pharmacies ?? []) { Text($0.name).tag(Int?.some($0.id)) }
                        }
                    }
                }
                Section("Durée et date") {
                    Picker("Durée", selection: $days) {
                        Text("1 sem.").tag(7)
                        Text("2 sem.").tag(14)
                        Text("4 sem.").tag(28)
                        Text("3 mois").tag(90)
                    }
                    .pickerStyle(.segmented)
                    DatePicker("Livraison souhaitée", selection: $wanted, in: Calendar.current.startOfDay(for: Date())...(Calendar.current.date(byAdding: .day, value: 120, to: Date())!), displayedComponents: .date)
                }
                Section {
                    TextField("Accès, horaires, personne à prévenir…", text: $note, axis: .vertical).lineLimit(2...5)
                } header: { Text("Précisions (facultatif)") } footer: {
                    Text("Aucune information médicale : ni pathologie, ni ordonnance. L'ordonnance reste dans votre pharmacie.")
                }
            }
            .navigationTitle("Demande de location")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Envoyer") {
                        guard let patientId else { return }
                        var body: [String: Any] = ["kind": "location", "product": product, "patient": patientId, "days": days, "wanted": Fmt.iso(wanted), "note": String(note.prefix(300))]
                        if let pharmacyId { body["pharmacy"] = pharmacyId }
                        Task { if await model.createRequest(body) { dismiss() } }
                    }
                    .disabled(product.isEmpty || patientId == nil || (model.isStaff && pharmacyId == nil) || model.busy)
                }
            }
            .sheet(isPresented: $addingPatient) { PatientForm { patientId = $0 } }
        }
    }
}

/// Reprise, prolongation ou problème sur un équipement en location.
struct EquipmentRequestView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let kind: RequestKind
    let equipmentId: Int
    init(kind: RequestKind, equipmentId: Int) { self.kind = kind; self.equipmentId = equipmentId }
    @State private var days = 7
    @State private var wanted = Calendar.current.date(byAdding: .day, value: 1, to: Date())!
    @State private var reason = ""
    @State private var note = ""

    var body: some View {
        NavigationStack {
            Form {
                if let e = model.equipment(id: equipmentId) {
                    Section {
                        HStack(spacing: 12) {
                            EquipmentThumb(photo: e.photo, size: 46)
                            VStack(alignment: .leading) {
                                Text(e.name).font(.subheadline.weight(.semibold))
                                Text(e.ref + (model.patient(e.patientId).map { " · " + $0.name } ?? "")).font(.caption).foregroundStyle(.secondary)
                            }
                        }
                    }
                }
                switch kind {
                case .prolongation:
                    Section("Prolonger de") {
                        Picker("Durée", selection: $days) {
                            Text("1 sem.").tag(7)
                            Text("2 sem.").tag(14)
                            Text("4 sem.").tag(28)
                            Text("3 mois").tag(90)
                        }
                        .pickerStyle(.segmented)
                    }
                case .reprise:
                    Section { DatePicker("Reprise souhaitée", selection: $wanted, in: Calendar.current.startOfDay(for: Date())..., displayedComponents: .date) }
                default:
                    Section("Nature du problème") {
                        Picker("Problème", selection: $reason) {
                            Text("Choisir…").tag("")
                            ForEach(model.reasons, id: \.0) { Text($0.1).tag($0.0) }
                        }
                        .pickerStyle(.inline)
                        .labelsHidden()
                    }
                }
                Section {
                    TextField(kind == .probleme ? "Ce qui ne fonctionne pas, depuis quand…" : "Accès, horaires…", text: $note, axis: .vertical).lineLimit(2...5)
                } header: { Text(kind == .probleme ? "Description" : "Précisions (facultatif)") } footer: { Text("Aucune information médicale.") }
            }
            .navigationTitle(kind.label)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Envoyer") {
                        var body: [String: Any] = ["kind": kind.rawValue, "equipment": equipmentId, "note": String(note.prefix(300))]
                        if kind == .prolongation { body["days"] = days }
                        if kind == .reprise { body["wanted"] = Fmt.iso(wanted) }
                        if kind == .probleme { body["reason"] = reason }
                        Task { if await model.createRequest(body) { dismiss() } }
                    }
                    .disabled((kind == .probleme && reason.isEmpty) || model.busy)
                }
            }
        }
    }
}

/// Choisir l'équipement loué concerné par une reprise, une prolongation ou un problème.
struct PickEquipmentView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let kind: RequestKind
    init(kind: RequestKind) { self.kind = kind }
    @State private var chosen: EquipmentLink?
    @State private var last: Int?

    var body: some View {
        NavigationStack {
            List {
                let rented = model.equipment.filter { $0.state == .loc }
                if rented.isEmpty { Text("Aucun équipement en location.").foregroundStyle(.secondary) }
                ForEach(rented) { e in
                    let pending = model.openRequests(for: e).first { $0.type == kind }
                    Button { if pending == nil { last = e.id; chosen = EquipmentLink(id: e.id) } } label: {
                        HStack {
                            EquipmentRow(e: e)
                            if let pending { Tag(text: pending.state.label, color: pending.state.color) }
                        }
                    }
                    .buttonStyle(.plain)
                    .disabled(pending != nil)
                }
            }
            .navigationTitle(kind.label + " · quel matériel ?")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } } }
            .sheet(item: $chosen, onDismiss: { if model.openRequests.contains(where: { $0.type == kind && $0.equipmentId == last }) { dismiss() } }) { link in
                EquipmentRequestView(kind: kind, equipmentId: link.id)
            }
        }
    }
}

extension EquipmentLink: Identifiable {}

// MARK: - Catalogue, planning, suivi des pharmacies

struct CatalogView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    @State private var request: String?
    init() {}

    var body: some View {
        NavigationStack {
            List(model.catalog) { c in
                Button { if !model.isStaff { request = c.name } } label: {
                    HStack(spacing: 12) {
                        EquipmentThumb(photo: c.photo, size: 50)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(c.name).font(.subheadline.weight(.semibold)).foregroundStyle(Color.tpInk)
                            Text((c.brand ?? "") + " · " + Fmt.xpf(c.weekPrice) + " / sem.").font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        if model.isStaff { Tag(text: "\(c.dispo) / \(c.total)", color: c.dispo > 0 ? .tpOK : .tpWarn) }
                        else { Tag(text: c.dispo > 0 ? "Disponible" : "Sur demande", color: c.dispo > 0 ? .tpOK : .tpWarn) }
                    }
                }
                .buttonStyle(.plain)
            }
            .navigationTitle("Catalogue")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Fermer") { dismiss() } } }
            .sheet(item: Binding(get: { request.map { RequestSheet.location($0) } }, set: { if $0 == nil { request = nil } })) { RequestSheetView($0) }
        }
    }
}

/// Sections du planning, à placer dans une List ; le parent présente la feuille.
struct PlanningView: View {
    @Environment(AppModel.self) private var model
    @Binding var sheet: RequestSheet?
    init(sheet: Binding<RequestSheet?>) { _sheet = sheet }

    var body: some View {
        let items = model.planItems
        let days = Array(Set(items.map(\.day))).sorted()
        Group {
            if items.isEmpty {
                Section { Text("Rien de prévu dans les 14 prochains jours.").foregroundStyle(.secondary) }
            }
            ForEach(days, id: \.self) { d in
                Section(dayLabel(d) + " · \(items.filter { $0.day == d }.count)") {
                    ForEach(items.filter { $0.day == d }) { x in
                        if let eid = x.equipmentId {
                            NavigationLink(value: EquipmentLink(id: eid)) { planRow(x) }
                        } else {
                            Button { if let r = x.requestId { sheet = .detail(r) } } label: { planRow(x) }.buttonStyle(.plain)
                        }
                    }
                }
            }
        }
    }

    private func planRow(_ x: AppModel.PlanItem) -> some View {
                            HStack(spacing: 12) {
                                Image(systemName: x.symbol).foregroundStyle(x.late ? Color.tpCrit : Color.tpAccent).frame(width: 28)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(x.title + (x.commune.isEmpty ? "" : " · " + x.commune)).font(.subheadline.weight(.semibold)).foregroundStyle(Color.tpInk)
                                    Text(x.detail).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                                }
                                Spacer()
                                if x.toPlan { Tag(text: "À planifier", color: .tpWarn) } else if x.late { Tag(text: "Retard", color: .tpCrit) }
                            }
    }

    private func dayLabel(_ d: Int) -> String {
        if d < 0 { return "En retard" }
        if d == 0 { return "Aujourd'hui" }
        if d == 1 { return "Demain" }
        let date = Fmt.day(Fmt.addDays(model.today, d)) ?? Date()
        return date.formatted(.dateTime.weekday(.wide).day().month(.wide).locale(Fmt.fr)).capitalized(with: Fmt.fr)
    }
}

struct PharmacyFollowView: View {
    @Environment(AppModel.self) private var model
    init() {}

    var body: some View {
        List(model.state?.pharmacies ?? []) { f in
            NavigationLink { PharmacyDetailView(pharmacy: f) } label: {
                let s = model.stats(for: f)
                VStack(alignment: .leading, spacing: 3) {
                    Text(f.name).font(.subheadline.weight(.semibold))
                    Text("\(s.rented) en location · \(Fmt.xpf(s.weekly))/sem." + (s.late > 0 ? " · \(s.late) en retard" : "") + (s.requests > 0 ? " · \(s.requests) demande(s)" : ""))
                        .font(.caption).foregroundStyle(s.late > 0 ? Color.tpCrit : .secondary)
                }
            }
        }
        .navigationTitle("Suivi des pharmacies")
    }
}

struct PharmacyDetailView: View {
    @Environment(AppModel.self) private var model
    let pharmacy: Pharmacy
    init(pharmacy: Pharmacy) { self.pharmacy = pharmacy }
    @State private var sheet: RequestSheet?

    var body: some View {
        let s = model.stats(for: pharmacy)
        List {
            Section {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                    tile("\(s.rented)", "en location", nil)
                    tile(Fmt.xpf(s.weekly), "loyers / sem.", nil)
                    tile("\(s.beneficiaries)", "bénéficiaires", nil)
                    tile("\(s.late)", "retours en retard", s.late > 0 ? .tpCrit : nil)
                    tile("\(s.soon)", "fins sous 14 j", s.soon > 0 ? .tpWarn : nil)
                    tile("\(s.prescriptions)", "ordonnances à traiter", s.prescriptions > 0 ? .tpWarn : nil)
                }
                .listRowBackground(Color.clear)
                .listRowInsets(EdgeInsets())
            } footer: { Text(pharmacy.commune + (pharmacy.email.map { $0.isEmpty ? "" : " · " + $0 } ?? "")) }
            let reqs = model.openRequests.filter { $0.pharmacyId == pharmacy.id }
            if !reqs.isEmpty {
                Section("Demandes en cours") {
                    ForEach(reqs) { r in Button { sheet = .detail(r.id) } label: { RequestRow(r: r) }.buttonStyle(.plain) }
                }
            }
            Section("Locations en cours") {
                ForEach(model.equipment.filter { $0.state == .loc && $0.pharmacyId == pharmacy.id }) { e in
                    NavigationLink(value: EquipmentLink(id: e.id)) { EquipmentRow(e: e) }
                }
            }
        }
        .navigationTitle(pharmacy.name)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $sheet) { RequestSheetView($0) }
    }

    private func tile(_ v: String, _ l: String, _ c: Color?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(v).font(.headline).foregroundStyle(c ?? Color.tpInk).lineLimit(1).minimumScaleFactor(0.7)
            Text(l).font(.caption2).foregroundStyle(.secondary).lineLimit(2)
        }
        .padding(10)
        .frame(maxWidth: .infinity, minHeight: 64, alignment: .topLeading)
        .background((c ?? Color.tpAccent).opacity(0.1), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

/// Écrans autonomes (accueil, menu Plus) : la liste des demandes ou le planning dans leur propre List.
struct RequestsScreen: View {
    @Environment(AppModel.self) private var model
    @State private var sheet: RequestSheet?
    init() {}
    var body: some View {
        List { RequestsListView(sheet: $sheet) }
            .navigationTitle("Demandes")
            .refreshable { await model.refresh() }
            .sheet(item: $sheet) { RequestSheetView($0) }
    }
}

struct PlanningScreen: View {
    @Environment(AppModel.self) private var model
    @State private var sheet: RequestSheet?
    init() {}
    var body: some View {
        List { PlanningView(sheet: $sheet) }
            .navigationTitle("Planning des tournées")
            .refreshable { await model.refresh() }
            .sheet(item: $sheet) { RequestSheetView($0) }
    }
}

/// Bloc « Demandes » de l'accueil.
struct HomeRequestsSection: View {
    @Environment(AppModel.self) private var model
    @State private var sheet: RequestSheet?
    init() {}

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if model.isStaff {
                let nw = model.openRequests.filter { $0.state == .nouvelle }
                HStack {
                    Text("Demandes des pharmacies").font(.title3.bold())
                    if !nw.isEmpty { Text("\(nw.count)").font(.caption.bold()).foregroundStyle(.white).padding(.horizontal, 7).padding(.vertical, 2).background(Color.tpCrit, in: Capsule()) }
                    Spacer()
                    NavigationLink("Tout voir") { RequestsScreen() }.font(.subheadline.weight(.semibold))
                }
                if nw.isEmpty {
                    Card { Label("Aucune nouvelle demande.", systemImage: "tray").foregroundStyle(Color.tpMuted) }
                } else {
                    VStack(spacing: 0) {
                        ForEach(nw.prefix(4)) { r in
                            Button { sheet = .detail(r.id) } label: { RequestRow(r: r).padding(12) }.buttonStyle(.plain)
                            if r.id != nw.prefix(4).last?.id { Divider().padding(.leading, 66) }
                        }
                    }
                    .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
                HStack(spacing: 10) {
                    NavigationLink { PlanningScreen() } label: { pill("Planning des tournées", "map") }
                    NavigationLink { PharmacyFollowView() } label: { pill("Suivi des pharmacies", "cross.case") }
                }
                .buttonStyle(.plain)
            } else {
                HStack {
                    Text("Nouvelle demande").font(.title3.bold())
                    Spacer()
                    Button("Catalogue") { sheet = .catalog }.font(.subheadline.weight(.semibold))
                }
                NewRequestGrid { k in sheet = k == .location ? .location(nil) : .pick(k) }
                let open = model.openRequests
                if !open.isEmpty {
                    HStack {
                        Text("Mes demandes en cours").font(.headline)
                        Spacer()
                        NavigationLink("Tout voir") { RequestsScreen() }.font(.subheadline.weight(.semibold))
                    }
                    .padding(.top, 6)
                    VStack(spacing: 0) {
                        ForEach(open.prefix(5)) { r in
                            Button { sheet = .detail(r.id) } label: { RequestRow(r: r).padding(12) }.buttonStyle(.plain)
                            if r.id != open.prefix(5).last?.id { Divider().padding(.leading, 66) }
                        }
                    }
                    .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
            }
        }
        .sheet(item: $sheet) { RequestSheetView($0) }
    }

    private func pill(_ t: String, _ icon: String) -> some View {
        Label(t, systemImage: icon)
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(Color.tpAccent)
            .frame(maxWidth: .infinity, minHeight: 46)
            .background(Color.tpAccent.opacity(0.1), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}
