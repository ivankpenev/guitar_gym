import Foundation
import SwiftUI

@MainActor
class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: UserResponse?
    @Published var errorMessage: String?
    @Published var isLoading = false

    private let api = APIClient.shared

    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            // OAuth2 form login uses form-encoded body
            let token: TokenResponse = try await loginWithForm(username: username, password: password)
            api.setToken(token.accessToken)
            let user: UserResponse = try await api.get(path: "/auth/me")
            currentUser = user
            isAuthenticated = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func register(email: String, username: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let body = RegisterRequest(email: email, username: username, password: password)
            let _: UserResponse = try await api.post(path: "/auth/register", body: body)
            // Auto-login after register
            await login(username: username, password: password)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func logout() {
        api.clearToken()
        isAuthenticated = false
        currentUser = nil
    }

    /// Login uses OAuth2 form-encoded format
    private func loginWithForm(username: String, password: String) async throws -> TokenResponse {
        guard let url = URL(string: "http://localhost:8000/auth/login") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let formBody = "username=\(username)&password=\(password)"
        request.httpBody = formBody.data(using: .utf8)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError(statusCode: 401, message: "Login failed")
        }

        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
}
