import SwiftUI

struct ExerciseSessionView: View {
    @StateObject private var vm: ExerciseViewModel
    let title: String

    init(exerciseType: String, title: String) {
        self._vm = StateObject(wrappedValue: ExerciseViewModel(exerciseType: exerciseType))
        self.title = title
    }

    var body: some View {
        VStack(spacing: 20) {
            // Score bar
            HStack {
                Label("\(vm.totalCorrect)/\(vm.totalAnswered)", systemImage: "checkmark.circle")
                Spacer()
                if vm.totalAnswered > 0 {
                    Text(String(format: "%.0f%%", vm.accuracy))
                        .font(.headline)
                }
                Spacer()
                DifficultyPicker(difficulty: $vm.difficulty)
            }
            .padding(.horizontal)

            if vm.isLoading && vm.currentQuestion == nil {
                Spacer()
                ProgressView()
                Spacer()
            } else if let question = vm.currentQuestion {
                // Fretboard visualization
                FretboardView(
                    highlights: highlightsFromQuestion(question),
                    fretRange: fretRangeFromQuestion(question)
                )

                // Question prompt
                Text(question.prompt)
                    .font(.title3.bold())

                // Result feedback
                if let result = vm.lastResult {
                    ResultBanner(result: result)
                }

                // Answer choices or next button
                if vm.lastResult != nil {
                    Button("Next Question") {
                        Task { await vm.loadQuestion() }
                    }
                    .buttonStyle(.borderedProminent)
                } else {
                    // Multiple choice buttons
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(question.choices, id: \.self) { choice in
                            Button {
                                Task { await vm.submitAnswer(choice) }
                            } label: {
                                Text(choice)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                    .padding(.horizontal)
                }
            } else {
                Spacer()
                Text("Tap below to start practicing")
                    .foregroundStyle(.secondary)
                Button("Start") {
                    Task { await vm.loadQuestion() }
                }
                .buttonStyle(.borderedProminent)
                Spacer()
            }

            Spacer()
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Helpers

    private func highlightsFromQuestion(_ q: QuestionResponse) -> [FretHighlight] {
        // Handle both single-position (note ID) and multi-position (interval) formats
        if let positions = q.visualData["positions"]?.value as? [[String: Any]] {
            return positions.enumerated().map { index, pos in
                FretHighlight(
                    string: pos["string"] as? Int ?? 1,
                    fret: pos["fret"] as? Int ?? 0,
                    label: pos["label"] as? String,
                    color: index == 0 ? .blue : .orange
                )
            }
        }

        if let highlightPositions = q.visualData["highlight_positions"]?.value as? [[String: Any]] {
            return highlightPositions.map { pos in
                FretHighlight(
                    string: pos["string"] as? Int ?? 1,
                    fret: pos["fret"] as? Int ?? 0,
                    label: "?",
                    color: .blue
                )
            }
        }

        return []
    }

    private func fretRangeFromQuestion(_ q: QuestionResponse) -> ClosedRange<Int> {
        let highlights = highlightsFromQuestion(q)
        let frets = highlights.map { $0.fret }
        let minFret = max(0, (frets.min() ?? 0) - 1)
        let maxFret = max(minFret + 5, (frets.max() ?? 5) + 2)
        return minFret...min(24, maxFret)
    }
}

struct ResultBanner: View {
    let result: AnswerResponse

    var body: some View {
        VStack(spacing: 4) {
            HStack {
                Image(systemName: result.correct ? "checkmark.circle.fill" : "xmark.circle.fill")
                Text(result.correct ? "Correct!" : "Incorrect")
                    .font(.headline)
            }
            .foregroundColor(result.correct ? .green : .red)

            if !result.explanation.isEmpty {
                Text(result.explanation)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(result.correct ? Color.green.opacity(0.1) : Color.red.opacity(0.1))
        )
        .padding(.horizontal)
    }
}

struct DifficultyPicker: View {
    @Binding var difficulty: Int

    var body: some View {
        Menu {
            ForEach(1...5, id: \.self) { level in
                Button {
                    difficulty = level
                } label: {
                    if level == difficulty {
                        Label("Level \(level)", systemImage: "checkmark")
                    } else {
                        Text("Level \(level)")
                    }
                }
            }
        } label: {
            Label("Lvl \(difficulty)", systemImage: "slider.horizontal.3")
                .font(.caption)
        }
    }
}
