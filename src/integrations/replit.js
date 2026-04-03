/**
 * Replit integration module.
 * Connects to the Replit API for running and managing Repls.
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class ReplitIntegration {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || process.env.REPLIT_API_URL || "https://replit.com/api/v1";
    this.apiKey = config.apiKey || process.env.REPLIT_API_KEY;
    this.replId = config.replId || process.env.REPLIT_REPL_ID;
  }

  _headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
    };
  }

  async getRepl(replId) {
    const id = replId || this.replId;
    const res = await fetch(`${this.apiUrl}/repls/${id}`, {
      headers: this._headers(),
    });
    if (!res.ok) {
      throw new Error(`Replit get repl failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async runRepl(replId) {
    const id = replId || this.replId;
    const res = await fetch(`${this.apiUrl}/repls/${id}/run`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      throw new Error(`Replit run repl failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async updateReplFile(replId, filePath, content) {
    const id = replId || this.replId;
    const res = await fetch(`${this.apiUrl}/repls/${id}/files`, {
      method: "PUT",
      headers: this._headers(),
      body: JSON.stringify({ path: filePath, content }),
    });
    if (!res.ok) {
      throw new Error(`Replit update file failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async listRepls() {
    const res = await fetch(`${this.apiUrl}/repls`, {
      headers: this._headers(),
    });
    if (!res.ok) {
      throw new Error(`Replit list repls failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }
}

module.exports = ReplitIntegration;
