import { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Pressable,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { getExercises } from "../../src/api";
import { ExerciseInfo } from "../../src/types";

const FALLBACK_EXERCISES: ExerciseInfo[] = [
  {
    exercise_type: "note_identification",
    display_name: "Note Identification",
    description: "Identify the note at a given fretboard position.",
  },
  {
    exercise_type: "interval_training",
    display_name: "Interval Training",
    description: "Identify the interval between two notes on the fretboard.",
  },
];

export default function ExerciseListScreen() {
  const router = useRouter();
  const [exercises, setExercises] = useState<ExerciseInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getExercises()
      .then(setExercises)
      .catch((err) => {
        console.warn("API unavailable, using fallback list:", err.message);
        setError("Backend offline — using built-in exercises");
        setExercises(FALLBACK_EXERCISES);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4f9cf7" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {error && <Text style={styles.banner}>{error}</Text>}
      <FlatList
        data={exercises}
        keyExtractor={(item) => item.exercise_type}
        contentContainerStyle={{ padding: 16, gap: 12 }}
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() =>
              router.push({
                pathname: "/exercise/[type]",
                params: { type: item.exercise_type, name: item.display_name },
              })
            }
          >
            <View style={styles.cardRow}>
              <Ionicons name="musical-notes" size={28} color="#4f9cf7" />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={styles.cardTitle}>{item.display_name}</Text>
                <Text style={styles.cardDesc}>{item.description}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#666" />
            </View>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e" },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#16213e" },
  banner: {
    backgroundColor: "#e6a817",
    color: "#1a1a2e",
    textAlign: "center",
    paddingVertical: 6,
    fontSize: 13,
    fontWeight: "600",
  },
  card: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 16,
  },
  cardRow: { flexDirection: "row", alignItems: "center" },
  cardTitle: { color: "#fff", fontSize: 17, fontWeight: "700" },
  cardDesc: { color: "#aaa", fontSize: 13, marginTop: 2 },
});
