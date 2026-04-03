"""Tests for the AffiliateWorkflow URL tag injection (no API calls)."""

from __future__ import annotations

import re


def _inject_tag(text: str, tag: str) -> str:
    """Mirror of the injection logic in AffiliateWorkflow."""
    _URL_RE = re.compile(r"https?://[^\s\"'<>]+(?<![.,;:!?)])")

    def _append(match: re.Match) -> str:
        url = match.group(0)
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}tag={tag}"

    return _URL_RE.sub(_append, text)


def test_tag_injected_into_plain_url() -> None:
    text = "Check it out at https://example.com/product."
    result = _inject_tag(text, "myref-20")
    assert "tag=myref-20" in result
    assert "https://example.com/product?tag=myref-20" in result


def test_tag_injected_with_existing_query_params() -> None:
    text = "Visit https://example.com/item?color=blue for details."
    result = _inject_tag(text, "myref-20")
    assert "https://example.com/item?color=blue&tag=myref-20" in result


def test_multiple_urls_all_tagged() -> None:
    text = "See https://a.com and https://b.com for info."
    result = _inject_tag(text, "x-20")
    assert result.count("tag=x-20") == 2


def test_no_url_unchanged() -> None:
    text = "No links here, just plain text."
    result = _inject_tag(text, "myref-20")
    assert result == text
