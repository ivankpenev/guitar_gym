import Foundation

struct ExerciseInfo: Codable, Identifiable {
    let exerciseType: String
    let displayName: String
    let description: String

    var id: String { exerciseType }

    enum CodingKeys: String, CodingKey {
        case exerciseType = "exercise_type"
        case displayName = "display_name"
        case description
    }
}

struct QuestionRequest: Codable {
    let difficulty: Int
}

struct QuestionResponse: Codable {
    let exerciseType: String
    let prompt: String
    let choices: [String]
    let visualData: [String: AnyCodable]
    let questionToken: String

    enum CodingKeys: String, CodingKey {
        case exerciseType = "exercise_type"
        case prompt
        case choices
        case visualData = "visual_data"
        case questionToken = "question_token"
    }
}

struct AnswerRequest: Codable {
    let questionToken: String
    let userAnswer: String

    enum CodingKeys: String, CodingKey {
        case questionToken = "question_token"
        case userAnswer = "user_answer"
    }
}

struct AnswerResponse: Codable {
    let correct: Bool
    let correctAnswer: String
    let userAnswer: String
    let explanation: String

    enum CodingKeys: String, CodingKey {
        case correct
        case correctAnswer = "correct_answer"
        case userAnswer = "user_answer"
        case explanation
    }
}

/// Type-erased Codable for handling dynamic JSON (visual_data).
struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let intVal = try? container.decode(Int.self) {
            value = intVal
        } else if let doubleVal = try? container.decode(Double.self) {
            value = doubleVal
        } else if let stringVal = try? container.decode(String.self) {
            value = stringVal
        } else if let boolVal = try? container.decode(Bool.self) {
            value = boolVal
        } else if let arrayVal = try? container.decode([AnyCodable].self) {
            value = arrayVal.map { $0.value }
        } else if let dictVal = try? container.decode([String: AnyCodable].self) {
            value = dictVal.mapValues { $0.value }
        } else {
            value = NSNull()
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        if let intVal = value as? Int {
            try container.encode(intVal)
        } else if let doubleVal = value as? Double {
            try container.encode(doubleVal)
        } else if let stringVal = value as? String {
            try container.encode(stringVal)
        } else if let boolVal = value as? Bool {
            try container.encode(boolVal)
        } else {
            try container.encodeNil()
        }
    }
}
