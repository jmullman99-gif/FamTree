import httpx
import pytest

from genealogy_mcp.findagrave import client

# ── Mock HTML responses ───────────────────────────────────────

MOCK_SEARCH_HTML = """
<html><body>
<div>Showing 1-2 of 42 results</div>
<div role="group" aria-label="Memorial">
<div class="memorial-item px-2 py-2 gx-4 gy-0 position-relative row border-bottom align-items-md-center" id="sr-1234">
    <div class="col-12 col-md col-print-3">
    <a class="d-flex align-items-center text-decoration-none" href="/memorial/1234/john-smith">
    <div class="memorial-item--info">
        <div class="memorial-item---grave">
            <h2 class="name-grave d-flex"><i class="pe-2 text-break">John Smith</i></i></h2>
            <b class="birthDeathDates fw-light fs-5 text-body">15 Mar 1850 &ndash; 22 Jun 1920</b>
        </div>
    </div>
    </a>
    </div>
    <div class="memorial-item---cemet col-12 col-md-auto">
        <form action="/cemetery/999/green-lawn-cemetery"><button type="submit" class="btn btn-link" role="link" title="Green Lawn Cemetery">Green Lawn Cemetery</button></form>
        <p class="addr-cemet mb-1">
            Columbus,
            Franklin County,
            Ohio,
            United States
        </p>
    </div>
</div>
</div>

<div role="group" aria-label="Memorial">
<div class="memorial-item px-2 py-2 gx-4 gy-0 position-relative row border-bottom align-items-md-center" id="sr-5678">
    <div class="col-12 col-md col-print-3">
    <a class="d-flex align-items-center text-decoration-none" href="/memorial/5678/john-smith-jr">
    <div class="memorial-item--info">
        <div class="memorial-item---grave">
            <h2 class="name-grave d-flex"><i class="pe-2 text-break">John Smith Jr.</i></i></h2>
            <b class="birthDeathDates fw-light fs-5 text-body">1880 &ndash; 1945</b>
        </div>
    </div>
    </a>
    </div>
    <div class="memorial-item---cemet col-12 col-md-auto">
        <form action="/cemetery/888/oak-hill"><button type="submit" class="btn btn-link" role="link" title="Oak Hill Cemetery">Oak Hill Cemetery</button></form>
        <p class="addr-cemet mb-1">
            Youngstown,
            Mahoning County,
            Ohio,
            United States
        </p>
    </div>
</div>
</div>
</body></html>
"""

MOCK_MEMORIAL_HTML = """
<html><head>
<meta property="og:title" content="John Smith (1850-1920)">
</head><body>
<h1 id="bio-name">John Smith</h1>
<time id="birthDateLabel" itemprop="birthDate">15 Mar 1850</time>
<span id="deathDateLabel" itemprop="deathDate">22 Jun 1920</span>
<a id="cemeteryNameLabel">Green Lawn Cemetery</a>
<div itemprop="address"><span>Columbus, Franklin County, Ohio, United States</span></div>
<span id="plotValue">Section B, Lot 42</span>
<div id="annotatedBio">Beloved father and husband. Served in the Civil War.</div>
</body></html>
"""

MOCK_EMPTY_HTML = """
<html><body>
<div>No results found</div>
</body></html>
"""


def _mock_transport(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "/memorial/search" in url:
        if "Nonexistent" in url:
            return httpx.Response(200, text=MOCK_EMPTY_HTML)
        return httpx.Response(200, text=MOCK_SEARCH_HTML)
    if "/memorial/1234" in url:
        return httpx.Response(200, text=MOCK_MEMORIAL_HTML)
    return httpx.Response(404)


@pytest.fixture
def mock_http():
    return httpx.AsyncClient(transport=httpx.MockTransport(_mock_transport))


# ── Tests ─────────────────────────────────────────────────────


class TestFindAGraveClient:
    @pytest.mark.asyncio
    async def test_search_memorials(self, mock_http):
        result = await client.search_memorials(mock_http, lastname="Smith")
        assert result["total"] == 42
        assert len(result["results"]) == 2

        first = result["results"][0]
        assert first["memorial_id"] == "1234"
        assert first["name"] == "John Smith"
        assert first["birth_date"] == "15 Mar 1850"
        assert first["death_date"] == "22 Jun 1920"
        assert first["cemetery"] == "Green Lawn Cemetery"
        assert "Ohio" in first["location"]
        assert first["url"] == "https://www.findagrave.com/memorial/1234"

    @pytest.mark.asyncio
    async def test_search_second_result(self, mock_http):
        result = await client.search_memorials(mock_http, lastname="Smith")
        second = result["results"][1]
        assert second["memorial_id"] == "5678"
        assert second["name"] == "John Smith Jr."
        assert second["birth_date"] == "1880"
        assert second["death_date"] == "1945"
        assert second["cemetery"] == "Oak Hill Cemetery"

    @pytest.mark.asyncio
    async def test_search_empty(self, mock_http):
        result = await client.search_memorials(mock_http, lastname="Nonexistent")
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_get_memorial(self, mock_http):
        result = await client.get_memorial(mock_http, memorial_id="1234")
        assert result["memorial_id"] == "1234"
        assert result["name"] == "John Smith"
        assert result["birth_date"] == "15 Mar 1850"
        assert result["death_date"] == "22 Jun 1920"
        assert result["cemetery"] == "Green Lawn Cemetery"
        assert "Ohio" in result["location"]
        assert "Civil War" in result["bio"]
        assert result["plot"] == "Section B, Lot 42"
        assert result["url"] == "https://www.findagrave.com/memorial/1234"

    @pytest.mark.asyncio
    async def test_search_params(self, mock_http):
        """Verify search passes filter parameters."""
        result = await client.search_memorials(
            mock_http,
            firstname="John",
            lastname="Smith",
            birth_year="1850",
            death_year="1920",
        )
        assert len(result["results"]) == 2
