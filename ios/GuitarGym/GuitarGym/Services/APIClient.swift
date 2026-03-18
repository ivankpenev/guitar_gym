import Foundation

/// Central API client for communicating with the Guitar Gym backend.
class APIClient {
    static let shared = APIClient()

    // Change this to your server URL
    private let baseURL = "http://localhost:8000"
    private var token: String?

    func setToken(_ token: String) {
        self.token = token
    }

    func clearToken() {
        self.token = nil
    }

    // MARK: - Generic request

    func request<T: Decodable>(
        _ method: String,
        path: String,
        body: Encodable? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let errorBody = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(statusCode: httpResponse.statusCode, message: errorBody)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    func get<T: Decodable>(path: String) async throws -> T {
        try await request("GET", path: path)
    }

    func post<T: Decodable>(path: String, body: Encodable? = nil) async throws -> T {
        try await request("POST", path: path, body: body)
    }
}

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case serverError(statusCode: Int, message: String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidResponse: return "Invalid response from server"
        case .serverError(let code, let msg): return "Server error \(code): \(msg)"
        }
    }
}
