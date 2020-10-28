import json
import pytest
import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestUpdate:

    """ TESTS: all update routes """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)
    index = None
    dataset_file = None
    dataset_json = None

    @pytest.mark.asyncio
    async def setup_class(self):
        await clear_all_indexes(self.client)
        self.index = await self.client.create_index(uid='indexUID')
        self.dataset_file = open('./datasets/small_movies.json', 'r')
        self.dataset_json = json.loads(self.dataset_file.read())
        self.dataset_file.close()

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.index.delete()
        await self.index.http.close()
        await self.client.close()

    @pytest.mark.asyncio
    async def test_get_all_update_status_default(self):
        """Tests getting the updates list of an empty index"""
        response = await self.index.get_all_update_status()
        assert isinstance(response, list)
        assert response == []

    @pytest.mark.asyncio
    async def test_get_all_update_status(self):
        """Tests getting the updates list of a populated index"""
        response = await self.index.add_documents(self.dataset_json)
        assert 'updateId' in response
        response = await self.index.add_documents(self.dataset_json)
        assert 'updateId' in response
        response = await self.index.get_all_update_status()
        assert len(response) == 2

    @pytest.mark.asyncio
    async def test_get_update(self):
        """Tests getting an update of a given operation"""
        response = await self.index.add_documents(self.dataset_json)
        assert 'updateId' in response
        update = await self.index.wait_for_pending_update(response['updateId'])
        assert update['status'] == 'processed'
        response = await self.index.get_update_status(response['updateId'])
        assert 'updateId' in response
        assert 'type' in response
        assert 'duration' in response
        assert 'enqueuedAt' in response
        assert 'processedAt' in response

    @pytest.mark.asyncio
    async def test_get_update_inexistent(self):
        """Tests getting an update of an INEXISTENT operation"""
        with pytest.raises(Exception):
            await self.index.get_update_status('999')
