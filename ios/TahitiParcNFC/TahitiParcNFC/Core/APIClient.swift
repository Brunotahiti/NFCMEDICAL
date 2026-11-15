import Foundation

/// Adresse du serveur Tahiti Parc NFC.
enum Server {
    static let site = "https://manaprocess.cloud/materiel/"
    static let api = site + "api/"
    static func photo(_ name: String) -> URL? { URL(string: site + "photos/" + name + ".jpg") }
    static func userPhoto(_ id: Int) -> URL? { URL(string: api + "photos/\(id)") }
}

struct APIError: LocalizedError {
    let status: Int
    let message: String
    var errorDescription: String? { message }
}

/// Client HTTP : session par cookie (partagée avec les images), réponses JSON.
final class APIClient {
    static let shared = APIClient()

    let session: URLSession
    let decoder: JSONDecoder

    private init() {
        let config = URLSessionConfiguration.default
        config.httpCookieStorage = .shared
        config.httpCookieAcceptPolicy = .always
        config.httpShouldSetCookies = true
        config.timeoutIntervalForRequest = 30
        session = URLSession(configuration: config)
        decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
    }

    func url(_ path: String) -> URL {
        URL(string: Server.api + path)!
    }

    func get<T: Decodable>(_ path: String, as type: T.Type = T.self) async throws -> T {
        try decoder.decode(T.self, from: try await send("GET", path))
    }

    @discardableResult
    func post(_ path: String, _ body: [String: Any] = [:]) async throws -> Data {
        try await send("POST", path, json: body)
    }

    func post<T: Decodable>(_ path: String, _ body: [String: Any] = [:], as type: T.Type) async throws -> T {
        try decoder.decode(T.self, from: try await send("POST", path, json: body))
    }

    func send(_ method: String, _ path: String, json: [String: Any]? = nil) async throws -> Data {
        var request = URLRequest(url: url(path))
        request.httpMethod = method
        if let json {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: json)
        }
        return try await perform(request)
    }

    /// Envoi d'un fichier brut (photo du matériel).
    @discardableResult
    func upload(_ path: String, data: Data, contentType: String, headers: [String: String]) async throws -> Data {
        var request = URLRequest(url: url(path))
        request.httpMethod = "POST"
        request.setValue(contentType, forHTTPHeaderField: "Content-Type")
        request.setValue("1", forHTTPHeaderField: "X-Mediparc")
        for (k, v) in headers { request.setValue(v, forHTTPHeaderField: k) }
        request.httpBody = data
        return try await perform(request)
    }

    /// Télécharge un fichier dans le dossier temporaire et renvoie son adresse locale.
    func download(_ path: String, filename: String) async throws -> URL {
        let data = try await send("GET", path)
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let file = dir.appendingPathComponent(filename)
        try data.write(to: file, options: .completeFileProtection)
        return file
    }

    private func perform(_ request: URLRequest) async throws -> Data {
        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw APIError(status: 0, message: "Connexion au serveur impossible. Vérifiez le réseau puis réessayez.")
        }
        let code = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(code) else {
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            let message = object?["error"] as? String ?? "Erreur du serveur (\(code))."
            throw APIError(status: code, message: message)
        }
        return data
    }

    func clearSession() {
        HTTPCookieStorage.shared.cookies?.forEach { HTTPCookieStorage.shared.deleteCookie($0) }
    }
}
