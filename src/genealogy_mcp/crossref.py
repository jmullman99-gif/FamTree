"""Cross-reference tool — searches all genealogy sources in parallel."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

from genealogy_mcp.archives import client as archives_client
from genealogy_mcp.newspapers import client as newspapers_client
from genealogy_mcp.wikitree import client as wikitree_client


async def _search_wikitree(http: Any, name: str, birth_year: str, death_year: str, birth_place: str) -> dict:
    parts = name.strip().split()
    first_name = parts[0] if parts else ""
    last_name = parts[-1] if len(parts) > 1 else parts[0] if parts else ""
    try:
        matches = await wikitree_client.search_person(
            http,
            last_name=last_name,
            first_name=first_name if len(parts) > 1 else "",
            birth_date=birth_year,
            death_date=death_year,
            birth_location=birth_place,
            limit=10,
        )
        return {"wikitree": matches}
    except Exception as e:
        return {"wikitree": [], "wikitree_error": str(e)}


async def _search_newspapers(http: Any, name: str, birth_year: str, birth_place: str) -> dict:
    try:
        # Search for name, optionally filtered by state (extracted from birth_place)
        state = ""
        if birth_place:
            # Try to extract US state from place string
            parts = [p.strip() for p in birth_place.split(",")]
            if len(parts) >= 2:
                state = parts[-1] if len(parts[-1]) > 2 else parts[-2] if len(parts) >= 2 else ""
        date_start = str(int(birth_year) - 5) if birth_year.isdigit() else ""
        date_end = str(int(birth_year) + 80) if birth_year.isdigit() else ""
        result = await newspapers_client.search_pages(
            http, query=name, state=state, date_start=date_start, date_end=date_end, rows=10
        )
        items = result.get("items", [])
        return {
            "newspapers": [
                {
                    "title": item.get("title", ""),
                    "date": item.get("date", ""),
                    "page_url": item.get("id", ""),
                    "snippet": (item.get("ocr_eng", "") or "")[:300],
                }
                for item in items
            ]
        }
    except Exception as e:
        return {"newspapers": [], "newspapers_error": str(e)}


async def _search_archives(http: Any, name: str, place: str) -> dict:
    try:
        result = await archives_client.search_records(http, name=name, place=place, number_show=10)
        docs = result.get("response", {}).get("docs", [])
        return {
            "archives": [
                {
                    "name": doc.get("personname", ""),
                    "event_type": doc.get("eventtype", ""),
                    "event_date": doc.get("eventdate", {}),
                    "event_place": doc.get("eventplace", []),
                    "archive": doc.get("archive_org", ""),
                    "url": doc.get("url", ""),
                }
                for doc in docs
            ]
        }
    except Exception as e:
        return {"archives": [], "archives_error": str(e)}


async def _cross_reference(
    http: Any,
    name: str,
    birth_year: str = "",
    birth_place: str = "",
    death_year: str = "",
) -> str:
    """Search all sources in parallel and return consolidated results."""
    results = await asyncio.gather(
        _search_wikitree(http, name, birth_year, death_year, birth_place),
        _search_newspapers(http, name, birth_year, birth_place),
        _search_archives(http, name, birth_place),
    )

    merged: dict = {}
    for r in results:
        for key, value in r.items():
            if key.endswith("_error"):
                # Attach error to the source key
                source = key.replace("_error", "")
                if source in merged:
                    merged[source] = {"error": value, "results": []}
                else:
                    merged[source] = {"error": value}
            else:
                merged[key] = value

    # Ensure all sources present
    for source in ("wikitree", "newspapers", "archives"):
        if source not in merged:
            merged[source] = []

    return json.dumps(merged, indent=2)


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="cross_reference",
        description="Search WikiTree, Chronicling America, and Open Archives in parallel for a person. Returns consolidated results from all sources.",
    )
    async def cross_reference(
        ctx: Context,
        name: str,
        birth_year: str = "",
        birth_place: str = "",
        death_year: str = "",
    ) -> list[TextContent]:
        http = ctx.request_context.lifespan_context.http
        result = await _cross_reference(http, name, birth_year, birth_place, death_year)
        return [TextContent(type="text", text=result)]
