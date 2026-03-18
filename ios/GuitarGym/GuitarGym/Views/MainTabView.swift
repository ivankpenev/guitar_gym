import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            ExerciseListView()
                .tabItem {
                    Label("Practice", systemImage: "music.note.list")
                }

            StatsView()
                .tabItem {
                    Label("Stats", systemImage: "chart.bar")
                }

            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
        }
    }
}
