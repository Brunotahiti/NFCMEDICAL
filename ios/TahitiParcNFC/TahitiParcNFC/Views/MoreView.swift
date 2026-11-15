import SwiftUI

struct MoreView: View {
    @Environment(AppModel.self) private var model
    @State private var changingPassword = false
    @State private var shared: SharedFile?
    @State private var confirmLogout = false

    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 14) {
                        Text(Fmt.initials(model.me?.name ?? "?"))
                            .font(.headline).foregroundStyle(.white)
                            .frame(width: 52, height: 52).background(LinearGradient.tpHero, in: Circle())
                        VStack(alignment: .leading, spacing: 2) {
                            Text(model.me?.name ?? "").font(.headline)
                            Text(model.roleLabel).font(.subheadline).foregroundStyle(.secondary)
                            Text(model.me?.login ?? "").font(.caption).foregroundStyle(.tertiary)
                        }
                    }
                    Button { changingPassword = true } label: { Label("Changer de mot de passe", systemImage: "key") }
                }
                if model.isStaff {
                    Section("Gestion") {
                        NavigationLink { BillingContent() } label: { Label("Facturation", systemImage: "doc.text") }
                        NavigationLink { MaintenanceView() } label: { Label("Entretien et contrôles", systemImage: "wrench.and.screwdriver") }
                    }
                }
                Section("Guides d'utilisation (PDF)") {
                    guide("pharmacie", "Guide de la pharmacie", "cross.case")
                    if model.isStaff {
                        guide("technicien", "Guide du technicien", "wave.3.right")
                        guide("administrateur", "Guide de l'administrateur", "person.badge.key")
                    }
                }
                Section("Confidentialité") {
                    Label("Aucune ordonnance n'est stockée en ligne : elles restent sur le serveur de votre pharmacie.", systemImage: "lock.shield")
                    Label("Aucune donnée médicale : seuls le nom, l'adresse, la commune et le téléphone du bénéficiaire sont enregistrés, chiffrés.", systemImage: "person.text.rectangle")
                    Label("Données anonymisées 3 ans après la dernière location.", systemImage: "clock.badge.checkmark")
                }
                .font(.footnote)
                Section {
                    Link(destination: URL(string: Server.site)!) { Label("Ouvrir la version web", systemImage: "safari") }
                    Button(role: .destructive) { confirmLogout = true } label: { Label("Se déconnecter", systemImage: "rectangle.portrait.and.arrow.right") }
                } footer: {
                    Text("Tahiti Parc NFC \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "") · ManaProcess")
                        .frame(maxWidth: .infinity).padding(.top, 8)
                }
            }
            .navigationTitle("Plus")
            .sheet(isPresented: $changingPassword) { PasswordView(forced: false) }
            .sheet(item: $shared) { ShareSheet(items: [$0.url]) }
            .confirmationDialog("Se déconnecter ?", isPresented: $confirmLogout, titleVisibility: .visible) {
                Button("Se déconnecter", role: .destructive) { Task { await model.logout() } }
            }
            .navigationDestination(for: EquipmentLink.self) { EquipmentDetailView(id: $0.id) }
        }
    }

    private func guide(_ name: String, _ title: String, _ icon: String) -> some View {
        Button {
            Task { if let url = await model.guide(name) { shared = SharedFile(url: url) } }
        } label: { Label(title, systemImage: icon) }
    }
}

/// Entretien : désinfections en attente, maintenance, contrôles à venir.
struct MaintenanceView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            section("Désinfection en attente", model.equipment.filter { $0.state == .desinf })
            section("En maintenance", model.equipment.filter { $0.state == .maint })
            section("Contrôles dans les 30 jours", model.equipment
                .filter { $0.state != .maint && (model.daysToCheck($0) ?? 999) <= 30 }
                .sorted { (model.daysToCheck($0) ?? 0) < (model.daysToCheck($1) ?? 0) })
        }
        .navigationTitle("Entretien")
        .refreshable { await model.refresh() }
    }

    @ViewBuilder
    private func section(_ title: String, _ items: [Equipment]) -> some View {
        Section("\(title) · \(items.count)") {
            if items.isEmpty { Text("Rien à traiter.").foregroundStyle(.secondary) }
            ForEach(items.prefix(200)) { e in
                NavigationLink(value: EquipmentLink(id: e.id)) { EquipmentRow(e: e) }
            }
        }
    }
}
