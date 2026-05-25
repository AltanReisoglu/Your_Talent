import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { StatusBar } from "expo-status-bar";

import { AccountScreen } from "../features/account/AccountScreen";
import { CaptureScreen } from "../features/capture/CaptureScreen";
import { ChatScreen } from "../features/chat/ChatScreen";
import { WikiSearchScreen } from "../features/wiki/WikiSearchScreen";
import { colors, radius, spacing } from "../components/design";

type Tab = "chat" | "wiki" | "capture" | "account";

const tabs: Array<{ id: Tab; label: string }> = [
  { id: "chat", label: "Chat" },
  { id: "wiki", label: "Wiki" },
  { id: "capture", label: "Capture" },
  { id: "account", label: "Account" }
];

export function AppShell() {
  const [activeTab, setActiveTab] = useState<Tab>("chat");

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />
      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <Pressable
            accessibilityRole="tab"
            accessibilityState={{ selected: activeTab === tab.id }}
            key={tab.id}
            onPress={() => setActiveTab(tab.id)}
            style={[styles.tab, activeTab === tab.id ? styles.activeTab : null]}
          >
            <Text style={[styles.tabText, activeTab === tab.id ? styles.activeTabText : null]}>
              {tab.label}
            </Text>
          </Pressable>
        ))}
      </View>
      <View style={styles.screen}>
        {activeTab === "chat" ? <ChatScreen /> : null}
        {activeTab === "wiki" ? <WikiSearchScreen /> : null}
        {activeTab === "capture" ? <CaptureScreen /> : null}
        {activeTab === "account" ? <AccountScreen /> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background
  },
  screen: {
    flex: 1
  },
  tabBar: {
    backgroundColor: colors.panel,
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    flexDirection: "row",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.xl,
    paddingBottom: spacing.sm
  },
  tab: {
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm
  },
  activeTab: {
    backgroundColor: colors.primary
  },
  tabText: {
    color: colors.muted,
    fontSize: 14,
    fontWeight: "700"
  },
  activeTabText: {
    color: "#ffffff"
  }
});
