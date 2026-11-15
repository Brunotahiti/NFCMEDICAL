import SwiftUI

/// Mise en location d'un équipement disponible.
struct NewRentalView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let equipment: Equipment
    init(equipment: Equipment) { self.equipment = equipment }
    @State private var patientId: Int?
    @State private var pharmacyId: Int?
    @State private var days = 28
    @State private var addingPatient = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack(spacing: 12) {
                        EquipmentThumb(photo: equipment.photo, size: 48)
                        VStack(alignment: .leading) {
                            Text(equipment.name).font(.subheadline.weight(.semibold))
                            Text(equipment.ref + " · " + Fmt.xpf(equipment.weekPrice) + " / semaine").font(.caption).foregroundStyle(.secondary)
                        }
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
                Section("Pharmacie") {
                    Picker("Pharmacie", selection: $pharmacyId) {
                        Text("Choisir…").tag(Int?.none)
                        ForEach(model.state?.pharmacies ?? []) { f in Text(f.name + " · " + f.commune).tag(Int?.some(f.id)) }
                    }
                }
                Section {
                    Picker("Durée", selection: $days) {
                        Text("1 sem.").tag(7)
                        Text("2 sem.").tag(14)
                        Text("4 sem.").tag(28)
                        Text("3 mois").tag(90)
                    }
                    .pickerStyle(.segmented)
                } header: { Text("Durée") } footer: {
                    Text("Fin prévue le \(Fmt.date(Fmt.addDays(model.today, days))) · environ \(Fmt.xpf(Int((Double(equipment.weekPrice) * Double(days) / 7).rounded())))")
                }
            }
            .navigationTitle("Mise en location")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Valider") {
                        guard let patientId, let pharmacyId else { return }
                        Task { if await model.rent(equipment, patient: patientId, pharmacy: pharmacyId, days: days) { dismiss() } }
                    }
                    .disabled(patientId == nil || pharmacyId == nil || model.busy)
                }
            }
            .sheet(isPresented: $addingPatient) { PatientForm { patientId = $0 } }
        }
    }
}

/// Bénéficiaire : nom, adresse, commune, téléphone. Aucune donnée médicale.
struct PatientForm: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    var onCreated: (Int) -> Void
    init(onCreated: @escaping (Int) -> Void) { self.onCreated = onCreated }
    @State private var name = ""
    @State private var address = ""
    @State private var commune = ""
    @State private var phone = ""

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Nom et prénom", text: $name).textContentType(.name)
                    TextField("Adresse", text: $address).textContentType(.fullStreetAddress)
                    Picker("Commune", selection: $commune) {
                        Text("Choisir…").tag("")
                        ForEach(model.state?.communes ?? [], id: \.self) { Text($0).tag($0) }
                    }
                    TextField("Téléphone", text: $phone).keyboardType(.phonePad).textContentType(.telephoneNumber)
                } footer: {
                    Text("Coordonnées chiffrées sur le serveur, anonymisées 3 ans après la dernière location. N'inscrivez aucune information médicale.")
                }
            }
            .navigationTitle("Nouveau bénéficiaire")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Ajouter") {
                        Task {
                            if let id = await model.addPatient(name: name, commune: commune, address: address, phone: phone) { onCreated(id); dismiss() }
                        }
                    }
                    .disabled(name.trimmingCharacters(in: .whitespaces).count < 2 || commune.isEmpty || model.busy)
                }
            }
        }
    }
}

/// Locations en cours (et terminées pour l'équipe).
struct LocationsView: View {
    @Environment(AppModel.self) private var model
    @State private var search = ""
    @State private var showClosed = false

    private var current: [Equipment] {
        model.equipment.filter { $0.state == .loc }
            .filter { e in search.isEmpty || [e.ref, e.name, model.patient(e.patientId)?.name ?? "", model.pharmacy(e.pharmacyId)?.name ?? ""].contains { $0.localizedCaseInsensitiveContains(search) } }
            .sorted { (model.daysLeft($0) ?? 999) < (model.daysLeft($1) ?? 999) }
    }

    var body: some View {
        NavigationStack {
            List {
                Picker("", selection: $showClosed) {
                    Text("En cours").tag(false)
                    Text("Terminées").tag(true)
                }
                .pickerStyle(.segmented)
                .listRowBackground(Color.clear)
                if showClosed {
                    let closed = model.state?.closed ?? []
                    if closed.isEmpty { Text("Aucune location terminée.").foregroundStyle(.secondary) }
                    ForEach(closed) { r in
                        HStack(spacing: 12) {
                            EquipmentThumb(photo: r.equipment.photo, size: 44)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(r.equipment.name + " · " + r.equipment.ref).font(.subheadline.weight(.semibold)).lineLimit(1)
                                Text((model.patient(r.patientId)?.name ?? "—") + " · " + (model.pharmacy(r.pharmacyId)?.name ?? "")).font(.caption).foregroundStyle(.secondary).lineLimit(1)
                                Text("Du \(Fmt.date(r.start)) au \(Fmt.date(r.end))").font(.caption2).foregroundStyle(.secondary)
                            }
                            Spacer()
                            Text(Fmt.xpf(r.amount)).font(.caption.weight(.semibold))
                        }
                    }
                } else {
                    if current.isEmpty { Text("Aucune location en cours.").foregroundStyle(.secondary) }
                    ForEach(current) { e in
                        NavigationLink(value: EquipmentLink(id: e.id)) { EquipmentRow(e: e) }
                    }
                }
            }
            .searchable(text: $search, prompt: "Bénéficiaire, référence, pharmacie…")
            .navigationTitle("Locations")
            .refreshable { await model.refresh() }
            .navigationDestination(for: EquipmentLink.self) { EquipmentDetailView(id: $0.id) }
        }
    }
}
