/**
 * Base44 integration module.
 * Connects to the Base44 platform API for app and workflow management.
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class Base44Integration {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || process.env.BASE44_API_URL || "https://api.base44.com";
    this.apiKey = config.apiKey || process.env.BASE44_API_KEY;
    this.appId = config.appId || process.env.BASE44_APP_ID;
  }

  _headers() {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.apiKey}`,
    };
  }

  async triggerWorkflow(workflowId, payload = {}) {
    const url = `${this.apiUrl}/apps/${this.appId}/workflows/${workflowId}/trigger`;
    const res = await fetch(url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Base44 workflow trigger failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async getAppStatus() {
    const url = `${this.apiUrl}/apps/${this.appId}`;
    const res = await fetch(url, { headers: this._headers() });
    if (!res.ok) {
      throw new Error(`Base44 app status check failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }

  async sendEvent(eventName, data = {}) {
    const url = `${this.apiUrl}/apps/${this.appId}/events`;
    const res = await fetch(url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ event: eventName, data }),
    });
    if (!res.ok) {
      throw new Error(`Base44 event send failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }
}

module.exports = Base44Integration;
