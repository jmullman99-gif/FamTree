from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from mcp.server.fastmcp import FastMCP


@dataclass
class AppContext:
    """Shared state available to all tools via ctx.request_context.lifespan_context."""

    http: httpx.AsyncClient


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30.0,
        headers={"User-Agent": "genealogy-mcp/0.1.0 (https://github.com/jmullman99-gif/genealogy-mcp)"},
    ) as http:
        yield AppContext(http=http)


def create_server() -> FastMCP:
    mcp = FastMCP("genealogy", lifespan=lifespan)

    from genealogy_mcp.gedcom.tools import register as register_gedcom
    register_gedcom(mcp)

    from genealogy_mcp.wikitree.tools import register as register_wikitree
    register_wikitree(mcp)

    from genealogy_mcp.newspapers.tools import register as register_newspapers
    from genealogy_mcp.archives.tools import register as register_archives
    register_newspapers(mcp)
    register_archives(mcp)

    from genealogy_mcp.findagrave.tools import register as register_findagrave
    register_findagrave(mcp)

    from genealogy_mcp.crossref import register as register_crossref
    register_crossref(mcp)

    return mcp
