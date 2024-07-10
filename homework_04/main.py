"""
Домашнее задание №4
Асинхронная работа с сетью и бд

доработайте функцию main, по вызову которой будет выполняться полный цикл программы
(добавьте туда выполнение асинхронной функции async_main):
- создание таблиц (инициализация)
- загрузка пользователей и постов
    - загрузка пользователей и постов должна выполняться конкурентно (параллельно)
      при помощи asyncio.gather (https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently)
- добавление пользователей и постов в базу данных
  (используйте полученные из запроса данные, передайте их в функцию для добавления в БД)
- закрытие соединения с БД
"""

import asyncio
from models import engine, Base, Session, User, Post
from jsonplaceholder_requests import fetch_users_data, fetch_posts_data


async def init_db():
    """Инициализация базы данных и создание таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_users_to_db(users_data):
    """Добавление пользователей в базу данных."""
    async with Session() as session:
        async with session.begin():
            session.add_all(
                [User(id=user["id"], name=user["name"], username=user["username"], email=user["email"]) for user in
                 users_data]
            )


async def add_posts_to_db(posts_data):
    """Добавление постов в базу данных."""
    async with Session() as session:
        async with session.begin():
            session.add_all(
                [Post(id=post["id"], user_id=post["userId"], title=post["title"], body=post["body"]) for post in
                 posts_data]
            )


async def async_main():
    """Основная асинхронная функция для выполнения всех шагов."""
    # Инициализация базы данных
    await init_db()

    # Загрузка данных пользователей и постов конкурентно
    users_data, posts_data = await asyncio.gather(
        fetch_users_data(),
        fetch_posts_data()
    )

    # Добавление данных в базу данных
    await add_users_to_db(users_data)
    await add_posts_to_db(posts_data)

    # Закрытие соединения с базой данных
    await engine.dispose()


def main():
    """Основная функция для запуска асинхронного выполнения."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
