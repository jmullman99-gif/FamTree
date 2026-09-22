"""Chronicling America API client (Library of Congress).

Uses the loc.gov collections API at ``www.loc.gov/collections/chronicling-america/``
(the legacy ``chroniclingamerica.loc.gov`` search endpoint was retired in 2024).
"""
from __future__ import annotations

import httpx

BASE_URL = "https://www.loc.gov"
COLLECTION_PATH = "/collections/chronicling-america/"


async def search_pages(
    http: httpx.AsyncClient,
    *,
    query: str,
    state: str = "",
    date_start: str = "",
    date_end: str = "",
    page: int = 1,
    rows: int = 20,
) -> dict:
    """Full-text search of newspaper pages. Returns matching pages with OCR snippets.

    Returns a dict with ``totalItems`` (int) and ``items`` (list of dicts with
    ``title``, ``date``, ``id`` (url), ``ocr_eng``).  This normalises the
    loc.gov collections response to the shape the rest of the codebase expects.
    """
    params: dict = {
        "q": query,
        "fo": "json",
        "c": min(rows, 100),
        "sp": page,
    }
    if state:
        params["fa"] = f"location_state:{state}"
    if date_start and date_end:
        params["dates"] = f"{date_start}/{date_end}"
    elif date_start:
        params["dates"] = f"{date_start}/"
    elif date_end:
        params["dates"] = f"/{date_end}"

    resp = await http.get(f"{BASE_URL}{COLLECTION_PATH}", params=params)
    resp.raise_for_status()
    data = resp.json()

    # Normalise to the shape the tools/crossref layer expects.
    results = data.get("results", [])
    pagination = data.get("pagination", {})
    items = []
    for r in results:
        description = r.get("description", [])
        ocr_text = description[0] if description else ""
        items.append({
            "id": r.get("url", ""),
            "title": r.get("title", ""),
            "date": r.get("date", ""),
            "ocr_eng": ocr_text,
        })

    return {
        "totalItems": pagination.get("of", len(items)),
        "items": items,
    }


async def get_page_ocr(http: httpx.AsyncClient, *, url: str) -> str:
    """Get full OCR text for a newspaper page.

    ``url`` should be a full loc.gov resource URL from search results.
    Appends ``?fo=txt`` to request the plain-text rendition.
    """
    target = url.rstrip("/")
    if not target.startswith("http"):
        target = f"{BASE_URL}{target}"

    resp = await http.get(target, params={"fo": "txt"})
    resp.raise_for_status()
    return resp.text
