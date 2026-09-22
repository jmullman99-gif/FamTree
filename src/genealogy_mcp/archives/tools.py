"""Open Archives MCP tools — 1 tool for Dutch/Belgian/French historical records."""
from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

from genealogy_mcp.archives import client


def _get_http(ctx: Context) -> Any:
    return ctx.request_context.lifespan_context.http


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="archives_search",
        description="Search Open Archives (openarchieven.nl) for Dutch, Belgian, and French historical records — birth, marriage, death registrations.",
    )
    async def archives_search(
        ctx: Context,
        name: str,
        place: str = "",
        number_show: int = 20,
        start: int = 0,
    ) -> list[TextContent]:
        try:
            result = await client.search_records(
                _get_http(ctx), name=name, place=place, number_show=number_show, start=start
            )
        except Exception as e:
            return [TextContent(type="text", text=f"Archives search failed: {e}")]
        response = result.get("response", {})
        total = response.get("number_found", 0)
        docs = response.get("docs", [])
        if not docs:
            return [TextContent(type="text", text=f"No archive records found for '{name}'.")]
        summary = {
            "total_results": total,
            "showing": len(docs),
            "results": [
                {
                    "name": doc.get("personname", ""),
                    "event_type": doc.get("eventtype", ""),
                    "event_date": doc.get("eventdate", {}),
                    "event_place": doc.get("eventplace", []),
                    "archive": doc.get("archive_org", ""),
                    "source_type": doc.get("sourcetype", ""),
                    "url": doc.get("url", ""),
                }
                for doc in docs
            ],
        }
        return [TextContent(type="text", text=json.dumps(summary, indent=2))]
