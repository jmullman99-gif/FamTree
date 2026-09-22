"""WikiTree MCP tools — 6 tools for searching WikiTree's 42M+ profiles."""
from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

from genealogy_mcp.wikitree import client


def _get_http(ctx: Context) -> Any:
    return ctx.request_context.lifespan_context.http


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="wikitree_search",
        description="Search WikiTree for a person by last name, first name, dates, and location. Returns up to `limit` matching profiles.",
    )
    async def wikitree_search(
        ctx: Context,
        last_name: str,
        first_name: str = "",
        birth_date: str = "",
        death_date: str = "",
        birth_location: str = "",
        limit: int = 10,
    ) -> list[TextContent]:
        try:
            matches = await client.search_person(
                _get_http(ctx),
                last_name=last_name,
                first_name=first_name,
                birth_date=birth_date,
                death_date=death_date,
                birth_location=birth_location,
                limit=limit,
            )
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        if not matches:
            return [TextContent(type="text", text="No WikiTree profiles found matching those criteria.")]
        return [TextContent(type="text", text=json.dumps(matches, indent=2))]

    @mcp.tool(
        name="wikitree_profile",
        description="Get a WikiTree profile by WikiTree ID (e.g. 'Smith-12345'). Returns name, dates, locations, and family links.",
    )
    async def wikitree_profile(ctx: Context, key: str) -> list[TextContent]:
        try:
            profile = await client.get_profile(_get_http(ctx), key=key)
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        return [TextContent(type="text", text=json.dumps(profile, indent=2))]

    @mcp.tool(
        name="wikitree_relatives",
        description="Get relatives for a WikiTree profile. Specify which relationships to include: parents, children, siblings, spouses.",
    )
    async def wikitree_relatives(
        ctx: Context,
        key: str,
        get_parents: bool = True,
        get_children: bool = True,
        get_siblings: bool = False,
        get_spouses: bool = True,
    ) -> list[TextContent]:
        try:
            result = await client.get_relatives(
                _get_http(ctx),
                key=key,
                get_parents=get_parents,
                get_children=get_children,
                get_siblings=get_siblings,
                get_spouses=get_spouses,
            )
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    @mcp.tool(
        name="wikitree_ancestors",
        description="Get ancestor tree for a WikiTree profile. Returns all ancestors to the specified depth (default 5 generations).",
    )
    async def wikitree_ancestors(ctx: Context, key: str, depth: int = 5) -> list[TextContent]:
        try:
            ancestors = await client.get_ancestors(_get_http(ctx), key=key, depth=depth)
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        if not ancestors:
            return [TextContent(type="text", text="No ancestors found.")]
        return [TextContent(type="text", text=json.dumps(ancestors, indent=2))]

    @mcp.tool(
        name="wikitree_descendants",
        description="Get descendant tree for a WikiTree profile. Returns all descendants to the specified depth (default 3 generations).",
    )
    async def wikitree_descendants(ctx: Context, key: str, depth: int = 3) -> list[TextContent]:
        try:
            descendants = await client.get_descendants(_get_http(ctx), key=key, depth=depth)
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        if not descendants:
            return [TextContent(type="text", text="No descendants found.")]
        return [TextContent(type="text", text=json.dumps(descendants, indent=2))]

    @mcp.tool(
        name="wikitree_bio",
        description="Get the full biography text for a WikiTree profile. This is where sourced narratives and citations live.",
    )
    async def wikitree_bio(ctx: Context, key: str) -> list[TextContent]:
        try:
            result = await client.get_bio(_get_http(ctx), key=key)
        except client.WikiTreeAPIError as e:
            return [TextContent(type="text", text=f"WikiTree error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Request failed: {e}")]
        bio_text = result.get("bio", "No biography available.")
        return [TextContent(type="text", text=bio_text)]
