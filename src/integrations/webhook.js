/**
 * Generic webhook handler module.
 * Sends outgoing webhooks to arbitrary URLs and validates incoming
 * webhook signatures (HMAC-SHA256).
 */

const crypto = require("crypto");
const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class WebhookIntegration {
  constructor(config = {}) {
    this.incomingSecret = config.incomingSecret || process.env.WEBHOOK_SECRET || "";
    this.targets = config.targets || [];
  }

  verifySignature(payload, signature) {
    if (!this.incomingSecret) {
      return false;
    }
    const expected = `sha256=${crypto
      .createHmac("sha256", this.incomingSecret)
      .update(payload)
      .digest("hex")}`;
    try {
      return crypto.timingSafeEqual(
        Buffer.from(expected, "utf8"),
        Buffer.from(signature, "utf8")
      );
    } catch {
      return false;
    }
  }

  async send(url, payload, secret) {
    const body = JSON.stringify(payload);
    const headers = { "Content-Type": "application/json" };
    if (secret) {
      const sig = crypto.createHmac("sha256", secret).update(body).digest("hex");
      headers["X-Hub-Signature-256"] = `sha256=${sig}`;
    }
    const res = await fetch(url, { method: "POST", headers, body });
    if (!res.ok) {
      throw new Error(`Webhook send to ${url} failed: ${res.status} ${res.statusText}`);
    }
    return res;
  }

  async broadcast(eventName, payload) {
    const targets = this.targets.filter(
      (t) => !t.events || t.events.includes(eventName)
    );
    const results = await Promise.allSettled(
      targets.map((t) => this.send(t.url, { event: eventName, ...payload }, t.secret))
    );
    return results;
  }
}

module.exports = WebhookIntegration;
