import SwiftUI

struct StatsView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Image(systemName: "chart.bar")
                    .font(.system(size: 48))
                    .foregroundStyle(.secondary)
                Text("Stats & Progress")
                    .font(.headline)
                Text("Your practice stats will appear here as you complete exercises.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
            }
            .navigationTitle("Stats")
        }
    }
}
