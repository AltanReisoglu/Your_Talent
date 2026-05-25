import { StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "./design";

type StatusBannerProps = {
  tone?: "info" | "warning" | "danger" | "success";
  title?: string;
  message: string;
};

export function StatusBanner({ tone = "info", title, message }: StatusBannerProps) {
  const toneStyle =
    tone === "danger"
      ? styles.danger
      : tone === "warning"
        ? styles.warning
        : tone === "success"
          ? styles.success
          : styles.info;
  return (
    <View style={[styles.banner, toneStyle]}>
      {title ? <Text style={styles.title}>{title}</Text> : null}
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    borderRadius: radius.md,
    borderWidth: 1,
    gap: spacing.xs,
    padding: spacing.md
  },
  info: {
    backgroundColor: colors.panel,
    borderColor: colors.border
  },
  warning: {
    backgroundColor: colors.warningBackground,
    borderColor: colors.warning
  },
  danger: {
    backgroundColor: colors.dangerBackground,
    borderColor: colors.danger
  },
  success: {
    backgroundColor: colors.successBackground,
    borderColor: colors.success
  },
  title: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "700"
  },
  message: {
    color: colors.text,
    fontSize: 14,
    lineHeight: 20
  }
});
