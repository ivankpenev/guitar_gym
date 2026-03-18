import { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Fretboard from "../../src/components/Fretboard";
import { getQuestion, submitAnswer } from "../../src/api";
import { QuestionResponse, AnswerResponse } from "../../src/types";

export default function ExerciseSession() {
  const { type, name } = useLocalSearchParams<{ type: string; name: string }>();

  const [difficulty, setDifficulty] = useState(1);
  const [question, setQuestion] = useState<QuestionResponse | null>(null);
  const [result, setResult] = useState<AnswerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [totalAnswered, setTotalAnswered] = useState(0);
  const [totalCorrect, setTotalCorrect] = useState(0);

  const loadQuestion = useCallback(async () => {
    setLoading(true);
    setResult(null);
    setSelectedAnswer(null);
    setError(null);
    try {
      const q = await getQuestion(type!, difficulty);
      setQuestion(q);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [type, difficulty]);

  useEffect(() => {
    loadQuestion();
  }, [loadQuestion]);

  const handleAnswer = async (answer: string) => {
    if (result || !question) return;
    setSelectedAnswer(answer);
    try {
      const res = await submitAnswer(type!, question.question_token, answer);
      setResult(res);
      setTotalAnswered((n) => n + 1);
      if (res.correct) setTotalCorrect((n) => n + 1);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // Extract highlights from visual_data
  const highlights = buildHighlights(question?.visual_data);

  const accuracy =
    totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : 0;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      {/* Score bar */}
      <View style={styles.scoreBar}>
        <View style={styles.scoreItem}>
          <Ionicons name="checkmark-circle" size={18} color="#4caf50" />
          <Text style={styles.scoreText}>
            {totalCorrect}/{totalAnswered}
          </Text>
        </View>
        {totalAnswered > 0 && (
          <Text style={styles.scoreText}>{accuracy}%</Text>
        )}
        <View style={styles.difficultyRow}>
          {[1, 2, 3, 4, 5].map((d) => (
            <Pressable
              key={d}
              style={[styles.diffBtn, d === difficulty && styles.diffBtnActive]}
              onPress={() => setDifficulty(d)}
            >
              <Text
                style={[
                  styles.diffText,
                  d === difficulty && styles.diffTextActive,
                ]}
              >
                {d}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      {/* Fretboard */}
      <Fretboard highlights={highlights} />

      {/* Question prompt */}
      {question && (
        <Text style={styles.prompt}>{question.prompt}</Text>
      )}

      {/* Error */}
      {error && (
        <Text style={styles.error}>{error}</Text>
      )}

      {/* Loading */}
      {loading && <ActivityIndicator size="large" color="#4f9cf7" style={{ marginTop: 20 }} />}

      {/* Result banner */}
      {result && (
        <View
          style={[
            styles.resultBanner,
            { backgroundColor: result.correct ? "#2e7d32" : "#c62828" },
          ]}
        >
          <Text style={styles.resultTitle}>
            {result.correct ? "Correct!" : "Incorrect"}
          </Text>
          {!result.correct && (
            <Text style={styles.resultDetail}>
              Answer: {result.correct_answer}
            </Text>
          )}
          {result.explanation ? (
            <Text style={styles.resultDetail}>{result.explanation}</Text>
          ) : null}
        </View>
      )}

      {/* Choices / Next button */}
      {!loading && question && !result && (
        <View style={styles.choicesGrid}>
          {question.choices.map((choice) => (
            <Pressable
              key={choice}
              style={[
                styles.choiceBtn,
                selectedAnswer === choice && styles.choiceBtnSelected,
              ]}
              onPress={() => handleAnswer(choice)}
            >
              <Text style={styles.choiceText}>{choice}</Text>
            </Pressable>
          ))}
        </View>
      )}

      {result && (
        <Pressable style={styles.nextBtn} onPress={loadQuestion}>
          <Text style={styles.nextBtnText}>Next Question</Text>
          <Ionicons name="arrow-forward" size={18} color="#fff" />
        </Pressable>
      )}
    </ScrollView>
  );
}

function buildHighlights(visualData?: Record<string, any>) {
  if (!visualData) return [];

  // Note identification: { highlight_positions: [{string, fret}] }
  if (visualData.highlight_positions) {
    return (visualData.highlight_positions as any[]).map((p) => ({
      string: p.string,
      fret: p.fret,
      label: "?",
      color: "#4f9cf7",
    }));
  }
  // Interval training: { positions: [{string, fret, label}] }
  if (visualData.positions) {
    const colors = ["#4f9cf7", "#e67e22", "#2ecc71", "#e74c3c"];
    return (visualData.positions as any[]).map((p, i) => ({
      string: p.string,
      fret: p.fret,
      label: p.label || "?",
      color: colors[i % colors.length],
    }));
  }
  return [];
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e" },
  scoreBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  scoreItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  scoreText: { color: "#ccc", fontSize: 15, fontWeight: "600" },
  difficultyRow: { flexDirection: "row", gap: 4 },
  diffBtn: {
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#1a1a2e",
  },
  diffBtnActive: { backgroundColor: "#4f9cf7" },
  diffText: { color: "#888", fontSize: 13, fontWeight: "700" },
  diffTextActive: { color: "#fff" },
  prompt: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "700",
    textAlign: "center",
    marginVertical: 12,
  },
  error: {
    color: "#ef5350",
    textAlign: "center",
    marginVertical: 8,
  },
  resultBanner: {
    borderRadius: 10,
    padding: 14,
    marginVertical: 12,
    alignItems: "center",
  },
  resultTitle: { color: "#fff", fontSize: 18, fontWeight: "800" },
  resultDetail: { color: "#ddd", fontSize: 14, marginTop: 4, textAlign: "center" },
  choicesGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginTop: 12,
    justifyContent: "center",
  },
  choiceBtn: {
    backgroundColor: "#1a1a2e",
    borderRadius: 10,
    paddingVertical: 14,
    paddingHorizontal: 24,
    minWidth: "45%",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#333",
  },
  choiceBtnSelected: { borderColor: "#4f9cf7" },
  choiceText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  nextBtn: {
    flexDirection: "row",
    backgroundColor: "#4f9cf7",
    borderRadius: 10,
    paddingVertical: 14,
    justifyContent: "center",
    alignItems: "center",
    gap: 8,
    marginTop: 16,
  },
  nextBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
});
