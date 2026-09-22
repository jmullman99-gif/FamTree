import httpx
import pytest

from genealogy_mcp.newspapers import client

# Mock the loc.gov collections API response format.
MOCK_LOC_RESPONSE = {
    "pagination": {"of": 42, "total": 21, "current": 1, "perpage": 2},
    "results": [
        {
            "url": "https://www.loc.gov/resource/sn83030214/1905-03-15/ed-1/?sp=1",
            "title": "Image 1 of New-York tribune., March 15, 1905",
            "date": "1905-03-15",
            "description": ["John Smith arrived yesterday on the steamer..."],
            "location_state": ["New York"],
        },
        {
            "url": "https://www.loc.gov/resource/sn83030214/1905-04-02/ed-1/?sp=3",
            "title": "Image 3 of New-York tribune., April 2, 1905",
            "date": "1905-04-02",
            "description": ["The funeral of Mr. Smith was held at..."],
            "location_state": ["New York"],
        },
    ],
}

MOCK_OCR_TEXT = "Full page OCR text content here with John Smith mentioned on line 42..."


def _mock_transport(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if "/collections/chronicling-america/" in url:
        return httpx.Response(200, json=MOCK_LOC_RESPONSE)
    if "fo=txt" in url or url.endswith("/ocr.txt"):
        return httpx.Response(200, text=MOCK_OCR_TEXT)
    return httpx.Response(404)


@pytest.fixture
def mock_http():
    return httpx.AsyncClient(transport=httpx.MockTransport(_mock_transport))


class TestNewspapersClient:
    @pytest.mark.asyncio
    async def test_search_pages(self, mock_http):
        result = await client.search_pages(mock_http, query="John Smith")
        assert result["totalItems"] == 42
        assert len(result["items"]) == 2
        assert "John Smith" in result["items"][0]["ocr_eng"]

    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_http):
        result = await client.search_pages(
            mock_http, query="Smith", state="New York", date_start="1900", date_end="1910"
        )
        assert result["totalItems"] == 42

    @pytest.mark.asyncio
    async def test_search_empty(self, mock_http):
        transport = httpx.MockTransport(
            lambda r: httpx.Response(200, json={"pagination": {}, "results": []})
        )
        async with httpx.AsyncClient(transport=transport) as http:
            result = await client.search_pages(http, query="xyznonexistent")
            assert result["totalItems"] == 0
            assert result["items"] == []

    @pytest.mark.asyncio
    async def test_get_page_ocr(self, mock_http):
        text = await client.get_page_ocr(
            mock_http,
            url="https://www.loc.gov/resource/sn83030214/1905-03-15/ed-1/?sp=1",
        )
        assert "John Smith" in text

    @pytest.mark.asyncio
    async def test_normalised_item_keys(self, mock_http):
        """Verify search_pages normalises loc.gov results to expected item shape."""
        result = await client.search_pages(mock_http, query="Smith")
        item = result["items"][0]
        assert "id" in item
        assert "title" in item
        assert "date" in item
        assert "ocr_eng" in item
