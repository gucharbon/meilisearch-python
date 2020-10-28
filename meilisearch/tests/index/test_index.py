import pytest
import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestIndex:

    """ TESTS: all index routes """

    client = meilisearch.AsyncClient(BASE_URL, MASTER_KEY)
    index_uid = 'indexUID'
    index_uid2 = 'indexUID2'
    index_uid3 = 'indexUID3'
    index_uid4 = 'indexUID4'

    @pytest.mark.asyncio
    async def setup_class(self):
        await clear_all_indexes(self.client)

    @pytest.mark.asyncio
    async def test_create_index(self):
        """Tests creating an index"""
        index = await self.client.create_index(uid=self.index_uid)
        assert isinstance(index, object)
        assert index.uid == self.index_uid
        assert await index.get_primary_key() is None

    @pytest.mark.asyncio
    async def test_create_index_with_primary_key(self):
        """Tests creating an index with a primary key"""
        index = await self.client.create_index(uid=self.index_uid2, options={'primaryKey': 'book_id'})
        assert isinstance(index, object)
        assert index.uid == self.index_uid2
        assert await index.get_primary_key() == 'book_id'

    @pytest.mark.asyncio
    async def test_create_index_with_uid_in_options(self):
        """Tests creating an index with a primary key"""
        index = await self.client.create_index(uid=self.index_uid3, options={'uid': 'wrong', 'primaryKey': 'book_id'})
        assert isinstance(index, object)
        assert index.uid == self.index_uid3
        assert await index.get_primary_key() == 'book_id'

    @pytest.mark.asyncio
    async def test_get_indexes(self):
        """Tests getting all indexes"""
        response = await self.client.get_indexes()
        uids = [index['uid'] for index in response]
        assert isinstance(response, list)
        assert self.index_uid in uids
        assert self.index_uid2 in uids
        assert self.index_uid3 in uids
        assert len(response) == 3

    def test_get_index_with_uid(self):
        """Tests getting one index with uid"""
        response = self.client.get_index(uid=self.index_uid)
        assert isinstance(response, object)
        assert response.uid == self.index_uid

    def test_get_index_with_none_uid(self):
        """Test raising an exception if the index UID is None"""
        with pytest.raises(Exception):
            self.client.get_index(uid=None)

    @pytest.mark.asyncio
    async def test_get_or_create_index(self):
        """Test get_or_create_index method"""
        # self.client.create_index(self.index_uid3)
        index_1 = await self.client.get_or_create_index(self.index_uid4)
        index_2 = await self.client.get_or_create_index(self.index_uid4)
        index_3 = await self.client.get_or_create_index(self.index_uid4)
        assert index_1.uid == index_2.uid == index_3.uid == self.index_uid4
        update = await index_1.add_documents([{
            'book_id': 1,
            'name': "Some book"
        }])
        await index_1.wait_for_pending_update(update['updateId'])
        documents = await index_2.get_documents()
        assert len(documents) == 1
        await index_2.delete()
        with pytest.raises(Exception):
            await self.client.get_index(index_3).info()

    @pytest.mark.asyncio
    async def test_get_or_create_index_with_primary_key(self):
        """Test get_or_create_index method with primary key"""
        index_1 = await self.client.get_or_create_index('books', {'primaryKey': self.index_uid4})
        index_2 = await self.client.get_or_create_index('books', {'primaryKey': 'some_wrong_key'})
        assert await index_1.get_primary_key() == self.index_uid4
        assert await index_2.get_primary_key() == self.index_uid4
        await index_1.delete()

    @pytest.mark.asyncio
    async def test_index_info(self):
        """Tests getting an index's info"""
        index = self.client.get_index(uid=self.index_uid)
        response = await index.info()
        assert isinstance(response, object)
        assert response['uid'] == self.index_uid
        assert response['primaryKey'] is None

    @pytest.mark.asyncio
    async def test_index_info_with_wrong_uid(self):
        """Tests getting an index's info in MeiliSearch with a wrong UID"""
        with pytest.raises(Exception):
            await self.client.get_index(uid='wrongUID').info()

    @pytest.mark.asyncio
    async def test_get_primary_key(self):
        """Tests getting the primary-key of an index"""
        index = self.client.get_index(uid=self.index_uid)
        response = await index.get_primary_key()
        assert response is None

    @pytest.mark.asyncio
    async def test_update_index(self):
        """Tests updating an index"""
        index = self.client.get_index(uid=self.index_uid)
        response = await index.update(primaryKey='objectID')
        assert isinstance(response, object)
        assert await index.get_primary_key() == 'objectID'

    @pytest.mark.asyncio
    async def test_delete_index(self):
        """Tests deleting an index"""
        index = self.client.get_index(uid=self.index_uid)
        response = await index.delete()
        assert isinstance(response, object)
        assert response.status_code == 204
        with pytest.raises(Exception):
            await self.client.get_index(uid=self.index_uid).info()
        index = self.client.get_index(uid=self.index_uid2)
        response = await index.delete()
        assert isinstance(response, object)
        assert response.status_code == 204
        with pytest.raises(Exception):
            await self.client.get_index(uid=self.index_uid2).info()
        index = self.client.get_index(uid=self.index_uid3)
        response = await index.delete()
        assert isinstance(response, object)
        assert response.status_code == 204
        with pytest.raises(Exception):
            await self.client.get_index(uid=self.index_uid3).info()
        assert len(await self.client.get_indexes()) == 0
