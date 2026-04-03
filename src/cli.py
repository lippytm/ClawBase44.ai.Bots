"""Typer-based CLI entry point for ClawBase44.ai.Bots."""

from __future__ import annotations

import asyncio
import logging

import typer
from rich.console import Console
from rich.logging import RichHandler

app = typer.Typer(
    name="clawbase",
    help="ClawBase44.ai.Bots — Autonomous Automation CLI",
    no_args_is_help=True,
)
console = Console()


def _setup_logging(debug: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
        format="%(message)s",
        datefmt="[%X]",
    )


# ── Content Generation ────────────────────────────────────────────────

content_app = typer.Typer(help="AI content-generation commands")
app.add_typer(content_app, name="content")


@content_app.command("generate")
def content_generate(
    topic: str = typer.Argument(..., help="Topic to write about"),
    content_type: str = typer.Option("blog post", "--type", "-t", help="Content type"),
    tone: str = typer.Option("professional", "--tone", help="Writing tone"),
    word_count: int = typer.Option(300, "--words", "-w", help="Target word count"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Generate AI content via the ChatGPT + Grok pipeline."""
    _setup_logging(debug)
    from src.workflows.content_gen import ContentGenerationWorkflow

    async def _run() -> None:
        wf = ContentGenerationWorkflow()
        result = await wf.run(
            topic=topic, content_type=content_type, tone=tone, word_count=word_count
        )
        console.rule("[bold green]Final Content")
        console.print(result.get("final_content") or result.get("draft", ""))

    asyncio.run(_run())


# ── Affiliate ────────────────────────────────────────────────────────

affiliate_app = typer.Typer(help="Affiliate content commands")
app.add_typer(affiliate_app, name="affiliate")


@affiliate_app.command("generate")
def affiliate_generate(
    product: str = typer.Argument(..., help="Product or service to promote"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Affiliate tag (overrides settings)"),
    content_type: str = typer.Option("product review", "--type", help="Content type"),
    word_count: int = typer.Option(400, "--words", "-w"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Generate affiliate-tagged content for a product."""
    _setup_logging(debug)
    from src.workflows.affiliate import AffiliateWorkflow

    async def _run() -> None:
        wf = AffiliateWorkflow()
        result = await wf.run(
            product=product, affiliate_tag=tag, content_type=content_type, word_count=word_count
        )
        console.rule("[bold green]Affiliate Content")
        console.print(result.get("affiliate_content", ""))

    asyncio.run(_run())


# ── Social Media ─────────────────────────────────────────────────────

social_app = typer.Typer(help="Social media broadcast commands")
app.add_typer(social_app, name="social")


@social_app.command("broadcast")
def social_broadcast(
    topic: str = typer.Argument(..., help="Topic of the social post"),
    flow_ns: str = typer.Option(..., "--flow", "-f", help="ManyChat flow namespace"),
    audience_tag: str | None = typer.Option(None, "--tag", "-t", help="ManyChat audience tag"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Generate a social post and broadcast it via ManyChat."""
    _setup_logging(debug)
    from src.workflows.social_media import SocialMediaWorkflow

    async def _run() -> None:
        wf = SocialMediaWorkflow()
        result = await wf.run(topic=topic, flow_ns=flow_ns, audience_tag=audience_tag)
        console.rule("[bold green]Broadcast Result")
        console.print_json(data=result.get("broadcast_result", {}))

    asyncio.run(_run())


# ── Web3 ──────────────────────────────────────────────────────────────

web3_app = typer.Typer(help="Web3 on-chain utilities")
app.add_typer(web3_app, name="web3")


@web3_app.command("balance")
def web3_balance(
    address: str | None = typer.Argument(
        None, help="Ethereum address (defaults to wallet in .env)"
    ),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
    """Check ETH balance for an address."""
    _setup_logging(debug)
    from src.integrations.web3_adapter import Web3Adapter

    adapter = Web3Adapter()
    balance = adapter.get_balance(address)
    console.print(f"Balance: [bold cyan]{balance:.6f} ETH[/bold cyan]")


@web3_app.command("status")
def web3_status(debug: bool = typer.Option(False, "--debug")) -> None:
    """Show Web3 provider connection status and latest block."""
    _setup_logging(debug)
    from src.integrations.web3_adapter import Web3Adapter

    adapter = Web3Adapter()
    connected = adapter.is_connected
    block = adapter.get_block_number() if connected else "N/A"
    gas = adapter.get_gas_price_gwei() if connected else "N/A"
    console.print(f"Connected: [{'green' if connected else 'red'}]{connected}[/]")
    console.print(f"Block:     {block}")
    console.print(f"Gas:       {gas} Gwei")


if __name__ == "__main__":
    app()
