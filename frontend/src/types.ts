export interface ExerciseInfo {
  exercise_type: string;
  display_name: string;
  description: string;
}

export interface QuestionResponse {
  exercise_type: string;
  prompt: string;
  choices: string[];
  visual_data: Record<string, any>;
  question_token: string;
}

export interface AnswerResponse {
  correct: boolean;
  correct_answer: string;
  user_answer: string;
  explanation: string;
}
