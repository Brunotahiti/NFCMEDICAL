import SwiftUI

enum PhotoKind: String, CaseIterable, Identifiable {
    case livraison, retour, etat, panne
    var id: String { rawValue }
    var label: String {
        switch self {
        case .livraison: return "Livraison"
        case .retour: return "Retour"
        case .etat: return "État du matériel"
        case .panne: return "Panne"
        }
    }
}

/// Photo horodatée : bandeau incrusté (référence, date, heure, position) puis envoi au serveur.
struct PhotoCaptureView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let e: Equipment
    init(e: Equipment) { self.e = e }
    @State private var kind: PhotoKind = .etat
    @State private var showCamera = false
    @State private var image: UIImage?
    @State private var stamped: Data?
    @State private var fix: LocationFix?
    @State private var locating = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Type de photo") {
                    Picker("Type", selection: $kind) { ForEach(PhotoKind.allCases) { Text($0.label).tag($0) } }
                        .pickerStyle(.segmented)
                }
                Section {
                    if let stamped, let ui = UIImage(data: stamped) {
                        Image(uiImage: ui).resizable().scaledToFit().clipShape(RoundedRectangle(cornerRadius: 12))
                        Button("Reprendre la photo") { showCamera = true }
                    } else {
                        Button { showCamera = true } label: { Label("Ouvrir l'appareil photo", systemImage: "camera.fill") }
                    }
                } footer: {
                    Text(locating ? "Recherche de la position…" : fix == nil ? "La date et l'heure sont incrustées sur la photo." : "La date, l'heure et la position sont incrustées sur la photo.")
                }
            }
            .navigationTitle("Photo · \(e.ref)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Envoyer") {
                        guard let stamped else { return }
                        Task { if await model.uploadPhoto(e, jpeg: stamped, kind: kind.rawValue, location: fix) { dismiss() } }
                    }
                    .disabled(stamped == nil || model.busy)
                }
            }
            .fullScreenCover(isPresented: $showCamera) {
                CameraPicker { img in
                    image = img
                    Task {
                        locating = true
                        fix = await LocationService.shared.current()
                        locating = false
                        restamp()
                    }
                }
                .ignoresSafeArea()
            }
            .onChange(of: kind) { restamp() }
            .task { if image == nil { showCamera = true } }
        }
    }

    private func restamp() {
        guard let image else { return }
        stamped = PhotoStamp.stamp(image, ref: e.ref, kind: kind.label, location: fix)
    }
}
