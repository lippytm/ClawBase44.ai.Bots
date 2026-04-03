/**
 * Grok (xAI) integration module.
 * Connects to the xAI API which is OpenAI-compatible.
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class GrokIntegration {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || process.env.XAI_API_URL || "https://api.x.ai/v1";
    this.apiKey = config.apiKey || process.env.XAI_API_KEY;
    this.model = config.model || process.env.GROK_MODEL || "grok-3";
  }

  _headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
    };
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
      throw new Error(`Grok chat failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async listModels() {
    const res = await fetch(`${this.apiUrl}/models`, {
      headers: this._headers(),
    });
    if (!res.ok) {
      throw new Error(`Grok list models failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }
}

module.exports = GrokIntegration;
