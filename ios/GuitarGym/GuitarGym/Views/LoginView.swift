import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authVM: AuthViewModel
    @State private var username = ""
    @State private var password = ""
    @State private var email = ""
    @State private var isRegistering = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "guitars")
                        .font(.system(size: 60))
                        .foregroundStyle(.blue)
                    Text("Guitar Gym")
                        .font(.largeTitle.bold())
                    Text("Master your fretboard")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.top, 40)

                // Form
                VStack(spacing: 16) {
                    if isRegistering {
                        TextField("Email", text: $email)
                            .textContentType(.emailAddress)
                            .keyboardType(.emailAddress)
                            .autocapitalization(.none)
                            .textFieldStyle(.roundedBorder)
                    }

                    TextField("Username", text: $username)
                        .textContentType(.username)
                        .autocapitalization(.none)
                        .textFieldStyle(.roundedBorder)

                    SecureField("Password", text: $password)
                        .textContentType(.password)
                        .textFieldStyle(.roundedBorder)
                }
                .padding(.horizontal)

                // Error
                if let error = authVM.errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.caption)
                }

                // Buttons
                Button {
                    Task {
                        if isRegistering {
                            await authVM.register(email: email, username: username, password: password)
                        } else {
                            await authVM.login(username: username, password: password)
                        }
                    }
                } label: {
                    if authVM.isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text(isRegistering ? "Create Account" : "Log In")
                            .frame(maxWidth: .infinity)
                    }
                }
                .buttonStyle(.borderedProminent)
                .padding(.horizontal)
                .disabled(authVM.isLoading)

                Button(isRegistering ? "Already have an account? Log in" : "Don't have an account? Register") {
                    isRegistering.toggle()
                }
                .font(.footnote)

                Spacer()
            }
        }
    }
}
