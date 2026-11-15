import SwiftUI

/// Scan d'une étiquette NFC : identifie le matériel, enregistre le passage et la position, ouvre sa fiche.
struct ScanView: View {
    @Environment(AppModel.self) private var model
    @State private var path: [EquipmentLink] = []
    @State private var manualRef = ""
    @State private var scanning = false
    @State private var lastResult: String?

    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(spacing: 22) {
                    Button(action: scan) {
                        ZStack {
                            Circle().fill(LinearGradient.tpHero).frame(width: 210, height: 210)
                                .shadow(color: Color.tpHero.opacity(0.35), radius: 24, y: 10)
                            Circle().stroke(Color.tpBrand.opacity(0.35), lineWidth: 10).frame(width: 240, height: 240)
                            VStack(spacing: 10) {
                                Image(systemName: "wave.3.right").font(.system(size: 64, weight: .semibold)).foregroundStyle(Color.tpBrand)
                                Text(scanning ? "Lecture…" : "Scanner une puce").font(.headline).foregroundStyle(.white)
                            }
                        }
                    }
                    .buttonStyle(.plain)
                    .disabled(scanning || !NFCService.isAvailable)
                    .padding(.top, 30)

                    Text(NFCService.isAvailable
                         ? "Approchez le haut de l'iPhone de l'étiquette du matériel. Le passage est enregistré avec votre position."
                         : "La lecture NFC n'est pas disponible sur cet appareil. Saisissez la référence ci-dessous.")
                        .font(.subheadline).foregroundStyle(Color.tpMuted).multilineTextAlignment(.center)
                        .padding(.horizontal, 24)

                    if let lastResult {
                        Text(lastResult).font(.footnote.weight(.semibold)).foregroundStyle(Color.tpCrit)
                    }

                    Card {
                        Text("Saisie manuelle").font(.headline)
                        HStack {
                            TextField("Référence (ex. LIT-0001)", text: $manualRef)
                                .textInputAutocapitalization(.characters)
                                .autocorrectionDisabled()
                                .submitLabel(.go)
                                .onSubmit(manual)
                            Button("Ouvrir", action: manual).buttonStyle(.borderedProminent).disabled(manualRef.isEmpty)
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .frame(maxWidth: .infinity)
            }
            .background(Color.tpBackground)
            .navigationTitle("Scanner")
            .navigationBarTitleDisplayMode(.inline)
            .navigationDestination(for: EquipmentLink.self) { EquipmentDetailView(id: $0.id) }
            .onOpenURL { url in open(text: url.absoluteString, source: "lien") }
        }
    }

    private func scan() {
        Task {
            scanning = true
            defer { scanning = false }
            do {
                let text = try await NFCService.shared.read()
                open(text: text, source: "nfc")
            } catch is CancellationError {
            } catch {
                lastResult = error.localizedDescription
            }
        }
    }

    private func manual() {
        open(text: manualRef, source: "saisie")
        manualRef = ""
    }

    private func open(text: String, source: String) {
        guard let e = model.equipment(fromTag: text) else {
            lastResult = "Aucun équipement de votre parc ne correspond à « \(text) »."
            return
        }
        lastResult = nil
        path = [EquipmentLink(id: e.id)]
        Task {
            let fix = await LocationService.shared.current()
            await model.recordScan(e, source: source, location: fix)
        }
    }
}
