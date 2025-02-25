from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

# Создание асинхронного подключения к базе данных
engine = create_async_engine('sqlite+aiosqlite:///tasks.db', echo=True)

# Создание асинхронного sessionmaker
new_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс для моделей
class Model(DeclarativeBase):
    pass

# Модель TaskOrm, которая будет маппироваться на таблицу 'tasks'
class TasksOrm(Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(nullable=True)


# Функция для создания таблиц в базе данных
async def create_tables():
    async with engine.begin() as conn:
        # Запуск асинхронного запроса на создание таблиц
        await conn.run_sync(Model.metadata.create_all)

# Функция для удаления таблиц в базе данных
async def delete_tables():
    async with engine.begin() as conn:
        # Запуск асинхронного запроса на удаление таблиц
        await conn.run_sync(Model.metadata.drop_all)
