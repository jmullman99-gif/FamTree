from urllib.parse import parse_qs

import httpx
import pytest

from genealogy_mcp.wikitree import client

# ── Mock transport ──────────────────────────────────────────────

MOCK_SEARCH_RESPONSE = [
    {
        "status": 0,
        "matches": [
            {
                "Id": 5185,
                "Name": "Clemens-1",
                "FirstName": "Samuel",
                "LastNameAtBirth": "Clemens",
                "BirthDate": "1835-11-30",
                "DeathDate": "1910-04-21",
                "BirthLocation": "Florida, Missouri",
            }
        ],
        "total": 1,
        "start": 0,
        "limit": 10,
    }
]

MOCK_PERSON_RESPONSE = [
    {
        "status": 0,
        "page_name": "Clemens-1",
        "profile": {
            "Id": 5185,
            "Name": "Clemens-1",
            "FirstName": "Samuel",
            "LastNameAtBirth": "Clemens",
            "BirthDate": "1835-11-30",
            "DeathDate": "1910-04-21",
            "BirthLocation": "Florida, Missouri",
            "Gender": "Male",
        },
    }
]

MOCK_BIO_RESPONSE = [
    {
        "status": 0,
        "user_id": 5185,
        "Name": "Clemens-1",
        "bio": "== Biography ==\nSamuel Clemens was born...",
    }
]

MOCK_ANCESTORS_RESPONSE = [
    {
        "status": "",
        "resultByKey": {"Clemens-1": {"Id": 5185}},
        "people": {
            "5185": {"Id": 5185, "Name": "Clemens-1", "Father": 5200, "Mother": 5201},
            "5200": {"Id": 5200, "Name": "Clemens-2", "Father": None, "Mother": None},
            "5201": {"Id": 5201, "Name": "Lampton-1", "Father": None, "Mother": None},
        },
    }
]

MOCK_DESCENDANTS_RESPONSE = [
    {
        "status": "",
        "resultByKey": {"Clemens-1": {"Id": 5185}},
        "people": {
            "5185": {"Id": 5185, "Name": "Clemens-1", "Father": 5200, "Mother": 5201},
            "5300": {"Id": 5300, "Name": "Clemens-10", "Father": 5185, "Mother": 5190},
        },
    }
]

MOCK_RELATIVES_RESPONSE = [
    {
        "status": 0,
        "items": [
            {
                "key": "Clemens-1",
                "user_id": 5185,
                "person": {"Id": 5185, "Name": "Clemens-1"},
                "Parents": {"5200": {"Id": 5200, "Name": "Clemens-2"}},
                "Children": {"5300": {"Id": 5300, "Name": "Clemens-10"}},
            }
        ],
    }
]

MOCK_ERROR_RESPONSE = [{"status": 1}]


def _mock_transport(request: httpx.Request) -> httpx.Response:
    body = request.content.decode()
    params = parse_qs(body)
    action = params.get("action", [""])[0]

    if action == "getPeople":
        # Route based on which traversal param is present.
        if "ancestors" in params:
            return httpx.Response(200, json=MOCK_ANCESTORS_RESPONSE)
        if "descendants" in params:
            return httpx.Response(200, json=MOCK_DESCENDANTS_RESPONSE)

    response_map = {
        "searchPerson": MOCK_SEARCH_RESPONSE,
        "getPerson": MOCK_PERSON_RESPONSE,
        "getBio": MOCK_BIO_RESPONSE,
        "getRelatives": MOCK_RELATIVES_RESPONSE,
    }
    data = response_map.get(action, MOCK_ERROR_RESPONSE)
    return httpx.Response(200, json=data)


@pytest.fixture
def mock_http():
    transport = httpx.MockTransport(_mock_transport)
    return httpx.AsyncClient(transport=transport)


# ── Tests ───────────────────────────────────────────────────────


class TestWikiTreeClient:
    @pytest.mark.asyncio
    async def test_search_person(self, mock_http):
        results = await client.search_person(mock_http, last_name="Clemens")
        assert len(results) == 1
        assert results[0]["Name"] == "Clemens-1"

    @pytest.mark.asyncio
    async def test_search_empty(self, mock_http):
        # Override transport for empty result
        transport = httpx.MockTransport(
            lambda r: httpx.Response(200, json=[{"status": 0, "matches": [], "total": 0}])
        )
        async with httpx.AsyncClient(transport=transport) as http:
            results = await client.search_person(http, last_name="Nonexistent")
            assert results == []

    @pytest.mark.asyncio
    async def test_get_profile(self, mock_http):
        profile = await client.get_profile(mock_http, key="Clemens-1")
        assert profile["FirstName"] == "Samuel"

    @pytest.mark.asyncio
    async def test_get_bio(self, mock_http):
        result = await client.get_bio(mock_http, key="Clemens-1")
        assert "Biography" in result["bio"]

    @pytest.mark.asyncio
    async def test_get_ancestors(self, mock_http):
        ancestors = await client.get_ancestors(mock_http, key="Clemens-1", depth=2)
        assert len(ancestors) == 3

    @pytest.mark.asyncio
    async def test_get_descendants(self, mock_http):
        descendants = await client.get_descendants(mock_http, key="Clemens-1", depth=2)
        assert len(descendants) == 2

    @pytest.mark.asyncio
    async def test_get_relatives(self, mock_http):
        result = await client.get_relatives(
            mock_http, key="Clemens-1", get_parents=True, get_children=True
        )
        assert "Parents" in result
        assert "Children" in result

    @pytest.mark.asyncio
    async def test_api_error_status(self, mock_http):
        transport = httpx.MockTransport(
            lambda r: httpx.Response(200, json=[{"status": 1}])
        )
        async with httpx.AsyncClient(transport=transport) as http:
            with pytest.raises(client.WikiTreeAPIError):
                await client.get_profile(http, key="Private-1")
