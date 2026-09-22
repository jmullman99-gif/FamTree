"""GEDCOM MCP tools — 7 tools for loading and querying local .ged files."""
from __future__ import annotations

import json
from collections import Counter

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from genealogy_mcp.gedcom.models import GedcomFile, Individual
from genealogy_mcp.gedcom.parser import parse_gedcom

_loaded: GedcomFile | None = None


def _indi_to_dict(indi: Individual) -> dict:
    return {
        "xref_id": indi.xref_id,
        "name": indi.name,
        "given_name": indi.given_name,
        "surname": indi.surname,
        "sex": indi.sex,
        "birth_date": indi.birth_date,
        "birth_place": indi.birth_place,
        "death_date": indi.death_date,
        "death_place": indi.death_place,
        "occupation": indi.occupation,
    }


# ── Sync helpers (for testing without MCP context) ──────────────

def _load_sync(file_path: str) -> str:
    global _loaded
    try:
        _loaded = parse_gedcom(file_path)
    except FileNotFoundError as e:
        return f"Error: {e}"
    n_indi = len(_loaded.individuals)
    n_fam = len(_loaded.families)
    return f"Loaded {n_indi} individuals and {n_fam} families from {file_path}"


def _search_sync(
    name: str = "",
    birth_year: str = "",
    birth_place: str = "",
    death_year: str = "",
    sex: str = "",
) -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    matches = []
    for indi in _loaded.individuals.values():
        if name and name.lower() not in indi.name.lower():
            continue
        if sex and indi.sex.upper() != sex.upper():
            continue
        if birth_year and birth_year not in indi.birth_date:
            continue
        if birth_place and birth_place.lower() not in indi.birth_place.lower():
            continue
        if death_year and death_year not in indi.death_date:
            continue
        matches.append(_indi_to_dict(indi))
    if not matches:
        return "No individuals found matching those criteria in the loaded GEDCOM file."
    return json.dumps(matches, indent=2)


def _person_sync(xref_id: str) -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    indi = _loaded.individuals.get(xref_id)
    if indi is None:
        return f"Person not found: {xref_id}"
    return json.dumps(_indi_to_dict(indi), indent=2)


def _family_sync(xref_id: str) -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    fam = _loaded.families.get(xref_id)
    if fam is None:
        return f"Family not found: {xref_id}"
    husband = _loaded.individuals.get(fam.husband_id or "")
    wife = _loaded.individuals.get(fam.wife_id or "")
    children = [
        _loaded.individuals.get(cid)
        for cid in fam.child_ids
        if _loaded.individuals.get(cid)
    ]
    result = {
        "xref_id": fam.xref_id,
        "husband": husband.name if husband else None,
        "husband_id": fam.husband_id,
        "wife": wife.name if wife else None,
        "wife_id": fam.wife_id,
        "marriage_date": fam.marriage_date,
        "marriage_place": fam.marriage_place,
        "children": [
            {"name": c.name, "xref_id": c.xref_id} for c in children
        ],
    }
    return json.dumps(result, indent=2)


def _ancestors_sync(xref_id: str, depth: int = 4) -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    if xref_id not in _loaded.individuals:
        return f"Person not found: {xref_id}"
    ancestors: list[dict] = []
    queue: list[tuple[str, int]] = [(xref_id, 0)]
    seen: set[str] = set()
    while queue:
        pid, gen = queue.pop(0)
        if pid in seen or gen > depth:
            continue
        seen.add(pid)
        indi = _loaded.individuals.get(pid)
        if indi is None:
            continue
        if gen > 0:
            entry = _indi_to_dict(indi)
            entry["generation"] = gen
            ancestors.append(entry)
        for fam_id in indi.famc:
            fam = _loaded.families.get(fam_id)
            if fam:
                if fam.husband_id:
                    queue.append((fam.husband_id, gen + 1))
                if fam.wife_id:
                    queue.append((fam.wife_id, gen + 1))
    return json.dumps(ancestors, indent=2)


def _descendants_sync(xref_id: str, depth: int = 4) -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    if xref_id not in _loaded.individuals:
        return f"Person not found: {xref_id}"
    descendants: list[dict] = []
    queue: list[tuple[str, int]] = [(xref_id, 0)]
    seen: set[str] = set()
    while queue:
        pid, gen = queue.pop(0)
        if pid in seen or gen > depth:
            continue
        seen.add(pid)
        indi = _loaded.individuals.get(pid)
        if indi is None:
            continue
        if gen > 0:
            entry = _indi_to_dict(indi)
            entry["generation"] = gen
            descendants.append(entry)
        for fam_id in indi.fams:
            fam = _loaded.families.get(fam_id)
            if fam:
                for cid in fam.child_ids:
                    queue.append((cid, gen + 1))
    return json.dumps(descendants, indent=2)


def _stats_sync() -> str:
    if _loaded is None:
        return "No GEDCOM file loaded. Use gedcom_load first."
    surname_counts = Counter(
        indi.surname for indi in _loaded.individuals.values() if indi.surname
    )
    return json.dumps(
        {
            "individuals": len(_loaded.individuals),
            "families": len(_loaded.families),
            "surnames": dict(surname_counts.most_common(20)),
            "encoding": _loaded.encoding,
        },
        indent=2,
    )


# ── MCP tool registration ──────────────────────────────────────

def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="gedcom_load",
        description="Load a GEDCOM (.ged) file into memory. Required before using other gedcom_* tools.",
    )
    async def gedcom_load(file_path: str) -> list[TextContent]:
        return [TextContent(type="text", text=_load_sync(file_path))]

    @mcp.tool(
        name="gedcom_search",
        description="Search for people in the loaded GEDCOM file by name, birth year, birth place, death year, or sex.",
    )
    async def gedcom_search(
        name: str = "",
        birth_year: str = "",
        birth_place: str = "",
        death_year: str = "",
        sex: str = "",
    ) -> list[TextContent]:
        return [TextContent(type="text", text=_search_sync(name, birth_year, birth_place, death_year, sex))]

    @mcp.tool(
        name="gedcom_person",
        description="Get full details for one person by their GEDCOM xref ID (e.g. '@I1@').",
    )
    async def gedcom_person(xref_id: str) -> list[TextContent]:
        return [TextContent(type="text", text=_person_sync(xref_id))]

    @mcp.tool(
        name="gedcom_family",
        description="Get a family group (husband, wife, children) by GEDCOM family xref ID (e.g. '@F1@').",
    )
    async def gedcom_family(xref_id: str) -> list[TextContent]:
        return [TextContent(type="text", text=_family_sync(xref_id))]

    @mcp.tool(
        name="gedcom_ancestors",
        description="Get ancestor tree for a person by xref ID. BFS traversal to configurable depth.",
    )
    async def gedcom_ancestors(xref_id: str, depth: int = 4) -> list[TextContent]:
        return [TextContent(type="text", text=_ancestors_sync(xref_id, depth))]

    @mcp.tool(
        name="gedcom_descendants",
        description="Get descendant tree for a person by xref ID. BFS traversal to configurable depth.",
    )
    async def gedcom_descendants(xref_id: str, depth: int = 4) -> list[TextContent]:
        return [TextContent(type="text", text=_descendants_sync(xref_id, depth))]

    @mcp.tool(
        name="gedcom_stats",
        description="Get statistics for the loaded GEDCOM file: individual/family counts, surname frequency, encoding.",
    )
    async def gedcom_stats() -> list[TextContent]:
        return [TextContent(type="text", text=_stats_sync())]
