import CoreNFC
import Foundation

/// Lecture et écriture des puces NFC (enregistrement NDEF de type lien).
final class NFCService: NSObject, NFCNDEFReaderSessionDelegate {
    static let shared = NFCService()

    static var isAvailable: Bool { NFCNDEFReaderSession.readingAvailable }

    private enum Mode { case read, write(URL) }
    private var mode: Mode = .read
    private var session: NFCNDEFReaderSession?
    private var continuation: CheckedContinuation<String, Error>?

    struct NFCError: LocalizedError {
        let message: String
        var errorDescription: String? { message }
    }

    /// Lit une puce et renvoie son contenu (lien ou texte).
    @MainActor
    func read() async throws -> String {
        try await begin(.read, prompt: "Approchez le haut de l'iPhone de l'étiquette NFC du matériel.")
    }

    /// Écrit le lien dans la puce (la puce doit être réinscriptible).
    @MainActor
    func write(_ url: URL) async throws {
        _ = try await begin(.write(url), prompt: "Approchez l'iPhone de la puce à programmer.")
    }

    @MainActor
    private func begin(_ mode: Mode, prompt: String) async throws -> String {
        guard Self.isAvailable else { throw NFCError(message: "La lecture NFC n'est pas disponible sur cet appareil.") }
        continuation?.resume(throwing: CancellationError())
        self.mode = mode
        return try await withCheckedThrowingContinuation { cont in
            continuation = cont
            let s = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: false)
            s.alertMessage = prompt
            session = s
            s.begin()
        }
    }

    private func finish(_ result: Result<String, Error>) {
        let c = continuation
        continuation = nil
        switch result {
        case .success(let v): c?.resume(returning: v)
        case .failure(let e): c?.resume(throwing: e)
        }
    }

    // MARK: NFCNDEFReaderSessionDelegate

    func readerSession(_ session: NFCNDEFReaderSession, didDetectNDEFs messages: [NFCNDEFMessage]) {}

    func readerSession(_ session: NFCNDEFReaderSession, didDetect tags: [NFCNDEFTag]) {
        guard tags.count == 1, let tag = tags.first else {
            session.alertMessage = "Plusieurs puces détectées : n'en approchez qu'une seule."
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { session.restartPolling() }
            return
        }
        session.connect(to: tag) { error in
            if let error { return self.fail(session, "Connexion à la puce impossible : \(error.localizedDescription)") }
            tag.queryNDEFStatus { status, capacity, error in
                if let error { return self.fail(session, error.localizedDescription) }
                switch self.mode {
                case .read:
                    guard status != .notSupported else { return self.fail(session, "Cette puce n'est pas au format NDEF.") }
                    tag.readNDEF { message, error in
                        guard error == nil, let record = message?.records.first else { return self.fail(session, "Puce vide ou illisible.") }
                        let text = record.wellKnownTypeURIPayload()?.absoluteString
                            ?? record.wellKnownTypeTextPayload().0
                            ?? String(data: record.payload, encoding: .utf8)
                        guard let text, !text.isEmpty else { return self.fail(session, "Contenu de la puce non reconnu.") }
                        session.alertMessage = "Puce lue."
                        session.invalidate()
                        self.finish(.success(text))
                    }
                case .write(let url):
                    guard status == .readWrite else {
                        return self.fail(session, status == .readOnly ? "Cette puce est verrouillée en lecture seule." : "Cette puce n'accepte pas l'écriture.")
                    }
                    guard let payload = NFCNDEFPayload.wellKnownTypeURIPayload(url: url) else { return self.fail(session, "Lien invalide.") }
                    let message = NFCNDEFMessage(records: [payload])
                    guard message.length <= capacity else { return self.fail(session, "Puce trop petite pour ce lien.") }
                    tag.writeNDEF(message) { error in
                        if let error { return self.fail(session, "Écriture impossible : \(error.localizedDescription)") }
                        session.alertMessage = "Puce programmée."
                        session.invalidate()
                        self.finish(.success(url.absoluteString))
                    }
                }
            }
        }
    }

    func readerSession(_ session: NFCNDEFReaderSession, didInvalidateWithError error: Error) {
        guard continuation != nil else { return }
        let code = (error as? NFCReaderError)?.code
        if code == .readerSessionInvalidationErrorUserCanceled || code == .readerSessionInvalidationErrorFirstNDEFTagRead {
            finish(.failure(CancellationError()))
        } else {
            finish(.failure(NFCError(message: error.localizedDescription)))
        }
    }

    private func fail(_ session: NFCNDEFReaderSession, _ message: String) {
        session.invalidate(errorMessage: message)
        finish(.failure(NFCError(message: message)))
    }
}
