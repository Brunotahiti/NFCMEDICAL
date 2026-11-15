import SwiftUI

struct ParcView: View {
    var body: some View {
        NavigationStack {
            EquipmentListView(filter: nil)
                .navigationDestination(for: EquipmentLink.self) { EquipmentDetailView(id: $0.id) }
        }
    }
}

/// Liste filtrable du matériel (par état, par recherche).
struct EquipmentListView: View {
    @Environment(AppModel.self) private var model
    @State private var filter: EquipmentState?
    init(filter: EquipmentState?) { _filter = State(initialValue: filter) }
    @State private var search = ""
    @State private var kind = "Tous"

    private var kinds: [String] { ["Tous"] + Array(Set(model.equipment.map(\.kind))).sorted() }

    private var items: [Equipment] {
        model.equipment.filter { e in
            (filter == nil || e.state == filter) &&
            (kind == "Tous" || e.kind == kind) &&
            (search.isEmpty || [e.ref, e.name, e.brand, model.patient(e.patientId)?.name ?? "", model.pharmacy(e.pharmacyId)?.name ?? ""]
                .contains { $0.localizedCaseInsensitiveContains(search) })
        }
    }

    var body: some View {
        List {
            Section {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        chip("Tout", count: model.equipment.count, selected: filter == nil) { filter = nil }
                        ForEach(EquipmentState.allCases) { s in
                            chip(s.label, count: model.count(s), selected: filter == s, color: s.color) { filter = s }
                        }
                    }
                    .padding(.vertical, 4)
                }
                .listRowInsets(EdgeInsets(top: 0, leading: 16, bottom: 0, trailing: 16))
                .listRowBackground(Color.clear)
            }
            Section("\(items.count) équipement\(items.count > 1 ? "s" : "")") {
                ForEach(items.prefix(400)) { e in
                    NavigationLink(value: EquipmentLink(id: e.id)) { EquipmentRow(e: e) }
                }
                if items.count > 400 {
                    Text("Affinez la recherche pour voir les \(items.count - 400) autres.").font(.footnote).foregroundStyle(.secondary)
                }
            }
        }
        .searchable(text: $search, prompt: "Référence, bénéficiaire, pharmacie…")
        .navigationTitle(filter?.label ?? "Parc")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Picker("Type", selection: $kind) { ForEach(kinds, id: \.self) { Text($0) } }
                } label: { Image(systemName: "line.3.horizontal.decrease.circle") }
            }
        }
        .refreshable { await model.refresh() }
    }

    private func chip(_ title: String, count: Int, selected: Bool, color: Color = .tpAccent, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text("\(title) \(count)")
                .font(.subheadline.weight(.semibold))
                .padding(.horizontal, 12).padding(.vertical, 7)
                .foregroundStyle(selected ? .white : color)
                .background(selected ? color : color.opacity(0.12), in: Capsule())
        }
        .buttonStyle(.plain)
    }
}

struct EquipmentRow: View {
    @Environment(AppModel.self) private var model
    let e: Equipment

    var body: some View {
        HStack(spacing: 12) {
            EquipmentThumb(photo: e.photo, size: 52)
            VStack(alignment: .leading, spacing: 3) {
                Text(e.name).font(.subheadline.weight(.semibold)).lineLimit(1)
                Text(e.ref + " · " + e.brand).font(.caption).foregroundStyle(.secondary).lineLimit(1)
                if e.state == .loc, let p = model.patient(e.patientId) {
                    Text(p.name + (model.pharmacy(e.pharmacyId).map { " · " + $0.name } ?? ""))
                        .font(.caption).foregroundStyle(Color.tpInfo).lineLimit(1)
                }
            }
            Spacer(minLength: 4)
            VStack(alignment: .trailing, spacing: 4) {
                StatusBadge(state: e.state)
                if e.state == .loc, let d = model.daysLeft(e) {
                    Text(d < 0 ? "Retard \(Fmt.duration(-d))" : "J-\(d)")
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(d < 0 ? Color.tpCrit : d <= 3 ? Color.tpWarn : Color.secondary)
                }
            }
        }
        .padding(.vertical, 2)
    }
}
