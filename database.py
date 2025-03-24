from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase
import config
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


DATABASE_URL = config.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

# Модель для хранения коротких ссылок
class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

# Модель для хранения мёртвых ссылок
class ExpiredLink(Base):
    __tablename__ = "expired_links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

# Модель для хранения проектов
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)


# Асинхронная функция получения сессии базы данных
async def get_db():
    async with SessionLocal() as session:
        yield session

# Асинхронная функция инициализации базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    async for s in get_db():
        yield s
