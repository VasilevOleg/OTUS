import aiohttp

# URL для загрузки данных пользователей и постов
USERS_DATA_URL = "https://jsonplaceholder.typicode.com/users"
POSTS_DATA_URL = "https://jsonplaceholder.typicode.com/posts"


# Асинхронная функция для выполнения запросов и получения данных в формате JSON
async def fetch_json(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


# Асинхронная функция для загрузки данных пользователей
async def fetch_users_data():
    async with aiohttp.ClientSession() as session:
        return await fetch_json(session, USERS_DATA_URL)


# Асинхронная функция для загрузки данных постов
async def fetch_posts_data():
    async with aiohttp.ClientSession() as session:
        return await fetch_json(session, POSTS_DATA_URL)
