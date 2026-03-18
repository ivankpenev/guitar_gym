import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: "#1a1a2e" },
        headerTintColor: "#fff",
        contentStyle: { backgroundColor: "#16213e" },
      }}
    >
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen
        name="exercise/[type]"
        options={{ title: "Exercise", headerBackTitle: "Back" }}
      />
    </Stack>
  );
}
