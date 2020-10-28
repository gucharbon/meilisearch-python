import json
import pytest
import meilisearch
from meilisearch.tests import BASE_URL, MASTER_KEY, clear_all_indexes

class TestSearch:

    """ TESTS: search route """

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
        response = await self.index.add_documents(self.dataset_json, primary_key='id')
        await self.index.wait_for_pending_update(response['updateId'])

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.index.delete()
        await self.index.http.close()
        await self.client.close()

    @pytest.mark.asyncio
    async def test_basic_search(self):
        """Tests search with an simple query"""
        response = await self.index.search('How to Train Your Dragon')
        assert isinstance(response, object)
        assert response['hits'][0]['id'] == '166428'

    @pytest.mark.asyncio
    async def test_basic_search_with_empty_params(self):
        """Tests search with an simple query and empty params"""
        response = await self.index.search('How to Train Your Dragon', {})
        assert isinstance(response, object)
        assert response['hits'][0]['id'] == '166428'
        assert '_formatted' not in response['hits'][0]

    @pytest.mark.asyncio
    async def test_basic_search_with_empty_query(self):
        """Tests search with empty query and empty params"""
        response = await self.index.search('')
        assert isinstance(response, object)
        assert len(response['hits']) == 20
        assert response['query'] == ''

    @pytest.mark.asyncio
    async def test_basic_search_with_placeholder(self):
        """Tests search with no query [None] and empty params"""
        response = await self.index.search(None, {})
        assert isinstance(response, object)
        assert len(response['hits']) == 20

    @pytest.mark.asyncio
    async def test_custom_search(self):
        """Tests search with an simple query and custom parameter (attributesToHighlight)"""
        response = await self.index.search(
            'Dragon',
            {
                'attributesToHighlight': ['title']
            }
        )
        assert isinstance(response, object)
        assert response['hits'][0]['id'] == '166428'
        assert '_formatted' in response['hits'][0]
        assert 'dragon' in response['hits'][0]['_formatted']['title'].lower()

    @pytest.mark.asyncio
    async def test_custom_search_with_empty_query(self):
        """Tests search with empty query and custom parameter (attributesToHighlight)"""
        response = await self.index.search(
            '',
            {
                'attributesToHighlight': ['title']
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 20
        assert response['query'] == ''

    @pytest.mark.asyncio
    async def test_custom_search_with_placeholder(self):
        """Tests search with no query [None] and custom parameter (limit)"""
        response = await self.index.search(
            None,
            {
                'limit': 5
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 5

    @pytest.mark.asyncio
    async def test_custom_search_params_with_wildcard(self):
        """Tests search with '*' in query params"""
        response = await self.index.search(
            'a',
            {
                'limit': 5,
                'attributesToHighlight': ['*'],
                'attributesToRetrieve': ['*'],
                'attributesToCrop': ['*'],
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 5
        assert '_formatted' in response['hits'][0]
        assert "title" in response['hits'][0]['_formatted']

    @pytest.mark.asyncio
    async def test_custom_search_params_with_simple_string(self):
        """Tests search with simple string in query params"""
        response = await self.index.search(
            'a',
            {
                'limit': 5,
                'attributesToHighlight': ['title'],
                'attributesToRetrieve': ['title'],
                'attributesToCrop': ['title'],
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 5
        assert '_formatted' in response['hits'][0]
        assert 'title' in response['hits'][0]['_formatted']
        assert not 'release_date' in response['hits'][0]['_formatted']

    @pytest.mark.asyncio
    async def test_custom_search_params_with_string_list(self):
        """Tests search with string list in query params"""
        response = await self.index.search(
            'a',
            {
                'limit': 5,
                'attributesToRetrieve': ['title', 'overview'],
                'attributesToHighlight': ['title'],
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 5
        assert 'title' in response['hits'][0]
        assert 'overview' in response['hits'][0]
        assert not 'release_date' in response['hits'][0]
        assert 'title' in response['hits'][0]['_formatted']
        assert not 'overview' in response['hits'][0]['_formatted']

    @pytest.mark.asyncio
    async def test_custom_search_params_with_facets_distribution(self):
        update = await self.index.update_attributes_for_faceting(['genre'])
        await self.index.wait_for_pending_update(update['updateId'])
        response = await self.index.search(
            'world',
            {
                'facetsDistribution': ['genre']
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 12
        assert 'facetsDistribution' in response
        assert 'exhaustiveFacetsCount' in response
        assert response['exhaustiveFacetsCount']
        assert 'genre' in response['facetsDistribution']
        assert response['facetsDistribution']['genre']['cartoon'] == 1
        assert response['facetsDistribution']['genre']['action'] == 3
        assert response['facetsDistribution']['genre']['fantasy'] == 1

    @pytest.mark.asyncio
    async def test_custom_search_params_with_facet_filters(self):
        update = await self.index.update_attributes_for_faceting(['genre'])
        await self.index.wait_for_pending_update(update['updateId'])
        response = await self.index.search(
            'world',
            {
                'facetFilters': [['genre:action']]
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 3
        assert 'facetsDistribution' not in response
        assert 'exhaustiveFacetsCount' not in response

    @pytest.mark.asyncio
    async def test_custom_search_params_with_multiple_facet_filters(self):
        update = await self.index.update_attributes_for_faceting(['genre'])
        await self.index.wait_for_pending_update(update['updateId'])
        response = await self.index.search(
            'world',
            {
                'facetFilters': ['genre:action', ['genre:action', 'genre:action']]
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 3
        assert 'facetsDistribution' not in response
        assert 'exhaustiveFacetsCount' not in response

    @pytest.mark.asyncio
    async def test_custom_search_params_with_many_params(self):
        update = await self.index.update_attributes_for_faceting(['genre'])
        await self.index.wait_for_pending_update(update['updateId'])
        response = await self.index.search(
            'world',
            {
                'facetFilters': [['genre:action']],
                'attributesToRetrieve': ['title', 'poster']
            }
        )
        assert isinstance(response, object)
        assert len(response['hits']) == 3
        assert 'facetsDistribution' not in response
        assert 'exhaustiveFacetsCount' not in response
        assert 'title' in response['hits'][0]
        assert 'poster' in response['hits'][0]
        assert 'overview' not in response['hits'][0]
        assert 'release_date' not in response['hits'][0]
        assert response['hits'][0]['title'] == 'Avengers: Infinity War'
