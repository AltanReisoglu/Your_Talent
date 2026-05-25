import { useMemo, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, TextInput, View } from "react-native";

import { FinancialSafetyNotice } from "../../components/FinancialSafetyNotice";
import { PrimaryButton } from "../../components/PrimaryButton";
import { Screen } from "../../components/Screen";
import { StatusBanner } from "../../components/StatusBanner";
import { colors, radius, spacing } from "../../components/design";
import { FinWikiApiError, invokeFinWiki } from "../../services/finwikiApi";

type ChatTurn = {
  role: "user" | "assistant";
  content: string;
};

function createSessionId(): string {
  return `mobile-${Date.now().toString(36)}`;
}

function errorMessage(error: unknown): string {
  if (error instanceof FinWikiApiError) {
    return `${error.message}${error.retryable ? " You can retry." : ""}`;
  }
  return error instanceof Error ? error.message : "Unexpected error.";
}

export function ChatScreen() {
  const userId = "mobile-guest";
  const sessionId = useMemo(createSessionId, []);
  const [prompt, setPrompt] = useState("DCF nedir?");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  async function sendPrompt() {
    const message = prompt.trim();
    if (!message || isLoading) {
      return;
    }
    setError("");
    setStatus("Sending prompt to FinWiki backend...");
    setIsLoading(true);
    setTurns((current) => [...current, { role: "user", content: message }]);
    try {
      const result = await invokeFinWiki({
        user_id: userId,
        session_id: sessionId,
        message
      });
      setTurns((current) => [...current, { role: "assistant", content: result.response }]);
      setStatus(`Thread: ${result.thread_id}`);
    } catch (err) {
      setError(errorMessage(err));
      setStatus("Request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Screen
      title="FinWiki"
      subtitle="Ask finance and knowledge-base questions through the hosted FinWiki agent."
    >
      <FinancialSafetyNotice />
      <View style={styles.card}>
        <TextInput
          multiline
          onChangeText={setPrompt}
          placeholder="Ask a financial concept or wiki question..."
          style={styles.input}
          value={prompt}
        />
        <PrimaryButton disabled={isLoading || !prompt.trim()} onPress={sendPrompt}>
          {isLoading ? "Thinking..." : "Ask FinWiki"}
        </PrimaryButton>
      </View>
      {isLoading ? <ActivityIndicator color={colors.primary} /> : null}
      {status ? <StatusBanner message={status} /> : null}
      {error ? <StatusBanner tone="danger" title="Request error" message={error} /> : null}
      <View style={styles.thread}>
        {turns.map((turn, index) => (
          <View
            key={`${turn.role}-${index}`}
            style={[styles.turn, turn.role === "assistant" ? styles.assistantTurn : styles.userTurn]}
          >
            <Text style={styles.role}>{turn.role === "assistant" ? "FinWiki" : "You"}</Text>
            <Text style={styles.content}>{turn.content}</Text>
          </View>
        ))}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.panel,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.md,
    padding: spacing.md
  },
  input: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 22,
    minHeight: 96,
    textAlignVertical: "top"
  },
  thread: {
    gap: spacing.md
  },
  turn: {
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.xs,
    padding: spacing.md
  },
  assistantTurn: {
    backgroundColor: colors.panel,
    borderColor: colors.border
  },
  userTurn: {
    backgroundColor: "#e8f5f1",
    borderColor: colors.primary
  },
  role: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase"
  },
  content: {
    color: colors.text,
    fontSize: 15,
    lineHeight: 22
  }
});
