import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authVM: AuthViewModel

    var body: some View {
        NavigationStack {
            List {
                if let user = authVM.currentUser {
                    Section("Account") {
                        LabeledContent("Username", value: user.username)
                        LabeledContent("Email", value: user.email)
                    }
                }

                Section {
                    Button("Log Out", role: .destructive) {
                        authVM.logout()
                    }
                }
            }
            .navigationTitle("Settings")
        }
    }
}
