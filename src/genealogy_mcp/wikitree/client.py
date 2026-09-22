"""WikiTree API client. All functions are async and take an httpx.AsyncClient."""
from __future__ import annotations

import httpx

API_URL = "https://api.wikitree.com/api.php"


class WikiTreeAPIError(Exception):
    """Raised when the WikiTree API returns a non-zero status."""


async def _post(http: httpx.AsyncClient, data: dict) -> list:
    resp = await http.post(API_URL, data=data)
    resp.raise_for_status()
    return resp.json()


def _check_status(result: list) -> None:
    if not result or not isinstance(result[0], dict):
        return
    status = result[0].get("status")
    # WikiTree uses 0 or "" for success; any other truthy value is an error.
    if status and status != 0:
        raise WikiTreeAPIError(f"WikiTree API error (status {status})")


async def search_person(
    http: httpx.AsyncClient,
    *,
    last_name: str = "",
    first_name: str = "",
    birth_date: str = "",
    death_date: str = "",
    birth_location: str = "",
    limit: int = 10,
) -> list[dict]:
    """Search WikiTree for people matching the given criteria."""
    data: dict = {"action": "searchPerson", "limit": str(limit)}
    if last_name:
        data["LastName"] = last_name
    if first_name:
        data["FirstName"] = first_name
    if birth_date:
        data["BirthDate"] = birth_date
    if death_date:
        data["DeathDate"] = death_date
    if birth_location:
        data["BirthLocation"] = birth_location

    result = await _post(http, data)
    _check_status(result)
    return result[0].get("matches", [])


async def get_profile(
    http: httpx.AsyncClient,
    *,
    key: str,
    fields: str = "*",
) -> dict:
    """Get a WikiTree profile by WikiTree ID (e.g. 'Smith-12345') or numeric User ID."""
    data = {"action": "getPerson", "key": key, "fields": fields, "resolveRedirect": "1"}
    result = await _post(http, data)
    _check_status(result)
    return result[0].get("profile", result[0])


async def get_relatives(
    http: httpx.AsyncClient,
    *,
    key: str,
    get_parents: bool = False,
    get_children: bool = False,
    get_siblings: bool = False,
    get_spouses: bool = False,
) -> dict:
    """Get relatives for a WikiTree profile."""
    data: dict = {"action": "getRelatives", "keys": key, "fields": "*"}
    if get_parents:
        data["getParents"] = "1"
    if get_children:
        data["getChildren"] = "1"
    if get_siblings:
        data["getSiblings"] = "1"
    if get_spouses:
        data["getSpouses"] = "1"

    result = await _post(http, data)
    _check_status(result)
    items = result[0].get("items", [])
    return items[0] if items else {}


async def get_ancestors(
    http: httpx.AsyncClient,
    *,
    key: str,
    depth: int = 5,
) -> list[dict]:
    """Get ancestor tree for a WikiTree profile.

    Uses ``getPeople`` with the ``ancestors`` parameter (the legacy
    ``getAncestors`` action was deprecated by WikiTree in 2025).
    Returns a flat list of ancestor profile dicts.
    """
    data = {
        "action": "getPeople",
        "keys": key,
        "ancestors": str(depth),
        "fields": "*",
        "resolveRedirect": "1",
    }
    result = await _post(http, data)
    _check_status(result)
    people = result[0].get("people", {})
    return list(people.values())


async def get_descendants(
    http: httpx.AsyncClient,
    *,
    key: str,
    depth: int = 3,
) -> list[dict]:
    """Get descendant tree for a WikiTree profile.

    Uses ``getPeople`` with the ``descendants`` parameter (the legacy
    ``getDescendants`` action was deprecated by WikiTree in 2025).
    Returns a flat list of descendant profile dicts.
    """
    data = {
        "action": "getPeople",
        "keys": key,
        "descendants": str(depth),
        "fields": "*",
        "resolveRedirect": "1",
    }
    result = await _post(http, data)
    _check_status(result)
    people = result[0].get("people", {})
    return list(people.values())


async def get_bio(
    http: httpx.AsyncClient,
    *,
    key: str,
) -> dict:
    """Get the full biography text for a WikiTree profile."""
    data = {"action": "getBio", "key": key}
    result = await _post(http, data)
    _check_status(result)
    return result[0]
