/**
 * OpenAI / ChatGPT integration module.
 * Supports Chat Completions and the Assistants API (ChatGPT Bots).
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class OpenAIIntegration {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || process.env.OPENAI_API_URL || "https://api.openai.com/v1";
    this.apiKey = config.apiKey || process.env.OPENAI_API_KEY;
    this.model = config.model || process.env.OPENAI_MODEL || "gpt-4o";
    this.assistantId = config.assistantId || process.env.CHATGPT_ASSISTANT_ID;
  }

  _headers(beta = false) {
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
    };
    if (beta) {
      headers["OpenAI-Beta"] = "assistants=v2";
    }
    return headers;
  }

  async chat(messages, options = {}) {
    const url = `${this.apiUrl}/chat/completions`;
    const res = await fetch(url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({
        model: options.model || this.model,
        messages,
        ...options,
      }),
    });
    if (!res.ok) {
      throw new Error(`OpenAI chat failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async createThread() {
    const res = await fetch(`${this.apiUrl}/threads`, {
      method: "POST",
      headers: this._headers(true),
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      throw new Error(`OpenAI thread creation failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async addMessage(threadId, content, role = "user") {
    const res = await fetch(`${this.apiUrl}/threads/${threadId}/messages`, {
      method: "POST",
      headers: this._headers(true),
      body: JSON.stringify({ role, content }),
    });
    if (!res.ok) {
      throw new Error(`OpenAI add message failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async runAssistant(threadId, assistantId) {
    const id = assistantId || this.assistantId;
    const res = await fetch(`${this.apiUrl}/threads/${threadId}/runs`, {
      method: "POST",
      headers: this._headers(true),
      body: JSON.stringify({ assistant_id: id }),
    });
    if (!res.ok) {
      throw new Error(`OpenAI run assistant failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async getRunStatus(threadId, runId) {
    const res = await fetch(`${this.apiUrl}/threads/${threadId}/runs/${runId}`, {
      headers: this._headers(true),
    });
    if (!res.ok) {
      throw new Error(`OpenAI get run status failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async listMessages(threadId) {
    const res = await fetch(`${this.apiUrl}/threads/${threadId}/messages`, {
      headers: this._headers(true),
    });
    if (!res.ok) {
      throw new Error(`OpenAI list messages failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }
}

module.exports = OpenAIIntegration;
