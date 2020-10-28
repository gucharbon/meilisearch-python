import pytest
import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY

class TestClient:

    """ TESTS: Client class """

    @pytest.mark.asyncio
    @staticmethod
    async def test_get_client():
        """Tests getting a client instance"""
        async with meilisearch.AsyncClient(BASE_URL, MASTER_KEY) as client:
            assert client.config
            response = await client.health()
            assert response.status_code == 200

    @pytest.mark.asyncio
    @staticmethod
    async def test_get_client_without_master_key():
        """Tests getting a client instance without MASTER KEY"""
        with pytest.raises(Exception):
            async with meilisearch.AsyncClient(BASE_URL) as client:
                await client.get_version()

    @pytest.mark.asyncio
    @staticmethod
    async def test_get_client_with_wrong_master_key():
        """Tests getting a client instance with an invalid MASTER KEY"""
        with pytest.raises(Exception):
            async with meilisearch.AsyncClient(BASE_URL, MASTER_KEY + "123") as client:
                await client.get_version()
