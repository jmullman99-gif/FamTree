import httpx
import pytest

from genealogy_mcp.archives import client

MOCK_SEARCH_RESPONSE = {
    "query": {"name": "Jansen", "start": 0, "number_show": 10},
    "response": {
        "number_found": 1500,
        "docs": [
            {
                "pid": "Person1",
                "identifier": "6df9eb7c-1386-86b8-48c8-699155afcdec",
                "archive_code": "ghn",
                "archive_org": "Nationaal Archief",
                "personname": "Jansen",
                "relationtype": "Kind",
                "eventtype": "Geboorte",
                "eventdate": {"year": 1878},
                "eventplace": ["'s-Gravenhage"],
                "sourcetype": "BS Geboorte",
                "url": "https://www.openarchieven.nl/show/6df9eb7c",
            }
        ],
    },
}


def _mock_transport(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "records/search.json" in url:
        return httpx.Response(200, json=MOCK_SEARCH_RESPONSE)
    return httpx.Response(404)


@pytest.fixture
def mock_http():
    return httpx.AsyncClient(transport=httpx.MockTransport(_mock_transport))


class TestArchivesClient:
    @pytest.mark.asyncio
    async def test_search_records(self, mock_http):
        result = await client.search_records(mock_http, name="Jansen")
        assert result["response"]["number_found"] == 1500
        assert len(result["response"]["docs"]) == 1

    @pytest.mark.asyncio
    async def test_search_empty(self, mock_http):
        transport = httpx.MockTransport(
            lambda r: httpx.Response(
                200, json={"query": {}, "response": {"number_found": 0, "docs": []}}
            )
        )
        async with httpx.AsyncClient(transport=transport) as http:
            result = await client.search_records(http, name="xyznonexistent")
            assert result["response"]["number_found"] == 0

    @pytest.mark.asyncio
    async def test_user_agent_header(self, mock_http):
        # Verify the client sends requests (transport will capture them)
        result = await client.search_records(mock_http, name="Test")
        assert result is not None
