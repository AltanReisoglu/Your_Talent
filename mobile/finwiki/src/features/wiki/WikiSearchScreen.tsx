import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { PrimaryButton } from "../../components/PrimaryButton";
import { Screen } from "../../components/Screen";
import { StatusBanner } from "../../components/StatusBanner";
import { colors, radius, spacing } from "../../components/design";
import { FinWikiApiError, searchWiki, type WikiPageSummary } from "../../services/finwikiApi";
import { WikiPageScreen } from "./WikiPageScreen";

function errorMessage(error: unknown): string {
  if (error instanceof FinWikiApiError) {
    return error.message;
  }
  return error instanceof Error ? error.message : "Unexpected error.";
}

export function WikiSearchScreen() {
  const [query, setQuery] = useState("DCF");
  const [results, setResults] = useState<WikiPageSummary[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runSearch() {
    const cleanQuery = query.trim();
    if (!cleanQuery || isLoading) {
      return;
    }
    setError("");
    setIsLoading(true);
    try {
      const response = await searchWiki(cleanQuery, 10);
      setResults(response.results);
      setSelectedPath(response.results[0]?.path ?? "");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Screen title="Knowledge Base" subtitle="Search durable FinWiki pages without opening Obsidian.">
      <View style={styles.card}>
        <TextInput
          onChangeText={setQuery}
          placeholder="Search concepts, companies, risk, regulation..."
          style={styles.input}
          value={query}
        />
        <PrimaryButton disabled={isLoading || !query.trim()} onPress={runSearch}>
          Search Wiki
        </PrimaryButton>
      </View>
      {isLoading ? <ActivityIndicator color={colors.primary} /> : null}
      {error ? <StatusBanner tone="danger" title="Search error" message={error} /> : null}
      <View style={styles.results}>
        {results.map((item) => (
          <Pressable
            key={item.path}
            onPress={() => setSelectedPath(item.path)}
            style={[styles.result, selectedPath === item.path ? styles.selectedResult : null]}
          >
            <Text style={styles.resultTitle}>{item.title}</Text>
            <Text style={styles.resultMeta}>
              {item.category} · {item.review_status} · {item.last_updated || "no date"}
            </Text>
            <Text style={styles.resultSummary}>{item.summary}</Text>
          </Pressable>
        ))}
      </View>
      {selectedPath ? <WikiPageScreen path={selectedPath} /> : null}
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
    minHeight: 44
  },
  results: {
    gap: spacing.md
  },
  result: {
    backgroundColor: colors.panel,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.xs,
    padding: spacing.md
  },
  selectedResult: {
    borderColor: colors.primary,
    borderWidth: 2
  },
  resultTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700"
  },
  resultMeta: {
    color: colors.muted,
    fontSize: 12
  },
  resultSummary: {
    color: colors.text,
    fontSize: 14,
    lineHeight: 20
  }
});
