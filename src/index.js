/**
 * ClawBase44.ai.Bots — Main entry point.
 *
 * Loads integration config and exposes all connectors.
 * Can be used as a library (require/import) or run directly to
 * perform a health-check across all configured integrations.
 */

"use strict";

const fs = require("fs");
const path = require("path");

const Base44Integration = require("./integrations/base44");
const OpenAIIntegration = require("./integrations/openai");
const GrokIntegration = require("./integrations/grok");
const ReplitIntegration = require("./integrations/replit");
const Web3Integration = require("./integrations/web3");
const GitHubIntegration = require("./integrations/github");
const WebhookIntegration = require("./integrations/webhook");

function loadConfig() {
  const configPath = path.resolve(__dirname, "../config/integrations.json");
  if (fs.existsSync(configPath)) {
    return JSON.parse(fs.readFileSync(configPath, "utf8"));
  }
  return {};
}

function createIntegrations(config = {}) {
  return {
    base44: new Base44Integration(config.base44 || {}),
    openai: new OpenAIIntegration(config.openai || {}),
    grok: new GrokIntegration(config.grok || {}),
    replit: new ReplitIntegration(config.replit || {}),
    web3: new Web3Integration(config.web3 || {}),
    github: new GitHubIntegration(config.github || {}),
    webhook: new WebhookIntegration(config.webhooks || {}),
  };
}

async function healthCheck(integrations) {
  const results = {};

  if (integrations.base44.apiKey) {
    try {
      await integrations.base44.getAppStatus();
      results.base44 = "ok";
    } catch (err) {
      results.base44 = `error: ${err.message}`;
    }
  } else {
    results.base44 = "skipped (no API key)";
  }

  if (integrations.grok.apiKey) {
    try {
      await integrations.grok.listModels();
      results.grok = "ok";
    } catch (err) {
      results.grok = `error: ${err.message}`;
    }
  } else {
    results.grok = "skipped (no API key)";
  }

  if (integrations.web3.rpcUrl) {
    try {
      const block = await integrations.web3.getBlockNumber();
      results.web3 = `ok (block ${block})`;
    } catch (err) {
      results.web3 = `error: ${err.message}`;
    }
  } else {
    results.web3 = "skipped (no RPC URL)";
  }

  return results;
}

if (require.main === module) {
  (async () => {
    const config = loadConfig();
    const integrations = createIntegrations(config);
    console.log("Running health check...");
    const results = await healthCheck(integrations);
    console.log("Health check results:", JSON.stringify(results, null, 2));
  })();
}

module.exports = { createIntegrations, loadConfig, healthCheck };
