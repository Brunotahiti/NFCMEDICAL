import SwiftUI

/// Onglet Facturation (pharmacie).
struct BillingView: View {
    var body: some View { NavigationStack { BillingContent() } }
}

/// Facturation mensuelle : jours loués dans le mois, par pharmacie.
struct BillingContent: View {
    @Environment(AppModel.self) private var model
    @State private var month = Fmt.month(Date())
    @State private var pharmacy: Int?
    @State private var billing: Billing?
    @State private var loading = false
    @State private var shared: SharedFile?

    var body: some View {
        Group {
            List {
                Section {
                    HStack {
                        Button { shift(-1) } label: { Image(systemName: "chevron.left") }
                        Spacer()
                        Text(Fmt.monthName(month)).font(.headline)
                        Spacer()
                        Button { shift(1) } label: { Image(systemName: "chevron.right") }.disabled(month >= Fmt.month(Date()))
                    }
                    .buttonStyle(.borderless)
                    if model.isStaff {
                        Picker("Pharmacie", selection: $pharmacy) {
                            Text("Toutes").tag(Int?.none)
                            ForEach(model.state?.pharmacies ?? []) { Text($0.name).tag(Int?.some($0.id)) }
                        }
                    }
                }
                if let b = billing {
                    Section {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(Fmt.xpf(b.total)).font(.system(size: 34, weight: .bold, design: .rounded)).foregroundStyle(Color.tpAccent)
                            Text("\(b.lines.count) ligne\(b.lines.count > 1 ? "s" : "")" + (b.provisional ? " · montant provisoire (mois en cours)" : ""))
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    }
                    ForEach(groups(b), id: \.0) { name, lines in
                        Section {
                            ForEach(lines) { l in
                                VStack(alignment: .leading, spacing: 3) {
                                    HStack {
                                        Text(l.patient).font(.subheadline.weight(.semibold))
                                        Spacer()
                                        Text(Fmt.xpf(l.amount)).font(.subheadline.weight(.semibold))
                                    }
                                    Text("\(l.equipment) · \(l.ref)").font(.caption).foregroundStyle(.secondary)
                                    Text("Du \(Fmt.date(l.from)) au \(Fmt.date(l.to)) · \(l.days) j · \(Fmt.xpf(l.weekPrice))/sem." + (l.open ? " · en cours" : ""))
                                        .font(.caption2).foregroundStyle(.secondary)
                                    if l.prescDate == nil {
                                        Text("Ordonnance non vérifiée").font(.caption2.weight(.semibold)).foregroundStyle(Color.tpWarn)
                                    }
                                }
                            }
                        } header: {
                            HStack { Text(name); Spacer(); Text(Fmt.xpf(lines.reduce(0) { $0 + $1.amount })) }
                        }
                    }
                } else if loading {
                    HStack { Spacer(); ProgressView(); Spacer() }
                }
            }
            .navigationTitle("Facturation")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Task { if let url = await model.billingCSV(month: month, pharmacy: pharmacy) { shared = SharedFile(url: url) } }
                    } label: { Image(systemName: "square.and.arrow.up") }
                }
            }
            .task(id: "\(month)-\(pharmacy ?? 0)") { await load() }
            .refreshable { await load() }
            .sheet(item: $shared) { ShareSheet(items: [$0.url]) }
        }
    }

    private func groups(_ b: Billing) -> [(String, [BillingLine])] {
        Dictionary(grouping: b.lines, by: \.pharmacy).sorted { $0.key.localizedCompare($1.key) == .orderedAscending }.map { ($0.key, $0.value) }
    }

    private func shift(_ n: Int) {
        guard let d = Fmt.day(month + "-01"), let r = Fmt.calendar.date(byAdding: .month, value: n, to: d) else { return }
        month = Fmt.month(r)
    }

    private func load() async {
        loading = true
        billing = await model.billing(month: month, pharmacy: pharmacy)
        loading = false
    }
}
