import asyncio
from .models import Base, User, Post, engine, Session
from .jsonplaceholder_requests import fetch_users_data, fetch_posts_data

# Асинхронная функция для инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Асинхронная функция для добавления пользователей в базу данных
async def add_users(session, users_data):
    users = [User(name=user["name"], username=user["username"], email=user["email"]) for user in users_data]
    session.add_all(users)
    await session.commit()

# Асинхронная функция для добавления постов в базу данных
async def add_posts(session, posts_data):
    posts = [Post(user_id=post["userId"], title=post["title"], body=post["body"]) for post in posts_data]
    session.add_all(posts)
    await session.commit()

# Основная асинхронная функция для выполнения всего цикла программы
async def async_main():
    async with Session() as session:
        await init_db()
        users_data, posts_data = await asyncio.gather(
            fetch_users_data(),
            fetch_posts_data(),
        )
        await add_users(session, users_data)
        await add_posts(session, posts_data)
        await session.close()

# Запуск основной функции
def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
