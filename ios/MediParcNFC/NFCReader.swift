import CoreNFC
import Foundation

enum NFCScanResult {
    case tag(String)   // identifiant de la puce, ex. 04:A2:3B:91:7C:5E:80
    case unavailable   // simulateur ou appareil sans NFC
    case cancelled
}

/// Lit l'identifiant unique (UID) d'une puce NFC avec Core NFC.
final class NFCReader: NSObject, NFCTagReaderSessionDelegate {
    private var session: NFCTagReaderSession?
    private var completion: ((NFCScanResult) -> Void)?

    func scan(completion: @escaping (NFCScanResult) -> Void) {
        guard NFCTagReaderSession.readingAvailable,
              let session = NFCTagReaderSession(pollingOption: [.iso14443, .iso15693],
                                                delegate: self, queue: nil)
        else {
            completion(.unavailable)
            return
        }
        self.completion = completion
        self.session = session
        session.alertMessage = "Approchez le haut de l'iPhone de la puce collée sur l'équipement."
        session.begin()
    }

    func tagReaderSessionDidBecomeActive(_ session: NFCTagReaderSession) {}

    func tagReaderSession(_ session: NFCTagReaderSession, didInvalidateWithError error: Error) {
        finish(.cancelled)
    }

    func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
        guard let tag = tags.first else { return }
        let identifier: Data
        switch tag {
        case .miFare(let t): identifier = t.identifier
        case .iso7816(let t): identifier = t.identifier
        case .iso15693(let t): identifier = t.identifier
        case .feliCa(let t): identifier = t.currentIDm
        @unknown default:
            session.invalidate(errorMessage: "Puce non prise en charge.")
            return
        }
        let uid = identifier.map { String(format: "%02X", $0) }.joined(separator: ":")
        session.alertMessage = "Puce lue"
        session.invalidate()
        finish(.tag(uid))
    }

    private func finish(_ result: NFCScanResult) {
        let callback = completion
        completion = nil
        session = nil
        callback?(result)
    }
}
