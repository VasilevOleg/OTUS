import aiohttp

USERS_DATA_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_DATA_URL = "https://jsonplaceholder.typicode.com/posts"


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch_users_data():
    return await fetch_json(USERS_DATA_URL)


async def fetch_posts_data():
    return await fetch_json(POSTS_DATA_URL)
