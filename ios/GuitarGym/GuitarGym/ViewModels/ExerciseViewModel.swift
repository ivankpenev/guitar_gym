import Foundation

@MainActor
class ExerciseViewModel: ObservableObject {
    @Published var currentQuestion: QuestionResponse?
    @Published var lastResult: AnswerResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?

    // Session stats
    @Published var totalAnswered = 0
    @Published var totalCorrect = 0

    let exerciseType: String
    var difficulty: Int

    private let api = APIClient.shared

    init(exerciseType: String, difficulty: Int = 1) {
        self.exerciseType = exerciseType
        self.difficulty = difficulty
    }

    var accuracy: Double {
        guard totalAnswered > 0 else { return 0 }
        return Double(totalCorrect) / Double(totalAnswered) * 100
    }

    func loadQuestion() async {
        isLoading = true
        lastResult = nil
        errorMessage = nil

        do {
            let body = QuestionRequest(difficulty: difficulty)
            let question: QuestionResponse = try await api.post(
                path: "/exercises/\(exerciseType)/question",
                body: body
            )
            currentQuestion = question
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func submitAnswer(_ answer: String) async {
        guard let question = currentQuestion else { return }
        isLoading = true

        do {
            let body = AnswerRequest(questionToken: question.questionToken, userAnswer: answer)
            let result: AnswerResponse = try await api.post(
                path: "/exercises/\(exerciseType)/answer",
                body: body
            )
            lastResult = result
            totalAnswered += 1
            if result.correct {
                totalCorrect += 1
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func reset() {
        totalAnswered = 0
        totalCorrect = 0
        currentQuestion = nil
        lastResult = nil
    }
}
