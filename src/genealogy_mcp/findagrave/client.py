"""Find A Grave scraper client.

Searches findagrave.com and extracts memorial data from HTML results.
No API key required.
"""
from __future__ import annotations

import re
from html import unescape

import httpx

BASE_URL = "https://www.findagrave.com"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; genealogy-mcp/0.1)",
}

# ── HTML parsing helpers ──────────────────────────────────────


def _extract_results(html: str) -> list[dict]:
    """Parse memorial search results from Find A Grave HTML."""
    results: list[dict] = []

    # Each result has id="sr-{memorial_id}"
    for block in re.finditer(
        r'id="sr-(\d+)">(.*?)(?=id="sr-|\Z)', html, re.DOTALL
    ):
        memorial_id = block.group(1)
        chunk = block.group(2)

        # Name: inside <i class="pe-2 text-break">...</i>
        name_match = re.search(
            r'class="[^"]*text-break[^"]*">(.*?)</i>', chunk, re.DOTALL
        )
        name = _clean(name_match.group(1)) if name_match else ""

        # Birth/death dates: inside <b class="birthDeathDates ...">
        dates_match = re.search(
            r'class="birthDeathDates[^"]*">(.*?)</b>', chunk, re.DOTALL
        )
        birth_date = ""
        death_date = ""
        if dates_match:
            raw = _clean(dates_match.group(1))
            # Dates are separated by – (ndash) or -
            parts = re.split(r"\s*[–\-]\s*", raw, maxsplit=1)
            birth_date = parts[0].strip() if parts else ""
            death_date = parts[1].strip() if len(parts) > 1 else ""

        # Cemetery name
        cemetery_match = re.search(
            r'title="([^"]+)"[^>]*>[^<]*</button>\s*</form>', chunk
        )
        cemetery = cemetery_match.group(1) if cemetery_match else ""

        # Location: inside <p class="addr-cemet ...">
        location_match = re.search(
            r'class="addr-cemet[^"]*">(.*?)</p>', chunk, re.DOTALL
        )
        location = ""
        if location_match:
            # Strip tags, collapse whitespace and commas
            raw_loc = re.sub(r"<[^>]+>", "", location_match.group(1))
            raw_loc = re.sub(r"\s+", " ", raw_loc).strip()
            # Clean up double commas from empty fields
            raw_loc = re.sub(r",\s*,", ",", raw_loc)
            raw_loc = raw_loc.strip(", ")
            location = raw_loc

        # Memorial URL
        url = f"{BASE_URL}/memorial/{memorial_id}"

        results.append({
            "memorial_id": memorial_id,
            "name": name,
            "birth_date": birth_date,
            "death_date": death_date,
            "cemetery": cemetery,
            "location": location,
            "url": url,
        })

    return results


def _clean(s: str) -> str:
    """Strip HTML tags, decode entities, collapse whitespace."""
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    return re.sub(r"\s+", " ", s).strip()


# ── Public API ────────────────────────────────────────────────


async def search_memorials(
    http: httpx.AsyncClient,
    *,
    firstname: str = "",
    lastname: str = "",
    birth_year: str = "",
    death_year: str = "",
    location: str = "",
    page: int = 1,
    rows: int = 20,
) -> dict:
    """Search Find A Grave for memorials.

    Returns a dict with ``total`` (int or None) and ``results`` (list of
    memorial dicts with name, dates, cemetery, location, url).
    """
    params: dict = {}
    if firstname:
        params["firstname"] = firstname
    if lastname:
        params["lastname"] = lastname
    if birth_year:
        params["birthyear"] = birth_year
    if death_year:
        params["deathyear"] = death_year
    if location:
        params["locationId"] = location
    if page > 1:
        params["page"] = str(page)

    resp = await http.get(
        f"{BASE_URL}/memorial/search",
        params=params,
        headers=_HEADERS,
    )
    resp.raise_for_status()

    results = _extract_results(resp.text)

    # Try to extract total count from "Showing X of Y"
    total_match = re.search(r"of\s+([\d,]+)\s+result", resp.text)
    total = int(total_match.group(1).replace(",", "")) if total_match else None

    return {
        "total": total,
        "results": results[:rows],
    }


