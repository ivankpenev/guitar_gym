import SwiftUI

struct ExerciseListView: View {
    @State private var exercises: [ExerciseInfo] = []
    @State private var isLoading = true

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView("Loading exercises...")
                } else {
                    List(exercises) { exercise in
                        NavigationLink {
                            ExerciseSessionView(exerciseType: exercise.exerciseType, title: exercise.displayName)
                        } label: {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(exercise.displayName)
                                    .font(.headline)
                                Text(exercise.description)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationTitle("Practice")
            .task {
                await loadExercises()
            }
        }
    }

    private func loadExercises() async {
        do {
            let result: [ExerciseInfo] = try await APIClient.shared.get(path: "/exercises/")
            exercises = result
        } catch {
            // Fallback: show hardcoded exercises if server unavailable
            exercises = [
                ExerciseInfo(exerciseType: "note_identification", displayName: "Note Identification", description: "Identify the note at a given fretboard position."),
                ExerciseInfo(exerciseType: "interval_training", displayName: "Interval Training", description: "Identify the interval between two notes on the fretboard."),
            ]
        }
        isLoading = false
    }
}
