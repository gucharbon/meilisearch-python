import pytest

import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestVersion:
    """ TESTS: version route """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)
    index = None

    @pytest.mark.asyncio
    async def setup_class(self):
        await clear_all_indexes(self.client)
        self.index = await self.client.create_index(uid='indexUID')

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.index.delete()
        await self.client.close()

    @pytest.mark.asyncio
    async def test_get_version(self):
        """Tests getting the version of the MeiliSearch instance"""
        response = await self.client.get_version()
        assert 'pkgVersion' in response
        assert 'commitSha' in response
        assert 'buildDate' in response