async def get_memorial(
    http: httpx.AsyncClient,
    *,
    memorial_id: str,
) -> dict:
    """Get details for a specific Find A Grave memorial.

    Returns a dict with name, dates, cemetery, location, bio, and URL.
    """
    resp = await http.get(
        f"{BASE_URL}/memorial/{memorial_id}",
        headers=_HEADERS,
    )
    resp.raise_for_status()
    html = resp.text

    # Name from og:title (most reliable) or bio-name h1
    name = ""
    og_match = re.search(r'property="og:title"\s+content="([^"]+)"', html)
    if og_match:
        raw_name = unescape(og_match.group(1))
        # Strip " (YYYY-YYYY)" and optional " - Find a Grave Memorial" suffix
        name = re.sub(r"\s*\([^)]*\)(?:\s*[-–].*)?$", "", raw_name).strip()
    if not name:
        name_match = re.search(r'id="bio-name"[^>]*>([^<]+)', html)
        if name_match:
            name = _clean(name_match.group(1))

    # Birth/death dates
    birth_date = ""
    death_date = ""
    birth_match = re.search(r'id="birthDateLabel"[^>]*>([^<]+)', html)
    if birth_match:
        birth_date = _clean(birth_match.group(1))
    death_match = re.search(r'id="deathDateLabel"[^>]*>([^<]+)', html)
    if death_match:
        raw_death = _clean(death_match.group(1))
        # Strip "(aged X)" suffix
        death_date = re.sub(r"\s*\(aged\s+\d+\)\s*$", "", raw_death)

    # Fallback: look for birthDeathDates span
    if not birth_date and not death_date:
        dates_match = re.search(
            r'class="birthDeathDates[^"]*">(.*?)</b>', html, re.DOTALL
        )
        if dates_match:
            raw = _clean(dates_match.group(1))
            parts = re.split(r"\s*[–\-]\s*", raw, maxsplit=1)
            birth_date = parts[0].strip() if parts else ""
            death_date = parts[1].strip() if len(parts) > 1 else ""

    # Cemetery — try cemeteryNameLabel first, then itemprop
    cemetery = ""
    cem_match = re.search(
        r'cemeteryNameLabel[^>]*>(.*?)</[^>]+>', html, re.DOTALL
    )
    if cem_match:
        cemetery = _clean(cem_match.group(1))
    if not cemetery:
        cem_match = re.search(
            r'id="cemetery[Nn]ame"[^>]*>(.*?)</[^>]+>', html, re.DOTALL
        )
        if cem_match:
            cemetery = _clean(cem_match.group(1))

    # Location — extract from Schema.org PostalAddress microdata
    location = ""
    addr_match = re.search(
        r'itemprop="address"[^>]*>(.*?)(?:</div>|</section>|Add to Map)',
        html,
        re.DOTALL,
    )
    if addr_match:
        raw_addr = re.sub(r"<[^>]+>", " ", addr_match.group(1))
        raw_addr = re.sub(r"\s+", " ", raw_addr).strip()
        # Clean comma runs and stray Schema.org attributes
        raw_addr = re.sub(r"\s*,\s*,", ",", raw_addr)
        raw_addr = re.sub(r"itemscope\s+itemtype=[^\s>]+", "", raw_addr)
        raw_addr = re.sub(r"Show Map.*$", "", raw_addr)
        raw_addr = re.sub(r"GPS-.*$", "", raw_addr)
        location = re.sub(r"\s+", " ", raw_addr).strip(", ")
    if not location:
        loc_match = re.search(
            r'id="cemetery[Ll]ocation"[^>]*>(.*?)</[^>]+>', html, re.DOTALL
        )
        if loc_match:
            location = _clean(loc_match.group(1))

    # Bio/inscription
    bio = ""
    bio_match = re.search(r'id="annotatedBio"[^>]*>(.*?)</div>', html, re.DOTALL)
    if bio_match:
        bio = _clean(bio_match.group(1))

    # Plot info
    plot = ""
    plot_match = re.search(r'id="plotValue"[^>]*>(.*?)</span>', html, re.DOTALL)
    if plot_match:
        plot = _clean(plot_match.group(1))

    return {
        "memorial_id": memorial_id,
        "name": name,
        "birth_date": birth_date,
        "death_date": death_date,
        "cemetery": cemetery,
        "location": location,
        "plot": plot,
        "bio": bio,
        "url": f"{BASE_URL}/memorial/{memorial_id}",
    }
