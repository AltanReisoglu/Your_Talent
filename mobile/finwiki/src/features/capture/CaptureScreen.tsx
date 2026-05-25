import { useState } from "react";
import { StyleSheet, Text, TextInput, View } from "react-native";

import { PrimaryButton } from "../../components/PrimaryButton";
import { Screen } from "../../components/Screen";
import { StatusBanner } from "../../components/StatusBanner";
import { colors, radius, spacing } from "../../components/design";
import { FinWikiApiError, submitIngest, type IngestSubmissionRequest } from "../../services/finwikiApi";

type CaptureType = IngestSubmissionRequest["type"];

function errorMessage(error: unknown): string {
  if (error instanceof FinWikiApiError) {
    return error.message;
  }
  return error instanceof Error ? error.message : "Unexpected error.";
}

export function CaptureScreen() {
  const [type, setType] = useState<CaptureType>("note");
  const [content, setContent] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit() {
    if (!content.trim() || isSubmitting) {
      return;
    }
    setStatus("");
    setError("");
    setIsSubmitting(true);
    try {
      const result = await submitIngest({
        user_id: "mobile-guest",
        type,
        content,
        notes
      });
      setStatus(`${result.status}: ${result.message} (${result.submission_id})`);
      setContent("");
      setNotes("");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen
      title="Capture"
      subtitle="Send notes or URLs to backend-managed ingest. The app never writes wiki files directly."
    >
      <View style={styles.card}>
        <View style={styles.typeRow}>
          {(["note", "url", "excerpt"] as CaptureType[]).map((value) => (
            <Text
              key={value}
              onPress={() => setType(value)}
              style={[styles.typePill, type === value ? styles.activeType : null]}
            >
              {value}
            </Text>
          ))}
        </View>
        <TextInput
          multiline
          onChangeText={setContent}
          placeholder="Paste a note, URL, or source excerpt..."
          style={styles.input}
          value={content}
        />
        <TextInput
          multiline
          onChangeText={setNotes}
          placeholder="Optional filing note..."
          style={[styles.input, styles.notesInput]}
          value={notes}
        />
        <PrimaryButton disabled={!content.trim() || isSubmitting} onPress={submit}>
          {isSubmitting ? "Submitting..." : "Request Ingest"}
        </PrimaryButton>
      </View>
      {status ? <StatusBanner tone="success" title="Submission queued" message={status} /> : null}
      {error ? <StatusBanner tone="danger" title="Submission error" message={error} /> : null}
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
  typeRow: {
    flexDirection: "row",
    gap: spacing.sm
  },
  typePill: {
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    color: colors.muted,
    fontSize: 13,
    fontWeight: "700",
    overflow: "hidden",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    textTransform: "uppercase"
  },
  activeType: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
    color: "#ffffff"
  },
  input: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 22,
    minHeight: 112,
    textAlignVertical: "top"
  },
  notesInput: {
    minHeight: 72
  }
});
