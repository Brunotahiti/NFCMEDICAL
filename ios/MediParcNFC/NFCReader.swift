import CoreNFC
import Foundation

enum NFCMode {
    case read          // lire le lien enregistré sur la puce
    case write(URL)    // écrire un lien sur la puce
}

enum NFCResult {
    case link(String?)     // lien lu (nil : puce vierge ou sans lien)
    case written(String)   // lien écrit
    case failed(String)
    case unavailable       // simulateur ou appareil sans NFC
    case cancelled
}

/// Lit ou écrit le lien (enregistrement NDEF de type URI) d'une puce NFC.
final class NFCReader: NSObject, NFCNDEFReaderSessionDelegate {
    private var session: NFCNDEFReaderSession?
    private var mode: NFCMode = .read
    private var completion: ((NFCResult) -> Void)?

    func start(_ mode: NFCMode, completion: @escaping (NFCResult) -> Void) {
        guard NFCNDEFReaderSession.readingAvailable else {
            completion(.unavailable)
            return
        }
        self.mode = mode
        self.completion = completion
        let session = NFCNDEFReaderSession(delegate: self, queue: nil, invalidateAfterFirstRead: false)
        switch mode {
        case .read:
            session.alertMessage = "Approchez le haut de l'iPhone de la puce collée sur l'équipement."
        case .write:
            session.alertMessage = "Approchez le haut de l'iPhone de la puce à programmer."
        }
        self.session = session
        session.begin()
    }

    func readerSessionDidBecomeActive(_ session: NFCNDEFReaderSession) {}

    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        finish(.cancelled)
    }

    // Requis par le protocole ; non appelé puisque la détection par puce ci-dessous est implémentée.
    func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {}

    func readerSession(_ session: NFCNDEFReaderSession, didDetect tags: [NFCNDEFTag]) {
        guard let tag = tags.first else { return }
        session.connect(to: tag) { [weak self] error in
            guard let self else { return }
            if error != nil {
                self.fail(session, "Connexion à la puce impossible.")
                return
            }
            tag.queryNDEFStatus { status, _, error in
                if error != nil || status == .notSupported {
                    self.fail(session, "Cette puce n'est pas compatible.")
                    return
                }
                switch self.mode {
                case .read:
                    tag.readNDEF { message, _ in
                        let url = message?.records.compactMap { $0.wellKnownTypeURIPayload() }.first
                        session.alertMessage = url == nil ? "Puce sans lien" : "Puce lue"
                        session.invalidate()
                        self.finish(.link(url?.absoluteString))
                    }
                case .write(let url):
                    guard status == .readWrite,
                          let payload = NFCNDEFPayload.wellKnownTypeURIPayload(url: url) else {
                        self.fail(session, "Cette puce est verrouillée en écriture.")
                        return
                    }
                    tag.writeNDEF(NFCNDEFMessage(records: [payload])) { error in
                        if error != nil {
                            self.fail(session, "Écriture impossible, réessayez.")
                            return
                        }
                        session.alertMessage = "Lien écrit sur la puce"
                        session.invalidate()
                        self.finish(.written(url.absoluteString))
                    }
                }
            }
        }
    }

    private func fail(_ session: NFCNDEFReaderSession, _ message: String) {
        session.invalidate(errorMessage: message)
        finish(.failed(message))
    }

    private func finish(_ result: NFCResult) {
        let callback = completion
        completion = nil
        session = nil
        callback?(result)
    }
}
