import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from genealogy_mcp import crossref


class TestCrossReference:
    @pytest.mark.asyncio
    async def test_cross_reference_all_succeed(self):
        mock_http = AsyncMock()

        with (
            patch("genealogy_mcp.crossref.wikitree_client.search_person") as mock_wt,
            patch("genealogy_mcp.crossref.newspapers_client.search_pages") as mock_np,
            patch("genealogy_mcp.crossref.archives_client.search_records") as mock_ar,
        ):
            mock_wt.return_value = [{"Name": "Smith-1", "FirstName": "John"}]
            mock_np.return_value = {"totalItems": 1, "items": [{"title": "Daily News", "date": "19050315"}]}
            mock_ar.return_value = {"response": {"number_found": 1, "docs": [{"personname": "Smith"}]}}

            result = await crossref._cross_reference(
                mock_http, name="John Smith", birth_year="1850"
            )
            parsed = json.loads(result)
            assert "wikitree" in parsed
            assert "newspapers" in parsed
            assert "archives" in parsed
            assert len(parsed["wikitree"]) == 1

    @pytest.mark.asyncio
    async def test_cross_reference_partial_failure(self):
        mock_http = AsyncMock()

        with (
            patch("genealogy_mcp.crossref.wikitree_client.search_person") as mock_wt,
            patch("genealogy_mcp.crossref.newspapers_client.search_pages") as mock_np,
            patch("genealogy_mcp.crossref.archives_client.search_records") as mock_ar,
        ):
            mock_wt.return_value = [{"Name": "Smith-1"}]
            mock_np.side_effect = Exception("Connection timeout")
            mock_ar.return_value = {"response": {"number_found": 0, "docs": []}}

            result = await crossref._cross_reference(
                mock_http, name="John Smith"
            )
            parsed = json.loads(result)
            assert len(parsed["wikitree"]) == 1
            assert "error" in parsed["newspapers"]
            assert parsed["archives"] == []

    @pytest.mark.asyncio
    async def test_cross_reference_no_results(self):
        mock_http = AsyncMock()

        with (
            patch("genealogy_mcp.crossref.wikitree_client.search_person") as mock_wt,
            patch("genealogy_mcp.crossref.newspapers_client.search_pages") as mock_np,
            patch("genealogy_mcp.crossref.archives_client.search_records") as mock_ar,
        ):
            mock_wt.return_value = []
            mock_np.return_value = {"totalItems": 0, "items": []}
            mock_ar.return_value = {"response": {"number_found": 0, "docs": []}}

            result = await crossref._cross_reference(mock_http, name="Nobody")
            parsed = json.loads(result)
            assert parsed["wikitree"] == []
            assert parsed["newspapers"] == []
            assert parsed["archives"] == []
