import PDFKit
import QuickLook
import SwiftUI
import UniformTypeIdentifiers
import VisionKit

/// Ordonnance : seule la vérification (date, validité, n° interne) est enregistrée en ligne.
struct PrescriptionCard: View {
    @Environment(AppModel.self) private var model
    let e: Equipment
    var onVerify: () -> Void
    var onFile: () -> Void

    var body: some View {
        Card {
            Label("Ordonnance", systemImage: "doc.text.magnifyingglass").font(.headline)
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: "lock.shield.fill").foregroundStyle(Color.tpAccent)
                Text("Aucune ordonnance n'est stockée en ligne. Les ordonnances restent sur le serveur de votre pharmacie : l'application les y enregistre et les y relit.")
                    .font(.caption)
            }
            .padding(10)
            .background(Color.tpAccent.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))

            if let p = e.prescription {
                let left = model.prescriptionDaysLeft(e)
                HStack {
                    Image(systemName: "checkmark.seal.fill").foregroundStyle(Color.tpOK)
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Vérifiée par \(p.by) le \(Fmt.date(p.at))").font(.subheadline.weight(.semibold))
                        Text("Ordonnance du \(Fmt.date(p.date))" + (p.valid.map { ", valable jusqu'au \(Fmt.date($0))" } ?? "") + (p.ref.isEmpty ? "" : " · n° \(p.ref)"))
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }
                if let left, left <= 15 {
                    Label(left < 0 ? "Ordonnance expirée : demandez une nouvelle ordonnance." : "Renouvellement à prévoir : valable encore \(Fmt.duration(left)).", systemImage: "bell.badge")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(left < 0 ? Color.tpCrit : Color.tpWarn)
                }
                if let end = e.plannedEnd, let v = p.valid, end > v {
                    Label("La location dépasse la validité de l'ordonnance (fin prévue le \(Fmt.date(end))).", systemImage: "exclamationmark.triangle")
                        .font(.caption).foregroundStyle(Color.tpWarn)
                }
            } else {
                Label("Ordonnance non vérifiée", systemImage: "exclamationmark.circle").foregroundStyle(Color.tpWarn).font(.subheadline.weight(.semibold))
            }
            HStack(spacing: 10) {
                Button(action: onFile) { Label("Scanner / voir", systemImage: "doc.viewfinder").frame(maxWidth: .infinity) }
                    .buttonStyle(.bordered)
                Button(action: onVerify) { Label(e.prescription == nil ? "Confirmer" : "Nouvelle", systemImage: "checkmark").frame(maxWidth: .infinity) }
                    .buttonStyle(.borderedProminent)
            }
            if e.prescription != nil {
                Button("Annuler la vérification", role: .destructive) { Task { await model.cancelPrescription(e) } }.font(.caption)
            }
        }
    }
}

struct PrescriptionSheet: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let e: Equipment
    init(e: Equipment) { self.e = e }
    @State private var date = Date()
    @State private var validUntil = Calendar.current.date(byAdding: .month, value: 3, to: Date())!
    @State private var ref = ""
    @State private var attest = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    DatePicker("Date de l'ordonnance", selection: $date, in: ...Date(), displayedComponents: .date)
                    DatePicker("Valable jusqu'au", selection: $validUntil, in: date..., displayedComponents: .date)
                    HStack {
                        ForEach([1, 3, 6, 12], id: \.self) { m in
                            Button("\(m) mois") { validUntil = Calendar.current.date(byAdding: .month, value: m, to: date)! }
                                .buttonStyle(.bordered).font(.caption)
                        }
                    }
                } footer: { Text("Raccourcis : durée de validité à partir de la date de l'ordonnance.") }
                Section {
                    TextField("N° interne (facultatif)", text: $ref).textInputAutocapitalization(.characters)
                } footer: { Text("Le numéro de classement dans votre pharmacie. N'inscrivez aucune information médicale.") }
                Section {
                    Toggle("La pharmacie détient l'ordonnance originale", isOn: $attest)
                } footer: {
                    Text("Seules la date, la validité et le numéro interne sont enregistrés. Ni l'ordonnance, ni la pathologie, ni le prescripteur ne sont stockés en ligne.")
                }
            }
            .navigationTitle("Vérifier l'ordonnance")
            .navigationBarTitleDisplayMode(.inline)
            .onChange(of: date) { if validUntil < date { validUntil = date } }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Enregistrer") {
                        Task {
                            if await model.verifyPrescription(e, date: Fmt.iso(date), validUntil: Fmt.iso(validUntil), ref: ref.trimmingCharacters(in: .whitespaces)) { dismiss() }
                        }
                    }
                    .disabled(!attest || model.busy)
                }
            }
        }
    }
}

