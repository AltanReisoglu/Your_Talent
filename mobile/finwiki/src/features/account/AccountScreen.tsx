import { useState } from "react";
import { StyleSheet, Text, TextInput, View } from "react-native";

import { FinancialSafetyNotice } from "../../components/FinancialSafetyNotice";
import { PrimaryButton } from "../../components/PrimaryButton";
import { Screen } from "../../components/Screen";
import { StatusBanner } from "../../components/StatusBanner";
import { colors, radius, spacing } from "../../components/design";
import { FinWikiApiError, getApiBaseUrl, requestAccountDeletion } from "../../services/finwikiApi";

function errorMessage(error: unknown): string {
  if (error instanceof FinWikiApiError) {
    return error.message;
  }
  return error instanceof Error ? error.message : "Unexpected error.";
}

export function AccountScreen() {
  const [userId, setUserId] = useState("mobile-guest");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function requestDeletion() {
    if (!userId.trim() || isSubmitting) {
      return;
    }
    setStatus("");
    setError("");
    setIsSubmitting(true);
    try {
      const result = await requestAccountDeletion(userId.trim(), true);
      setStatus(
        `Deletion requested. Effective after ${result.effective_after}. ${result.retained_data_notice}`
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Screen
      title="Account & Privacy"
      subtitle="Review the active backend, safety posture, and account deletion path."
    >
      <FinancialSafetyNotice />
      <StatusBanner title="Backend" message={getApiBaseUrl()} />
      <View style={styles.card}>
        <Text style={styles.label}>User ID</Text>
        <TextInput onChangeText={setUserId} style={styles.input} value={userId} />
        <Text style={styles.help}>
          If accounts are enabled for store release, Apple and Google require an accessible
          deletion path. This request is sent to the backend for audit-aware processing.
        </Text>
        <PrimaryButton disabled={!userId.trim() || isSubmitting} onPress={requestDeletion}>
          {isSubmitting ? "Requesting..." : "Request Account Deletion"}
        </PrimaryButton>
      </View>
      {status ? <StatusBanner tone="success" title="Deletion request" message={status} /> : null}
      {error ? <StatusBanner tone="danger" title="Deletion error" message={error} /> : null}
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
  label: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700"
  },
  input: {
    borderColor: colors.border,
    borderRadius: radius.sm,
    borderWidth: 1,
    color: colors.text,
    fontSize: 16,
    padding: spacing.md
  },
  help: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20
  }
});
