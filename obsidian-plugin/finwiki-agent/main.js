const {
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TextAreaComponent,
  requestUrl,
} = require("obsidian");

const DEFAULT_SETTINGS = {
  endpoint: "http://127.0.0.1:8000/invoke",
  userId: "obsidian-user",
  sessionPrefix: "obsidian",
  maxContextChars: 12000,
};

module.exports = class FinWikiAgentPlugin extends Plugin {
  async onload() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    this.lastResponse = null;

    this.addSettingTab(new FinWikiSettingTab(this.app, this));

    this.addRibbonIcon("bot", "Ask FinWiki", () => {
      this.runSafely(() => this.openAskModal());
    });

    this.addCommand({
      id: "ask-finwiki",
      name: "Ask FinWiki",
      callback: () => this.runSafely(() => this.openAskModal()),
    });

    this.addCommand({
      id: "ask-finwiki-with-context",
      name: "Ask FinWiki about selection/current note",
      editorCallback: () => this.runSafely(() => this.askWithContext()),
    });

    this.addCommand({
      id: "ingest-current-note",
      name: "Ingest current note",
      editorCallback: () => this.runSafely(() => this.ingestCurrentNote()),
    });

    this.addCommand({
      id: "run-finwiki-lint",
      name: "Run wiki lint",
      callback: () => this.runSafely(() => this.runLint()),
    });
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  async runSafely(action) {
    try {
      await action();
    } catch (error) {
      new Notice(error.message || String(error));
      console.error("FinWiki plugin action failed", error);
    }
  }

  openAskModal(initialValue = "") {
    new FinWikiPromptModal(
      this.app,
      "Ask FinWiki",
      initialValue,
      async (prompt) => {
        await this.invokeAndShow(prompt);
      }
    ).open();
  }

  async askWithContext() {
    const context = this.getActiveNoteContext();
    const prompt = [
      "Answer the user's question using the provided Obsidian note context when relevant.",
      "If the context should become durable FinWiki knowledge, say what page should be updated.",
      "",
      this.renderContext(context),
      "",
      "User question:",
    ].join("\n");
    this.openAskModal(prompt);
  }

  async ingestCurrentNote() {
    const context = this.getActiveNoteContext({ requireFullNote: true });
    const prompt = [
      "Ingest this Obsidian note into the FinWiki knowledge base.",
      "Use the existing FinWiki routing: check for duplicates, preserve source lineage, update or create the appropriate English wiki page, and do not duplicate agent logic in the client.",
      "",
      this.renderContext(context),
    ].join("\n");
    await this.invokeAndShow(prompt);
  }

  async runLint() {
    await this.invokeAndShow(
      "Run a FinWiki wiki health check/lint report. Return a concise summary of orphan pages, dead wikilinks, stale pages, and index issues."
    );
  }

  async invokeAndShow(message) {
    if (!message || !message.trim()) {
      new Notice("FinWiki prompt is empty.");
      return;
    }

    const notice = new Notice("FinWiki is thinking...", 0);
    try {
      const response = await this.invokeFinWiki(message);
      this.lastResponse = response;
      notice.hide();
      new FinWikiResponseModal(this.app, this, response).open();
    } catch (error) {
      notice.hide();
      new Notice(`FinWiki request failed: ${error.message}`);
      console.error("FinWiki request failed", error);
    }
  }

  async invokeFinWiki(message) {
    const payload = {
      user_id: this.settings.userId || DEFAULT_SETTINGS.userId,
      session_id: this.buildSessionId(),
      message,
    };

    const response = await requestUrl({
      url: this.settings.endpoint || DEFAULT_SETTINGS.endpoint,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (response.status < 200 || response.status >= 300) {
      throw new Error(this.extractErrorMessage(response));
    }

    const data = this.parseResponse(response);
    if (!data || typeof data.response !== "string") {
      throw new Error("Gateway returned JSON without a response field.");
    }
    return data;
  }

  buildSessionId() {
    const prefix = (this.settings.sessionPrefix || "obsidian")
      .trim()
      .replace(/[^a-zA-Z0-9_-]+/g, "-")
      .replace(/^-+|-+$/g, "");
    return `${prefix || "obsidian"}-${new Date()
      .toISOString()
      .replace(/[:.]/g, "-")}`;
  }

  getActiveNoteContext(options = {}) {
    const view = this.app.workspace.getActiveViewOfType(MarkdownView);
    if (!view || !view.file) {
      throw new Error("Open a Markdown note first.");
    }

    const path = view.file.path;
    if (this.isProtectedPath(path)) {
      throw new Error(`Refusing to send protected path as context: ${path}`);
    }

    const selection = view.editor.getSelection();
    const rawContent =
      options.requireFullNote || !selection ? view.editor.getValue() : selection;
    const maxChars = Number(this.settings.maxContextChars) || 12000;
    const content = rawContent.slice(0, maxChars);

    return {
      path,
      mode: selection && !options.requireFullNote ? "selection" : "note",
      content,
      truncated: rawContent.length > content.length,
    };
  }

  isProtectedPath(path) {
    const normalized = path.toLowerCase();
    return (
      normalized.startsWith(".") ||
      normalized.includes("/.obsidian/") ||
      normalized.includes("/.git/") ||
      normalized === ".env" ||
      normalized.startsWith("raw/") ||
      normalized.startsWith("policies/")
    );
  }

  renderContext(context) {
    const truncated = context.truncated
      ? "\n\n[Context truncated by FinWiki Obsidian plugin.]"
      : "";
    return [
      "Obsidian context:",
      `- path: ${context.path}`,
      `- mode: ${context.mode}`,
      "",
      "```markdown",
      context.content,
      "```",
      truncated,
    ].join("\n");
  }

  async appendResponseToActiveNote(response) {
    const view = this.app.workspace.getActiveViewOfType(MarkdownView);
    if (!view || !view.file) {
      throw new Error("Open a Markdown note before appending.");
    }
    if (this.isProtectedPath(view.file.path)) {
      throw new Error(`Refusing to write protected path: ${view.file.path}`);
    }

    const block = [
      "",
      "",
      "## FinWiki Response",
      "",
      `> ${new Date().toISOString()}`,
      "",
      response.response.trim(),
      "",
    ].join("\n");

    view.editor.replaceRange(block, {
      line: view.editor.lineCount(),
      ch: 0,
    });
  }

  parseResponse(response) {
    if (response.json && typeof response.json === "object") {
      return response.json;
    }
    try {
      return JSON.parse(response.text);
    } catch (error) {
      throw new Error("Gateway returned invalid JSON.");
    }
  }

  extractErrorMessage(response) {
    try {
      const data = this.parseResponse(response);
      return data.detail || data.title || response.text || `HTTP ${response.status}`;
    } catch (_error) {
      return response.text || `HTTP ${response.status}`;
    }
  }
};

class FinWikiPromptModal extends Modal {
  constructor(app, title, initialValue, onSubmit) {
    super(app);
    this.title = title;
    this.initialValue = initialValue;
    this.onSubmit = onSubmit;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.addClass("finwiki-modal");
    contentEl.createEl("h2", { text: this.title });

    const textarea = new TextAreaComponent(contentEl);
    textarea.inputEl.addClass("finwiki-prompt");
    textarea.setValue(this.initialValue || "");
    textarea.inputEl.focus();

    new Setting(contentEl)
      .addButton((button) =>
        button
          .setButtonText("Send")
          .setCta()
          .onClick(async () => {
            const value = textarea.getValue().trim();
            this.close();
            await this.onSubmit(value);
          })
      )
      .addButton((button) =>
        button.setButtonText("Cancel").onClick(() => this.close())
      );
  }

  onClose() {
    this.contentEl.empty();
  }
}

class FinWikiResponseModal extends Modal {
  constructor(app, plugin, response) {
    super(app);
    this.plugin = plugin;
    this.response = response;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.addClass("finwiki-modal");
    contentEl.createEl("h2", { text: "FinWiki Response" });

    const responseEl = contentEl.createEl("pre", { cls: "finwiki-response" });
    responseEl.textContent = this.response.response;

    if (this.response.thread_id) {
      const meta = contentEl.createEl("div", { cls: "finwiki-meta" });
      meta.textContent = `Thread: ${this.response.thread_id}`;
    }

    new Setting(contentEl)
      .addButton((button) =>
        button
          .setButtonText("Append to note")
          .setCta()
          .onClick(async () => {
            try {
              await this.plugin.appendResponseToActiveNote(this.response);
              new Notice("FinWiki response appended to active note.");
              this.close();
            } catch (error) {
              new Notice(error.message);
            }
          })
      )
      .addButton((button) =>
        button.setButtonText("Close").onClick(() => this.close())
      );
  }

  onClose() {
    this.contentEl.empty();
  }
}

class FinWikiSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "FinWiki Agent" });

    new Setting(containerEl)
      .setName("Invoke endpoint")
      .setDesc("Local C# gateway endpoint. Default: http://127.0.0.1:8000/invoke")
      .addText((text) =>
        text
          .setPlaceholder(DEFAULT_SETTINGS.endpoint)
          .setValue(this.plugin.settings.endpoint)
          .onChange(async (value) => {
            this.plugin.settings.endpoint = value.trim() || DEFAULT_SETTINGS.endpoint;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("User ID")
      .setDesc("Identity passed to FinWiki.")
      .addText((text) =>
        text
          .setPlaceholder(DEFAULT_SETTINGS.userId)
          .setValue(this.plugin.settings.userId)
          .onChange(async (value) => {
            this.plugin.settings.userId = value.trim() || DEFAULT_SETTINGS.userId;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Session prefix")
      .setDesc("Prefix used for generated FinWiki session IDs.")
      .addText((text) =>
        text
          .setPlaceholder(DEFAULT_SETTINGS.sessionPrefix)
          .setValue(this.plugin.settings.sessionPrefix)
          .onChange(async (value) => {
            this.plugin.settings.sessionPrefix =
              value.trim() || DEFAULT_SETTINGS.sessionPrefix;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Max context characters")
      .setDesc("Maximum selected/note characters sent as context.")
      .addText((text) =>
        text
          .setPlaceholder(String(DEFAULT_SETTINGS.maxContextChars))
          .setValue(String(this.plugin.settings.maxContextChars))
          .onChange(async (value) => {
            const parsed = Number.parseInt(value, 10);
            this.plugin.settings.maxContextChars =
              Number.isFinite(parsed) && parsed > 0
                ? parsed
                : DEFAULT_SETTINGS.maxContextChars;
            await this.plugin.saveSettings();
          })
      );
  }
}
