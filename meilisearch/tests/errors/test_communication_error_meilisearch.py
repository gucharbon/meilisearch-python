import pytest
import meilisearch
from meilisearch.errors import MeiliSearchCommunicationError
from meilisearch.tests import MASTER_KEY

class TestMeiliSearchCommunicationError:

    """ TESTS: MeiliSearchCommunicationError class """

    @pytest.mark.asyncio
    @staticmethod
    async def test_meilisearch_communication_error_host():
        with pytest.raises(MeiliSearchCommunicationError):
            async with meilisearch.AsyncClient("http://wrongurl:1234", MASTER_KEY) as client:
                await client.create_index("some_index")
