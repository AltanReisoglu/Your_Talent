import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { StatusBanner } from "../../components/StatusBanner";
import { colors, radius, spacing } from "../../components/design";
import { FinWikiApiError, loadWikiPage, type WikiPageResponse } from "../../services/finwikiApi";

type WikiPageScreenProps = {
  path: string;
};

function errorMessage(error: unknown): string {
  if (error instanceof FinWikiApiError) {
    return error.message;
  }
  return error instanceof Error ? error.message : "Unexpected error.";
}

export function WikiPageScreen({ path }: WikiPageScreenProps) {
  const [page, setPage] = useState<WikiPageResponse["page"] | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError("");
    loadWikiPage(path)
      .then((result) => {
        if (!cancelled) {
          setPage(result.page);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(errorMessage(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [path]);

  if (isLoading) {
    return <ActivityIndicator color={colors.primary} />;
  }

  if (error) {
    return <StatusBanner tone="danger" title="Page error" message={error} />;
  }

  if (!page) {
    return null;
  }

  return (
    <View style={styles.page}>
      <Text style={styles.title}>{page.title}</Text>
      <Text style={styles.meta}>
        {page.review_status || "unknown"} · {page.last_updated || "no date"}
      </Text>
      <Text style={styles.body}>{page.content}</Text>
      {page.sources.length ? (
        <StatusBanner title="Sources" message={page.sources.join("\n")} />
      ) : null}
      {page.related.length ? (
        <StatusBanner title="Related" message={page.related.join(", ")} />
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  page: {
    backgroundColor: colors.panel,
    borderColor: colors.border,
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.md,
    padding: spacing.md
  },
  title: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "700"
  },
  meta: {
    color: colors.muted,
    fontSize: 13
  },
  body: {
    color: colors.text,
    fontSize: 15,
    lineHeight: 22
  }
});
