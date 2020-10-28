import asyncio

MASTER_KEY = 'masterKey'
BASE_URL = 'http://127.0.0.1:7700'

async def clear_all_indexes(client):
    indexes = await client.get_indexes()
    for index in indexes:
        await client.get_index(index['uid']).delete()

async def wait_for_dump_creation(client, dump_uid):
    dump_status = await client.get_dump_status(dump_uid)
    while dump_status['status'] == 'processing':
        asyncio.sleep(0.1)
        dump_status = await client.get_dump_status(dump_uid)
