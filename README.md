# ClawBase44.ai.Bots

> **Autonomous Automation Applications** — adding depth, diversity, efficiency, and flexibility to Base44 and beyond.  
> Build custom workflows with ChatGPT, Grok, Web3, ManyChat, affiliate programs, BotBuilders, Replit, and more.

[![CI](https://github.com/lippytm/ClawBase44.ai.Bots/actions/workflows/ci.yml/badge.svg)](https://github.com/lippytm/ClawBase44.ai.Bots/actions/workflows/ci.yml)

---

## Features

| Module | Description |
|--------|-------------|
| **Core framework** | `BaseBot` abstract class, pluggable `WorkflowEngine`, APScheduler-backed `BotScheduler` |
| **ChatGPT integration** | OpenAI Chat Completions — single-turn chat & content generation helper |
| **Grok / xAI integration** | xAI Grok endpoint (OpenAI-compatible) — market analysis & general chat |
| **ManyChat integration** | Send messages, trigger flows, and broadcast to subscriber segments |
| **Web3 adapter** | Check balances, send ETH, call smart contracts via web3.py |
| **Content-gen workflow** | ChatGPT draft → Grok review → ChatGPT refinement pipeline |
| **Social-media workflow** | AI-generated post → ManyChat broadcast |
| **Affiliate workflow** | AI product copy with automatic affiliate tag injection |
| **CLI** | `clawbase` Typer CLI with sub-commands for every workflow |

---

## Quick Start

### 1 — Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 2 — Configure

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3 — Use the CLI

```bash
# Generate a blog post with ChatGPT + Grok review
clawbase content generate "Top 5 AI automation tools in 2024" --type "blog post" --words 400

# Generate affiliate product review with auto-tagged links
clawbase affiliate generate "Jasper AI" --tag "mysite-20"

# Broadcast a social post via ManyChat
clawbase social broadcast "New AI features" --flow "content20240101_post0"

# Check your Web3 wallet balance
clawbase web3 balance

# Web3 provider status
clawbase web3 status
```

---

## Project Layout

```
src/
  core/
    base_bot.py        # Abstract BaseBot
    workflow.py        # Step, Workflow, WorkflowEngine
    scheduler.py       # BotScheduler (APScheduler wrapper)
  integrations/
    chatgpt.py         # OpenAI / ChatGPT client
    grok.py            # Grok / xAI client
    manychat.py        # ManyChat REST client
    web3_adapter.py    # Web3 on-chain adapter
  workflows/
    content_gen.py     # ChatGPT + Grok content pipeline
    social_media.py    # AI post → ManyChat broadcast
    affiliate.py       # AI copy + affiliate tag injection
  cli.py               # Typer CLI entry point
config/
  settings.py          # Pydantic Settings (reads .env)
tests/                 # pytest test suite
.github/workflows/
  ci.yml               # GitHub Actions CI (lint + test)
```

---

## Extending with a Custom Bot

```python
from src.core.base_bot import BaseBot

class MyBot(BaseBot):
    def __init__(self):
        super().__init__(name="my-bot")

    async def run(self, context: dict) -> dict:
        # Your automation logic here
        return {"status": "done"}

# Run it
import asyncio
bot = MyBot()
result = asyncio.run(bot.execute({"seed": "data"}))
```

---

## Running Tests

```bash
pytest --cov=src --cov=config -v
```

---

## License

[Boost Software License 1.0](LICENSE)
