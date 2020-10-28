import pytest

import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestStats:

    """ TESTS: stats route """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)
    index = None

    @pytest.mark.asyncio
    async def setup_class(self):
        await clear_all_indexes(self.client)
        self.index = await self.client.create_index(uid='indexUID')

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.index.delete()
        await self.index.http.close()
        await self.client.close()

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Tests getting stats of a single index"""
        response = await self.index.get_stats()
        assert isinstance(response, object)
        assert 'numberOfDocuments' in response
        assert response['numberOfDocuments'] == 0
        assert 'isIndexing' in response
