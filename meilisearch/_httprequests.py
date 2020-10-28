import httpx
from meilisearch.errors import MeiliSearchApiError, MeiliSearchCommunicationError

class HttpRequests:

    config = None
    headers = {}

    def __init__(self, config):
        self.config = config
        self.headers = {
            'X-Meili-Api-Key': self.config.api_key,
            'Content-Type': 'application/json'
        }
        self._client = httpx.AsyncClient()

    async def close(self):
        """Close asyncio http client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Context manager for HttpRequests."""
        return self

    async def __aexit__(self, *args, **kwargs):
        """Close asyncio connection when exiting from context manager."""
        await self.close()

    async def send_request(self, method, path, body=None):
        try:
            request_path = self.config.url + '/' + path
            if body is None:
                request = self._client.build_request(method, request_path, headers=self.headers)
            else:
                request = self._client.build_request(method, request_path, headers=self.headers, json=body)
            response = await self._client.send(request)
            return self.__validate(response)
        except httpx.ConnectError as err:
            raise MeiliSearchCommunicationError(err) from err

    async def get(self, path):
        return await self.send_request("GET", path)

    async def post(self, path, body=None):
        return await self.send_request("POST", path, body)

    async def put(self, path, body=None):
        return await self.send_request("PUT", path, body)

    async def delete(self, path, body=None):
        return await self.send_request("DELETE", path, body)

    @staticmethod
    def __to_json(request):
        if request.content == b'':
            return request
        return request.json()

    @staticmethod
    def __validate(response):
        try:
            response.raise_for_status()
            return HttpRequests.__to_json(response)
        except httpx.HTTPError as err:
            raise MeiliSearchApiError(err, response) from err