/// Scan ou import de l'ordonnance vers le dossier de la pharmacie (app Fichiers : serveur SMB, NAS…),
/// et relecture depuis ce dossier. Rien n'est envoyé au serveur Tahiti Parc.
struct PrescriptionFileView: View {
    @Environment(\.dismiss) private var dismiss
    let e: Equipment
    init(e: Equipment) { self.e = e }
    @State private var scanning = false
    @State private var picking = false
    @State private var pickForViewing = false
    @State private var document: PDFFile?
    @State private var exporting = false
    @State private var previewURL: URL?
    @State private var message: String?

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Label("Le fichier est enregistré uniquement dans le dossier de votre pharmacie que vous choisissez (serveur local, NAS, dossier partagé). Il n'est jamais envoyé en ligne.", systemImage: "lock.shield")
                        .font(.footnote)
                }
                Section("Enregistrer une ordonnance") {
                    Button { scanning = true } label: { Label("Scanner l'ordonnance", systemImage: "doc.viewfinder") }
                        .disabled(!VNDocumentCameraViewController.isSupported)
                    Button { pickForViewing = false; picking = true } label: { Label("Importer un fichier (photo, PDF, HEIC…)", systemImage: "square.and.arrow.down") }
                }
                Section("Consulter") {
                    Button { pickForViewing = true; picking = true } label: { Label("Voir l'ordonnance sur le serveur de la pharmacie", systemImage: "folder") }
                }
                if let message { Section { Text(message).font(.footnote).foregroundStyle(Color.tpOK) } }
            }
            .navigationTitle("Ordonnance · \(e.ref)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Fermer") { dismiss() } } }
            .fullScreenCover(isPresented: $scanning) {
                DocumentScanner { pages in
                    scanning = false
                    if let data = PDFFile.make(from: pages) { document = PDFFile(data: data); DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { exporting = true } }
                } onCancel: { scanning = false }
                .ignoresSafeArea()
            }
            .fileImporter(isPresented: $picking, allowedContentTypes: [.image, .pdf]) { result in
                guard case .success(let url) = result else { return }
                let access = url.startAccessingSecurityScopedResource()
                defer { if access { url.stopAccessingSecurityScopedResource() } }
                if pickForViewing {
                    let copy = FileManager.default.temporaryDirectory.appendingPathComponent(url.lastPathComponent)
                    try? FileManager.default.removeItem(at: copy)
                    if (try? FileManager.default.copyItem(at: url, to: copy)) != nil { previewURL = copy }
                    return
                }
                guard let data = try? Data(contentsOf: url) else { return }
                if UTType(filenameExtension: url.pathExtension)?.conforms(to: .pdf) == true {
                    document = PDFFile(data: data)
                } else if let img = UIImage(data: data), let pdf = PDFFile.make(from: [img]) {
                    document = PDFFile(data: pdf)
                }
                if document != nil { DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { exporting = true } }
            }
            .fileExporter(isPresented: $exporting, document: document, contentType: .pdf, defaultFilename: fileName) { result in
                if case .success = result { message = "Ordonnance enregistrée dans le dossier de la pharmacie." }
                document = nil
            }
            .quickLookPreview($previewURL)
        }
    }

    private var fileName: String { "Ordonnance-\(e.ref)-\(Fmt.iso(Date()))" }
}

struct PDFFile: FileDocument {
    static var readableContentTypes: [UTType] { [.pdf] }
    var data: Data
    init(data: Data) { self.data = data }
    init(configuration: ReadConfiguration) throws { data = configuration.file.regularFileContents ?? Data() }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { FileWrapper(regularFileWithContents: data) }

    static func make(from images: [UIImage]) -> Data? {
        let pdf = PDFDocument()
        for (i, img) in images.enumerated() {
            if let page = PDFPage(image: img) { pdf.insert(page, at: i) }
        }
        return pdf.pageCount > 0 ? pdf.dataRepresentation() : nil
    }
}

struct DocumentScanner: UIViewControllerRepresentable {
    var onScan: ([UIImage]) -> Void
    var onCancel: () -> Void

    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let vc = VNDocumentCameraViewController()
        vc.delegate = context.coordinator
        return vc
    }
    func updateUIViewController(_ vc: VNDocumentCameraViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(self) }

    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let parent: DocumentScanner
        init(_ parent: DocumentScanner) { self.parent = parent }
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            parent.onScan((0..<scan.pageCount).map { scan.imageOfPage(at: $0) })
        }
        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) { parent.onCancel() }
        func documentCameraViewController(_ controller: VNDocumentCameraViewController, didFailWithError error: Error) { parent.onCancel() }
    }
}
