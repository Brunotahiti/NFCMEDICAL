import SwiftUI

struct EquipmentLink: Hashable { let id: Int }

struct DashboardView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    hero
                    if model.isStaff { stateGrid }
                    alertsSection
                }
                .padding(16)
            }
            .background(Color.tpBackground)
            .navigationTitle("Accueil")
            .toolbarTitleDisplayMode(.inline)
            .refreshable { await model.refresh() }
            .navigationDestination(for: EquipmentLink.self) { EquipmentDetailView(id: $0.id) }
            .navigationDestination(for: EquipmentState.self) { EquipmentListView(filter: $0) }
        }
    }

    private var hero: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Bonjour \(model.me?.name.components(separatedBy: " ").first ?? "")")
                        .font(.title2.bold())
                    Text(model.roleLabel + " · " + Fmt.longDate(model.today))
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.75))
                }
                Spacer()
                Image(systemName: "wave.3.right.circle.fill")
                    .font(.system(size: 38))
                    .foregroundStyle(Color.tpBrand)
            }
            let loc = model.count(.loc), total = model.equipment.count
            if model.isStaff {
                HStack(alignment: .firstTextBaseline) {
                    Text("\(total == 0 ? 0 : loc * 100 / total) %").font(.system(size: 44, weight: .bold, design: .rounded))
                    Text("du parc en location").foregroundStyle(.white.opacity(0.8))
                }
                ProgressView(value: Double(loc), total: Double(max(total, 1))).tint(.tpBrand)
                HStack {
                    metric("\(total)", "équipements")
                    Spacer()
                    metric(Fmt.xpf(model.monthlyRevenue), "par mois (estimé)")
                }
            } else {
                HStack(alignment: .firstTextBaseline) {
                    Text("\(loc)").font(.system(size: 44, weight: .bold, design: .rounded))
                    Text(loc > 1 ? "locations en cours" : "location en cours").foregroundStyle(.white.opacity(0.8))
                }
                let missing = model.equipment.filter { $0.prescription == nil }.count
                metric("\(missing)", missing > 1 ? "ordonnances à vérifier" : "ordonnance à vérifier")
            }
        }
        .foregroundStyle(.white)
        .padding(20)
        .background(LinearGradient.tpHero, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func metric(_ value: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(value).font(.headline)
            Text(label).font(.caption).foregroundStyle(.white.opacity(0.7))
        }
    }

    private var stateGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            ForEach(EquipmentState.allCases) { s in
                NavigationLink(value: s) {
                    VStack(alignment: .leading, spacing: 8) {
                        Image(systemName: s.symbol).font(.title3).foregroundStyle(s.color)
                        Text("\(model.count(s))").font(.title.bold()).foregroundStyle(Color.tpInk)
                        Text(s.label).font(.subheadline).foregroundStyle(Color.tpMuted)
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var alertsSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("À traiter").font(.title3.bold())
            let alerts = model.alerts
            if alerts.isEmpty {
                Card {
                    Label("Rien à signaler aujourd'hui.", systemImage: "checkmark.seal")
                        .foregroundStyle(Color.tpOK)
                }
            } else {
                ForEach(alerts.prefix(30)) { a in
                    NavigationLink(value: EquipmentLink(id: a.equipmentId ?? 0)) {
                        HStack(spacing: 12) {
                            Circle().fill(a.level.color).frame(width: 10, height: 10)
                            VStack(alignment: .leading, spacing: 3) {
                                Text(a.title).font(.subheadline.weight(.semibold)).foregroundStyle(Color.tpInk)
                                Text(a.detail).font(.caption).foregroundStyle(Color.tpMuted)
                            }
                            Spacer()
                            Tag(text: a.tag, color: a.level.color)
                        }
                        .padding(12)
                        .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}
