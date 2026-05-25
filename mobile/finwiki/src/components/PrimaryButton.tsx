import type { PropsWithChildren } from "react";
import { Pressable, StyleSheet, Text } from "react-native";

import { colors, radius, spacing } from "./design";

type PrimaryButtonProps = PropsWithChildren<{
  disabled?: boolean;
  onPress: () => void;
}>;

export function PrimaryButton({ children, disabled = false, onPress }: PrimaryButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        pressed && !disabled ? styles.pressed : null,
        disabled ? styles.disabled : null
      ]}
    >
      <Text style={styles.label}>{children}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: "center",
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md
  },
  pressed: {
    backgroundColor: colors.primaryPressed
  },
  disabled: {
    opacity: 0.55
  },
  label: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700"
  }
});
