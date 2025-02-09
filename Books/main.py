from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

# FastAPI and SQLAlchemy setup
app = FastAPI()
engine = create_async_engine('sqlite+aiosqlite:///books.db')
new_session = async_sessionmaker(engine, expire_on_commit=False)

# Session Dependency
async def get_session():
    async with new_session() as session:
        yield session

# Pydantic schemas for request and response
class BookAddShema(BaseModel):
    title: str
    author: str

class BookShema(BookAddShema):
    id: int

# SQLAlchemy models
class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]

# Setup Database Route
@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"ok": True}

# Add Book Route
@app.post("/books")
async def add_books(data: BookAddShema, session: AsyncSession = Depends(get_session)):
    new_book = BookModel(title=data.title, author=data.author)
    session.add(new_book)
    await session.commit()
    return {"ok": True}

# Get Books Route
@app.get("/books", response_model=list[BookShema])
async def get_books(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BookModel))
    books = result.scalars().all()
    return books
