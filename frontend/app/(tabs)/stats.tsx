import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";

export default function StatsScreen() {
  return (
    <View style={styles.container}>
      <Ionicons name="stats-chart" size={48} color="#555" />
      <Text style={styles.title}>Stats</Text>
      <Text style={styles.sub}>
        Practice stats will appear here once you log in and complete some
        exercises.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#16213e",
    justifyContent: "center",
    alignItems: "center",
    padding: 32,
  },
  title: { color: "#fff", fontSize: 22, fontWeight: "700", marginTop: 12 },
  sub: { color: "#888", fontSize: 14, textAlign: "center", marginTop: 8 },
});
