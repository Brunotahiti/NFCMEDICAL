import SwiftUI
import UIKit

/// Appareil photo du système (ou photothèque sur le simulateur).
struct CameraPicker: UIViewControllerRepresentable {
    var onImage: (UIImage) -> Void
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = UIImagePickerController.isSourceTypeAvailable(.camera) ? .camera : .photoLibrary
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ controller: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraPicker
        init(_ parent: CameraPicker) { self.parent = parent }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage { parent.onImage(image) }
            parent.dismiss()
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { parent.dismiss() }
    }
}

enum PhotoStamp {
    /// Réduit la photo et y incruste un bandeau : référence, date et heure, position.
    static func stamp(_ image: UIImage, ref: String, kind: String, location: LocationFix?, date: Date = Date()) -> Data? {
        let maxSide: CGFloat = 1600
        let scale = min(1, maxSide / max(image.size.width, image.size.height))
        let size = CGSize(width: (image.size.width * scale).rounded(), height: (image.size.height * scale).rounded())
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        let renderer = UIGraphicsImageRenderer(size: size, format: format)
        let stamped = renderer.image { ctx in
            image.draw(in: CGRect(origin: .zero, size: size))
            let band = max(54, size.height * 0.075)
            let rect = CGRect(x: 0, y: size.height - band, width: size.width, height: band)
            UIColor(white: 0, alpha: 0.55).setFill()
            ctx.fill(rect)
            let when = date.formatted(.dateTime.day(.twoDigits).month(.twoDigits).year().hour().minute().locale(Fmt.fr))
            var line = "\(ref) · \(kind) · \(when)"
            if let l = location { line += String(format: " · %.5f, %.5f (±%.0f m)", l.latitude, l.longitude, l.accuracy) }
            let font = UIFont.systemFont(ofSize: band * 0.36, weight: .semibold)
            let attrs: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: UIColor.white]
            let textSize = (line as NSString).size(withAttributes: attrs)
            (line as NSString).draw(at: CGPoint(x: band * 0.3, y: rect.midY - textSize.height / 2), withAttributes: attrs)
        }
        return stamped.jpegData(compressionQuality: 0.82)
    }
}

/// Feuille de partage (PDF, CSV…).
struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }
    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}

/// Adresse locale partageable, utilisable avec `.sheet(item:)`.
struct SharedFile: Identifiable {
    let url: URL
    var id: String { url.path }
}
