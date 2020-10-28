import pytest
import meilisearch
from meilisearch.errors import MeiliSearchApiError
from meilisearch.tests import BASE_URL, MASTER_KEY

class TestMeiliSearchApiError:

    """ TESTS: MeiliSearchApiError class """

    @pytest.mark.asyncio
    @staticmethod
    async def test_meilisearch_api_error_no_master_key():
        with pytest.raises(MeiliSearchApiError):
            async with meilisearch.AsyncClient(BASE_URL) as client:
                await client.create_index("some_index")

    @pytest.mark.asyncio
    @staticmethod
    async def test_meilisearch_api_error_wrong_master_key():
        with pytest.raises(MeiliSearchApiError):
            async with meilisearch.AsyncClient(BASE_URL, MASTER_KEY + '123') as client:
                await client.create_index("some_index")
