"""Find A Grave MCP tools — 2 tools for searching memorials and grave records."""
from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

from genealogy_mcp.findagrave import client


def _get_http(ctx: Context) -> Any:
    return ctx.request_context.lifespan_context.http


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="findagrave_search",
        description="Search Find A Grave for memorials by name, birth/death year, and location. Returns memorial IDs, names, dates, cemetery, and location.",
    )
    async def findagrave_search(
        ctx: Context,
        lastname: str,
        firstname: str = "",
        birth_year: str = "",
        death_year: str = "",
        location: str = "",
        page: int = 1,
    ) -> list[TextContent]:
        try:
            result = await client.search_memorials(
                _get_http(ctx),
                firstname=firstname,
                lastname=lastname,
                birth_year=birth_year,
                death_year=death_year,
                location=location,
                page=page,
            )
        except Exception as e:
            return [TextContent(type="text", text=f"Find A Grave error: {e}")]
        if not result["results"]:
            return [TextContent(type="text", text="No memorials found matching those criteria on Find A Grave.")]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    @mcp.tool(
        name="findagrave_memorial",
        description="Get full details for a Find A Grave memorial by its memorial ID. Returns name, dates, cemetery, location, biography/inscription, and plot info.",
    )
    async def findagrave_memorial(ctx: Context, memorial_id: str) -> list[TextContent]:
        try:
            result = await client.get_memorial(_get_http(ctx), memorial_id=memorial_id)
        except Exception as e:
            return [TextContent(type="text", text=f"Find A Grave error: {e}")]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
