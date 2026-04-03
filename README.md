# ClawBase44.ai.Bots

Adding depth, diversity, efficiency, and flexibility to Base44 and related repositories — enabling custom applications and automated workflows with **ChatGPT**, **Grok**, **Replit**, **Web3**, and more.

---

## Overview

This repository provides a modular integration layer that connects GitHub workflows to external services and platforms. Each integration is available as:

- A **Node.js module** under `src/integrations/` for programmatic use
- A **GitHub Actions workflow** under `.github/workflows/` for automation

---

## Integrations

| Service | Module | Workflow | Trigger |
|---|---|---|---|
| **GitHub Repositories** | `src/integrations/github.js` | `repository-sync.yml` | push to `main` / `workflow_dispatch` |
| **Base44** | `src/integrations/base44.js` | `base44-integration.yml` | `workflow_dispatch` / `repository_dispatch` |
| **OpenAI / ChatGPT** | `src/integrations/openai.js` | `openai-integration.yml` | `workflow_dispatch` / `repository_dispatch` |
| **ChatGPT Assistants (Bots)** | `src/integrations/openai.js` | `openai-integration.yml` | `workflow_dispatch` (mode: assistant) |
| **Grok (xAI)** | `src/integrations/grok.js` | `grok-integration.yml` | `workflow_dispatch` / `repository_dispatch` |
| **Replit** | `src/integrations/replit.js` | `replit-integration.yml` | `workflow_dispatch` / `repository_dispatch` |
| **Web3 / Blockchain** | `src/integrations/web3.js` | `web3-integration.yml` | `workflow_dispatch` / `repository_dispatch` |
| **Generic Webhooks** | `src/integrations/webhook.js` | `integration-dispatch.yml` | any of the above |

---

## Quick Start

### 1. Install dependencies

```bash
npm install
```

### 2. Configure integrations

Copy the example config and fill in your credentials:

```bash
cp config/integrations.example.json config/integrations.json
# Edit config/integrations.json — this file is git-ignored
```

