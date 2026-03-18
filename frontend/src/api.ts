import { Platform } from "react-native";
import { ExerciseInfo, QuestionResponse, AnswerResponse } from "./types";

// Android emulator uses 10.0.2.2 for host loopback; iOS simulator & web use localhost
const BASE_URL =
  Platform.OS === "android"
    ? "http://10.0.2.2:8000"
    : "http://localhost:8000";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export async function getExercises(): Promise<ExerciseInfo[]> {
  return request("/exercises/");
}

export async function getQuestion(
  exerciseType: string,
  difficulty: number
): Promise<QuestionResponse> {
  return request(`/exercises/${exerciseType}/question`, {
    method: "POST",
    body: JSON.stringify({ difficulty }),
  });
}

export async function submitAnswer(
  exerciseType: string,
  questionToken: string,
  userAnswer: string
): Promise<AnswerResponse> {
  return request(`/exercises/${exerciseType}/answer`, {
    method: "POST",
    body: JSON.stringify({
      question_token: questionToken,
      user_answer: userAnswer,
    }),
  });
}
