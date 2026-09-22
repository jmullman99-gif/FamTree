import asyncio

import pytest
from genealogy_mcp.server import create_server


def test_server_creates():
    """Server instance is created without error."""
    mcp = create_server()
    assert mcp is not None
    assert mcp.name == "genealogy"


def test_all_tools_registered():
    """All 19 tools are registered."""
    mcp = create_server()
    tools = asyncio.run(mcp.list_tools())
    tool_names = sorted(t.name for t in tools)
    expected = sorted([
        "gedcom_load", "gedcom_search", "gedcom_person", "gedcom_family",
        "gedcom_ancestors", "gedcom_descendants", "gedcom_stats",
        "wikitree_search", "wikitree_profile", "wikitree_relatives",
        "wikitree_ancestors", "wikitree_descendants", "wikitree_bio",
        "newspaper_search", "newspaper_page",
        "archives_search",
        "findagrave_search", "findagrave_memorial",
        "cross_reference",
    ])
    assert tool_names == expected, f"Missing or extra tools: {set(expected) ^ set(tool_names)}"
