import pytest

import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY

class TestHealth:

    """ TESTS: health route """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)

    @pytest.mark.asyncio
    def test_health(self):
        """Tests checking the health of MeiliSearch instance"""
        response = self.client.health()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def teardown_class(self):
        """Cleans all indexes in MEiliSearch when all the test are done"""
        await self.client.close()
