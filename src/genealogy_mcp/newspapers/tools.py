"""Chronicling America MCP tools — 2 tools for US newspaper archives (1789–1963)."""
from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

from genealogy_mcp.newspapers import client


def _get_http(ctx: Context) -> Any:
    return ctx.request_context.lifespan_context.http


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="newspaper_search",
        description="Search US newspapers (1789–1963) via Chronicling America (Library of Congress). Returns pages with OCR text snippets.",
    )
    async def newspaper_search(
        ctx: Context,
        query: str,
        state: str = "",
        date_start: str = "",
        date_end: str = "",
        page: int = 1,
        rows: int = 20,
    ) -> list[TextContent]:
        try:
            result = await client.search_pages(
                _get_http(ctx),
                query=query,
                state=state,
                date_start=date_start,
                date_end=date_end,
                page=page,
                rows=rows,
            )
        except Exception as e:
            return [TextContent(type="text", text=f"Newspaper search failed: {e}")]
        total = result.get("totalItems", 0)
        items = result.get("items", [])
        if not items:
            return [TextContent(type="text", text=f"No newspaper results found for '{query}'.")]
        summary = {
            "total_results": total,
            "showing": len(items),
            "results": [
                {
                    "title": item.get("title", ""),
                    "date": item.get("date", ""),
                    "city": item.get("city", []),
                    "state": item.get("state", []),
                    "page_url": item.get("id", ""),
                    "snippet": (item.get("ocr_eng", "") or "")[:500],
                }
                for item in items
            ],
        }
        return [TextContent(type="text", text=json.dumps(summary, indent=2))]

    @mcp.tool(
        name="newspaper_page",
        description="Get full OCR text for a newspaper page. Use the page_url from newspaper_search results.",
    )
    async def newspaper_page(ctx: Context, url: str) -> list[TextContent]:
        try:
            text = await client.get_page_ocr(_get_http(ctx), url=url)
        except Exception as e:
            return [TextContent(type="text", text=f"Failed to get page: {e}")]
        return [TextContent(type="text", text=text)]
