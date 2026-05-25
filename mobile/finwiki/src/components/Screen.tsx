import type { PropsWithChildren } from "react";
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "./design";

type ScreenProps = PropsWithChildren<{
  title: string;
  subtitle?: string;
}>;

export function Screen({ title, subtitle, children }: ScreenProps) {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background
  },
  content: {
    gap: spacing.lg,
    padding: spacing.lg,
    paddingBottom: spacing.xl
  },
  header: {
    gap: spacing.xs
  },
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: "700"
  },
  subtitle: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 21
  }
});
