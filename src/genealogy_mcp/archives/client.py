"""Open Archives API client (openarchieven.nl — Dutch/Belgian/French records)."""
from __future__ import annotations

import httpx

BASE_URL = "https://api.openarchieven.nl/1.1"


async def search_records(
    http: httpx.AsyncClient,
    *,
    name: str,
    place: str = "",
    number_show: int = 20,
    start: int = 0,
) -> dict:
    """Search Open Archives for historical records matching a person name.

    Rate limit: 4 requests/second (enforced server-side).
    """
    params: dict = {
        "name": name,
        "number_show": min(number_show, 100),
        "start": start,
        "lang": "en",
    }
    if place:
        # Open Archives accepts place in the name field with quotes
        # but also filters by eventplace
        params["name"] = f"{name} {place}"

    resp = await http.get(f"{BASE_URL}/records/search.json", params=params)
    resp.raise_for_status()
    return resp.json()
