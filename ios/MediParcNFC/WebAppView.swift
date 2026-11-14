import MapKit
import SwiftUI
import WebKit

/// Adresse de l'application partagée (comptes, base de données, ordonnances, facturation).
let siteURL = URL(string: "https://manaprocess.cloud/materiel/")!

/// Affiche l'application en ligne et relie la lecture NFC et les cartes aux fonctions natives de l'iPhone.
/// Sans connexion au démarrage, la version de démonstration embarquée (dossier Web) s'affiche.
struct WebAppView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        config.setURLSchemeHandler(BundleSchemeHandler(), forURLScheme: "mediparc")
        config.userContentController.add(context.coordinator, name: "nfc")
        config.userContentController.add(context.coordinator, name: "map")
        config.userContentController.add(context.coordinator, name: "save")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.scrollView.bounces = false
        webView.scrollView.isScrollEnabled = false
        webView.allowsLinkPreview = false
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        context.coordinator.webView = webView
        webView.load(URLRequest(url: siteURL, cachePolicy: .reloadRevalidatingCacheData, timeoutInterval: 20))
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate, WKUIDelegate, WKDownloadDelegate {
        weak var webView: WKWebView?
        private let reader = NFCReader()
        private var usingFallback = false
        private var downloads: [WKDownload: URL] = [:]

        // MARK: Messages de la page

        func userContentController(_ userContentController: WKUserContentController,
                                   didReceive message: WKScriptMessage) {
            let body = message.body as? [String: Any] ?? [:]
            switch message.name {
            case "nfc": handleNFC(body)
            case "map": showMap(body)
            case "save": saveFile(body)
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
            guard !pins.isEmpty, let root = topController() else { return }
            let host = UIHostingController(rootView: MapScreen(pins: pins, focus: body["focus"] as? String))
            host.modalPresentationStyle = .fullScreen
            root.present(host, animated: true)
        }

        /// {name, mime, data (base64)} : ordonnance scannée, proposée à « Enregistrer dans Fichiers »
        /// (serveur de la pharmacie connecté dans l'app Fichiers). Le fichier n'est pas envoyé à MédiParc.
        private func saveFile(_ body: [String: Any]) {
            guard let b64 = body["data"] as? String, let data = Data(base64Encoded: b64),
                  let root = topController() else { return }
            let raw = (body["name"] as? String) ?? "ordonnance.pdf"
            let name = raw.replacingOccurrences(of: "/", with: "-").replacingOccurrences(of: ":", with: "-")
            let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let url = dir.appendingPathComponent(name)
            do { try data.write(to: url, options: .completeFileProtection) } catch { return }
            let share = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            share.popoverPresentationController?.sourceView = root.view
            share.completionWithItemsHandler = { [weak self] _, completed, _, _ in
                try? FileManager.default.removeItem(at: dir)
                self?.run("window.onNativeSaved(\(completed ? "true" : "false"))")
            }
            root.present(share, animated: true)
        }

        // MARK: Navigation

        private func isOurs(_ url: URL?) -> Bool {
            guard let url else { return false }
            if url.scheme == "mediparc" || url.scheme == "about" || url.scheme == "blob" { return true }
            return url.host == siteURL.host && url.path.hasPrefix("/materiel")
        }

        /// Les liens de l'application restent dans l'app ; les autres (Apple Plans…) s'ouvrent à l'extérieur.
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if let url = navigationAction.request.url, navigationAction.targetFrame?.isMainFrame != false, !isOurs(url) {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }

        /// Les fichiers à télécharger (export de facturation) passent par le menu de partage.
        func webView(_ webView: WKWebView, decidePolicyFor navigationResponse: WKNavigationResponse,
                     decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
            if let http = navigationResponse.response as? HTTPURLResponse,
               let disposition = http.value(forHTTPHeaderField: "Content-Disposition"),
               disposition.lowercased().hasPrefix("attachment") {
                decisionHandler(.download)
                return
            }
            decisionHandler(navigationResponse.canShowMIMEType ? .allow : .download)
        }

        func webView(_ webView: WKWebView, navigationResponse: WKNavigationResponse, didBecome download: WKDownload) {
            download.delegate = self
        }

        func webView(_ webView: WKWebView, navigationAction: WKNavigationAction, didBecome download: WKDownload) {
            download.delegate = self
        }

        func download(_ download: WKDownload, decideDestinationUsing response: URLResponse,
                      suggestedFilename: String, completionHandler: @escaping (URL?) -> Void) {
            let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let url = dir.appendingPathComponent(suggestedFilename)
            downloads[download] = url
            completionHandler(url)
        }

        func downloadDidFinish(_ download: WKDownload) {
            guard let url = downloads.removeValue(forKey: download), let root = topController() else { return }
            let share = UIActivityViewController(activityItems: [url], applicationActivities: nil)
            share.popoverPresentationController?.sourceView = root.view
            root.present(share, animated: true)
        }

        func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
            downloads.removeValue(forKey: download)
            run("window.toast && toast(\(literal("Téléchargement impossible.")))")
        }

        /// Les documents ouverts dans un nouvel onglet (ordonnances) s'affichent dans une fenêtre de l'app,
        /// avec la même session de connexion.
        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                     for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            guard let url = navigationAction.request.url else { return nil }
            if !isOurs(url) {
                UIApplication.shared.open(url)
                return nil
            }
            let viewer = DocumentViewController(configuration: configuration, delegate: self)
            topController()?.present(UINavigationController(rootViewController: viewer), animated: true)
            return viewer.webView
        }

        /// Hors connexion au démarrage : version de démonstration embarquée.
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            guard !usingFallback, let local = URL(string: "mediparc://app/index.html") else { return }
            usingFallback = true
            webView.load(URLRequest(url: local))
        }

        func webView(_ webView: WKWebView, requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                     initiatedByFrame frame: WKFrameInfo, type: WKMediaCaptureType,
                     decisionHandler: @escaping (WKPermissionDecision) -> Void) {
            decisionHandler(.prompt)
        }

        // MARK: Outils

        private func topController() -> UIViewController? {
            var top = webView?.window?.rootViewController
            while let next = top?.presentedViewController { top = next }
            return top
        }

        private func run(_ script: String) {
            webView?.evaluateJavaScript(script, completionHandler: nil)
        }

        /// Encode un texte en littéral JavaScript sûr (ou null).
        private func literal(_ text: String?) -> String {
            guard let text,
                  let data = try? JSONSerialization.data(withJSONObject: [text]),
                  let json = String(data: data, encoding: .utf8) else { return "null" }
            return String(json.dropFirst().dropLast())
        }
    }
}

/// Fenêtre d'affichage d'un document (photo ou PDF d'ordonnance), avec bouton Fermer et partage.
final class DocumentViewController: UIViewController {
    let webView: WKWebView

    init(configuration: WKWebViewConfiguration, delegate: WKNavigationDelegate & WKUIDelegate) {
        webView = WKWebView(frame: .zero, configuration: configuration)
        super.init(nibName: nil, bundle: nil)
        webView.navigationDelegate = delegate
        webView.uiDelegate = delegate
    }

    required init?(coder: NSCoder) { nil }

    override func loadView() { view = webView }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Document"
        navigationItem.leftBarButtonItem = UIBarButtonItem(systemItem: .close, primaryAction: UIAction { [weak self] _ in
            self?.dismiss(animated: true)
        })
    }
}

/// Sert les fichiers du dossier Web embarqué dans l'app (mediparc://app/…), utilisé hors connexion.
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
