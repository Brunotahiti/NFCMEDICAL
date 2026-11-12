import MapKit
import SwiftUI
import WebKit

/// Affiche l'interface (dossier Web) et relie le bouton de scan à Core NFC.
struct WebAppView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.setURLSchemeHandler(BundleSchemeHandler(), forURLScheme: "mediparc")
        config.userContentController.add(context.coordinator, name: "nfc")
        config.userContentController.add(context.coordinator, name: "map")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.bounces = false
        webView.scrollView.isScrollEnabled = false
        webView.allowsLinkPreview = false
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        context.coordinator.webView = webView

        if let url = URL(string: "mediparc://app/index.html") {
            webView.load(URLRequest(url: url))
        }
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate, WKUIDelegate {
        weak var webView: WKWebView?
        private let reader = NFCReader()

        func userContentController(_ userContentController: WKUserContentController,
                                   didReceive message: WKScriptMessage) {
            let body = message.body as? [String: Any] ?? [:]
            switch message.name {
            case "nfc": handleNFC(body)
            case "map": showMap(body)
            default: break
            }
        }

        /// {action: "read"} lit le lien d'une puce ; {action: "write", url: "…"} écrit un lien.
        private func handleNFC(_ body: [String: Any]) {
            var mode = NFCMode.read
            if body["action"] as? String == "write" {
                guard let text = body["url"] as? String, let url = URL(string: text) else {
                    run("window.onNfcError(\(literal("Lien invalide.")))")
                    return
                }
                mode = .write(url)
            }
            reader.start(mode) { [weak self] result in
                DispatchQueue.main.async {
                    guard let self else { return }
                    switch result {
                    case .link(let url):
                        self.run("window.onNfcLink(\(self.literal(url)))")
                    case .written(let url):
                        self.run("window.onNfcWritten(\(self.literal(url)))")
                    case .failed(let message):
                        self.run("window.onNfcError(\(self.literal(message)))")
                    case .unavailable:
                        self.run("window.onNfcUnavailable()")
                    case .cancelled:
                        self.run("window.onNfcCancelled()")
                    }
                }
            }
        }

        /// {focus: "id", pins: [{id, title, subtitle, lat, lon}]} ouvre la carte Apple Plans.
        private func showMap(_ body: [String: Any]) {
            let rows = body["pins"] as? [[String: Any]] ?? []
            let pins: [MapPin] = rows.compactMap { row in
                guard let id = row["id"] as? String,
                      let lat = (row["lat"] as? NSNumber)?.doubleValue,
                      let lon = (row["lon"] as? NSNumber)?.doubleValue else { return nil }
                return MapPin(id: id,
                              title: row["title"] as? String ?? "",
                              subtitle: row["subtitle"] as? String ?? "",
                              coordinate: CLLocationCoordinate2D(latitude: lat, longitude: lon))
            }
            guard !pins.isEmpty, let root = webView?.window?.rootViewController else { return }
            let host = UIHostingController(rootView: MapScreen(pins: pins, focus: body["focus"] as? String))
            host.modalPresentationStyle = .fullScreen
            root.present(host, animated: true)
        }

        /// Encode un texte en littéral JavaScript sûr (ou null).
        private func literal(_ text: String?) -> String {
            guard let text,
                  let data = try? JSONSerialization.data(withJSONObject: [text]),
                  let json = String(data: data, encoding: .utf8) else { return "null" }
            return String(json.dropFirst().dropLast())
        }

        /// Les liens externes (ex. « Plans ») s'ouvrent hors de l'app.
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if navigationAction.navigationType == .linkActivated,
               let url = navigationAction.request.url, url.scheme != "mediparc" {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                     for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            if let url = navigationAction.request.url {
                UIApplication.shared.open(url)
            }
            return nil
        }

        private func run(_ script: String) {
            webView?.evaluateJavaScript(script, completionHandler: nil)
        }
    }
}

/// Sert les fichiers du dossier Web embarqué dans l'app (mediparc://app/…).
final class BundleSchemeHandler: NSObject, WKURLSchemeHandler {
    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url,
              let fileURL = resolve(url.path),
              let data = try? Data(contentsOf: fileURL),
              let response = HTTPURLResponse(
                url: url, statusCode: 200, httpVersion: "HTTP/1.1",
                headerFields: ["Content-Type": mimeType(for: fileURL.pathExtension),
                               "Content-Length": String(data.count)])
        else {
            urlSchemeTask.didFailWithError(URLError(.fileDoesNotExist))
            return
        }
        urlSchemeTask.didReceive(response)
        urlSchemeTask.didReceive(data)
        urlSchemeTask.didFinish()
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    /// Xcode peut copier les ressources avec ou sans leurs sous-dossiers : on essaie les deux.
    private func resolve(_ path: String) -> URL? {
        let relative = path.hasPrefix("/") ? String(path.dropFirst()) : path
        guard !relative.isEmpty, !relative.contains("..") else { return nil }
        let base = Bundle.main.bundleURL
        let fileName = (relative as NSString).lastPathComponent
        let candidates = [
            base.appendingPathComponent("Web").appendingPathComponent(relative),
            base.appendingPathComponent(relative),
            base.appendingPathComponent(fileName)
        ]
        return candidates.first { FileManager.default.fileExists(atPath: $0.path) }
    }

    private func mimeType(for ext: String) -> String {
        switch ext.lowercased() {
        case "html": return "text/html; charset=utf-8"
        case "jpg", "jpeg": return "image/jpeg"
        case "png": return "image/png"
        case "css": return "text/css; charset=utf-8"
        case "js": return "text/javascript; charset=utf-8"
        default: return "application/octet-stream"
        }
    }
}