Or set the equivalent environment variables (see [Environment Variables](#environment-variables)).

### 3. Run the health check

```bash
npm start
```

### 4. Use as a library

```js
const { createIntegrations } = require('./src/index');

const integrations = createIntegrations({
  openai: { apiKey: process.env.OPENAI_API_KEY },
  grok:   { apiKey: process.env.XAI_API_KEY },
});

// ChatGPT chat completion
const result = await integrations.openai.chat([
  { role: 'user', content: 'Hello from ClawBase44!' }
]);
console.log(result.choices[0].message.content);

// Grok query
const grokResult = await integrations.grok.chat([
  { role: 'user', content: 'Explain Web3 in one sentence.' }
]);
console.log(grokResult.choices[0].message.content);

// Broadcast event to downstream GitHub repos
await integrations.github.broadcastDispatch('upstream-sync', { sha: '...' });

// Trigger a Base44 workflow
await integrations.base44.triggerWorkflow('my-workflow-id', { key: 'value' });

// Query latest blockchain block
const block = await integrations.web3.getBlockNumber();
console.log('Latest block:', block);
```

---

## GitHub Actions Workflows

### Integration Dispatch (`integration-dispatch.yml`)

Broadcasts an event to one or all configured integrations.

**Trigger:** `workflow_dispatch` or `repository_dispatch` (type: `integration-trigger`)

**Inputs:**
| Input | Description | Default |
|---|---|---|
| `service` | Target service (`base44`, `openai`, `grok`, `replit`, `web3`, `github`, `all`) | `all` |
| `event` | Event name to broadcast | `workflow_run` |
| `payload` | JSON payload | `{}` |

---

### Repository Sync (`repository-sync.yml`)

Fires a `repository_dispatch` event to all downstream repos listed in the `DOWNSTREAM_REPOS` secret whenever code is pushed to `main`.

**Secrets required:** `REPO_SYNC_TOKEN`, `DOWNSTREAM_REPOS` (comma-separated `owner/repo` list)

---

### Base44 Integration (`base44-integration.yml`)

Triggers a workflow in your Base44 app.

**Secrets required:** `BASE44_API_KEY`, `BASE44_APP_ID`

**Inputs:** `workflow_id`, `payload`

---

### OpenAI / ChatGPT Integration (`openai-integration.yml`)

Sends a message via the Chat Completions API or the Assistants API (for ChatGPT Bots).

**Secrets required:** `OPENAI_API_KEY`; optionally `CHATGPT_ASSISTANT_ID`, `OPENAI_MODEL`

**Inputs:** `mode` (`chat` | `assistant`), `prompt`, `assistant_id`

---

### Grok Integration (`grok-integration.yml`)

Queries Grok via the xAI API (OpenAI-compatible).

**Secrets required:** `XAI_API_KEY`

**Inputs:** `prompt`, `model`

---

### Replit Integration (`replit-integration.yml`)

Interacts with Replit repls (status, run, list).

**Secrets required:** `REPLIT_API_KEY`, `REPLIT_REPL_ID`

**Inputs:** `action` (`run` | `list` | `status`), `repl_id`

---

### Web3 Integration (`web3-integration.yml`)

Queries an EVM-compatible blockchain via JSON-RPC (no wallet required for read-only calls).

**Secrets required:** `WEB3_RPC_URL`; optionally `WEB3_CHAIN_ID`, `WEB3_CONTRACT_ADDRESS`

**Inputs:** `action` (`block` | `balance` | `chainid`), `address`

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `GITHUB_TOKEN` | GitHub | Personal access token or Actions token |
| `DOWNSTREAM_REPOS` | GitHub Sync | Comma-separated list of `owner/repo` to notify |
| `BASE44_API_KEY` | Base44 | API key from Base44 dashboard |
| `BASE44_APP_ID` | Base44 | Application ID |
| `OPENAI_API_KEY` | OpenAI / ChatGPT | OpenAI API key |
| `OPENAI_MODEL` | OpenAI | Model to use (default: `gpt-4o`) |
| `CHATGPT_ASSISTANT_ID` | ChatGPT Bots | Assistants API assistant ID |
| `XAI_API_KEY` | Grok | xAI API key |
| `GROK_MODEL` | Grok | Model to use (default: `grok-3`) |
| `REPLIT_API_KEY` | Replit | Replit API key |
| `REPLIT_REPL_ID` | Replit | Default Repl ID |
| `WEB3_RPC_URL` | Web3 | JSON-RPC endpoint (e.g. Infura/Alchemy) |
| `WEB3_CHAIN_ID` | Web3 | Chain ID (default: `1` = Ethereum mainnet) |
| `WEB3_CONTRACT_ADDRESS` | Web3 | Default contract address |
| `WEBHOOK_SECRET` | Webhooks | HMAC-SHA256 secret for incoming webhooks |

---

## Repository Structure

```
.github/workflows/          # GitHub Actions integration workflows
  integration-dispatch.yml
  repository-sync.yml
  base44-integration.yml
  openai-integration.yml
  grok-integration.yml
  replit-integration.yml
  web3-integration.yml

src/
  integrations/             # Service connector modules
    base44.js
    openai.js
    grok.js
    replit.js
    web3.js
    github.js
    webhook.js
  index.js                  # Main entry point / health check

config/
  integrations.example.json # Configuration template (copy → integrations.json)

package.json
.gitignore
README.md
LICENSE
```

---

## Security

- **Never** commit `config/integrations.json` or any file containing real API keys.
- Store all secrets in **GitHub repository secrets** (Settings → Secrets and variables → Actions).
- Incoming webhook signatures are verified with HMAC-SHA256 via `WebhookIntegration.verifySignature()`.

---

## License

MIT — see [LICENSE](LICENSE).

