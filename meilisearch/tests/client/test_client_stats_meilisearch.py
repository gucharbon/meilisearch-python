import pytest

import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestStats:

    """ TESTS: client stats route """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)
    index = None
    index2 = None

    @pytest.mark.asyncio
    async def setup_class(self):
        await clear_all_indexes(self.client)
        self.index = await self.client.create_index(uid='indexUID')
        self.index_2 = await self.client.create_index(uid='indexUID2')

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.index.delete()
        await self.index_2.delete()
        await self.client.close()

    @pytest.mark.asyncio
    async def test_get_all_stats(self):
        """Tests getting all stats after creating two indexes"""
        response = await self.client.get_all_stats()
        assert isinstance(response, object)
        assert 'databaseSize' in response
        assert isinstance(response['databaseSize'], int)
        assert 'lastUpdate' in response
        assert 'indexes' in response
        assert 'indexUID' in response['indexes']
        assert 'indexUID2' in response['indexes']
