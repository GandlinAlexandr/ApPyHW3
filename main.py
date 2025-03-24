from fastapi import Depends, FastAPI, Query, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, Link, init_db, SessionLocal, ExpiredLink, Project
import random, string
from fastapi.responses import RedirectResponse
from schemas import ShortenResponse, SearchLinkResponse, ExpiredLinkResponse
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy.future import select
import redis
import config
from datetime import datetime, timedelta, timezone
from config import CLEANUP_AFTER_DAYS
from sqlalchemy import delete
from auth.db import User
from auth.schemas import UserCreate, UserRead, UserUpdate
from auth.users import auth_backend, current_active_user, fastapi_users
from sqlalchemy import desc
import json


# Использую lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # База данных создаётся при запуске
    # await create_db_and_tables()
    task = asyncio.create_task(delete_expired_links_task())
    task_day = asyncio.create_task(delete_expired_links_task_days())
    yield  # Ожидание завершения приложения
    task.cancel()
    task_day.cancel()


app = FastAPI(lifespan=lifespan)

# Подключение к Redis
redis_client = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)

# Аутентификация
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# @app.get("/authenticated-route")
# async def authenticated_route(user: User = Depends(current_active_user)):
#     return {"message": f"Привет, {user.email}!"}


# Функция для генерации случайного кода
def generate_short_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Фоновая задача для удаления просроченных ссылок
async def delete_expired_links_task():
    while True:
        async with SessionLocal() as session:
            now = datetime.now(timezone.utc).replace(tzinfo=None)

            expired_links = await session.execute(
                select(Link).where(Link.expires_at.isnot(None), Link.expires_at <= now)
            )
            expired_links = expired_links.scalars().all()

            for link in expired_links:
                # Если у ссылки есть владелец — архивируем
                if link.owner_id is not None:
                    archived = ExpiredLink(
                        original_url=link.original_url,
                        short_code=link.short_code,
                        created_at=link.created_at,
                        expires_at=link.expires_at,
                        access_count=link.access_count,
                        last_accessed_at=link.last_accessed_at,
                        owner_id=link.owner_id,
                        project_id=link.project_id,
                    )
                    session.add(archived)

                # 🗑 Удаляем из основной таблицы и Redis
                await session.delete(link)
                redis_client.delete(link.short_code)
                redis_client.delete(f"stats:{link.short_code}")
                redis_client.delete(f"search:{link.original_url}")

            await session.commit()

        await asyncio.sleep(30)  # Проверяем раз в полминуты


# Функция удаления ссылки по времени существования
async def delete_expired_links_task_days():
    while True:
        async with SessionLocal() as session:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            threshold = now - timedelta(days=CLEANUP_AFTER_DAYS)
            """
            Условия удаления:
            1. Был переход, но давно
            2. Или никогда не было перехода, но ссылка старая
            """
            condition = (
                (Link.last_accessed_at != None) & (Link.last_accessed_at < threshold)
            ) | ((Link.last_accessed_at == None) & (Link.created_at < threshold))

            result = await session.execute(select(Link).where(condition))
            links = result.scalars().all()

            for link in links:
                # Сохраняем в архив (только если есть владелец)
                if link.owner_id is not None:
                    archived = ExpiredLink(
                        original_url=link.original_url,
                        short_code=link.short_code,
                        created_at=link.created_at,
                        expires_at=link.expires_at,
                        last_accessed_at=link.last_accessed_at,
                        owner_id=link.owner_id,
                        project_id=link.project_id,
                    )
                    session.add(archived)

                redis_client.delete(link.short_code)

            # Удаляем из базы
            await session.execute(delete(Link).where(condition))
            await session.commit()

        await asyncio.sleep(3600 * 6)  # Проверяем раз в 6 часов


# Функция проверки владельца ссылки
async def verify_link_owner(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
) -> Link:
    result = await db.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    if link.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа")
    return link


# Создание короткой ссылки
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")


# Создание короткой ссылки для зарегистрированного пользователя
@app.post("/links/shorten", response_model=ShortenResponse, tags=["Authorized only"])
async def shorten_url(
    original_url: str = Query(..., description="Исходный URL для сокращения"),
    custom_alias: Optional[str] = Query(
        None, description="Кастомный alias (опционально)"
    ),
    expires_at: Optional[datetime] = Query(
        None,
        description="Дата действия ссылки в формате UTC: 2025-03-23T19:50 (опционально)",
    ),
    project_id: Optional[int] = Query(None, description="ID проекта (опционально)"),
    db: AsyncSession = Depends(get_db),
    token: str = Security(oauth2_scheme),
    user: User = Depends(current_active_user),
):
    """
    Создает короткую ссылку, поддерживает кастомный alias, время жизни и привязку к проекту.
    Для зарегистрированного пользователя.
    """
    if custom_alias:
        existing_link = await db.execute(
            select(Link).where(Link.short_code == custom_alias)
        )
        if existing_link.scalar():
            raise HTTPException(
                status_code=400, detail="Кастомный alias уже существует"
            )
        short_code = custom_alias
    else:
        short_code = generate_short_code()

    # Проверяем, если указан проект — принадлежит ли он пользователю
    if project_id is not None:
        project_result = await db.execute(
            select(Project).where(Project.id == project_id, Project.owner_id == user.id)
        )
        project = project_result.scalar()
        if not project:
            raise HTTPException(
                status_code=404, detail="Проект не найден или не принадлежит вам"
            )

    new_link = Link(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
        owner_id=user.id,
        project_id=project_id,
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)

    return ShortenResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}",
        original_url=original_url,
        expires_at=expires_at,
    )


# Создание короткой ссылки для гостей
@app.post("/links/public", response_model=ShortenResponse, tags=["Public"])
async def shorten_url_public(
    original_url: str = Query(..., description="Исходный URL для сокращения"),
    custom_alias: Optional[str] = Query(
        None, description="Кастомный alias (опционально)"
    ),
    expires_at: Optional[datetime] = Query(
        None,
        description="Дата действия ссылки в формате UTC: 2025-03-23T19:50 (опционально)",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание короткой ссылки для незарегистрированных пользователей.
    """
    if custom_alias:
        existing_link = await db.execute(
            select(Link).where(Link.short_code == custom_alias)
        )
        if existing_link.scalar():
            raise HTTPException(
                status_code=400, detail="Кастомный alias уже существует"
            )
        short_code = custom_alias
    else:
        short_code = generate_short_code()

    new_link = Link(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
        owner_id=None,
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)

    return ShortenResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}",
        original_url=original_url,
        expires_at=expires_at,
    )


# Перенаправление ссылки (запускается автоматически при переходе)
@app.get("/{short_code}", tags=["Public"])
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Перенаправляет пользователя на оригинальный URL по короткому коду.
    """
    # Проверяем кэш Redis
    cached_url = redis_client.get(short_code)
    if cached_url:
        await db.execute(
            Link.__table__.update()
            .where(Link.short_code == short_code)
            .values(
                last_accessed_at=datetime.utcnow(), access_count=Link.access_count + 1
            )
        )
        await db.commit()
        return RedirectResponse(url=cached_url)

    # Получаем ссылку из БД
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalars().first()

    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    # Обновляем статистику
    link.access_count += 1
    link.last_accessed_at = datetime.utcnow()
    await db.commit()

    # Кэшируем URL в Redis
    redis_client.setex(short_code, 3600, link.original_url)

    return RedirectResponse(url=link.original_url)


# Поиск по оригинальной ссылке
@app.get("/links/search", response_model=List[SearchLinkResponse], tags=["Public"])
async def search_link(
    original_url: str = Query(..., description="Оригинальный URL для поиска"),
    db: AsyncSession = Depends(get_db),
):
    """
    Поиск всех коротких ссылок по оригинальному URL.
    Результат кэшируется в Redis на 10 минут.
    """
    cache_key = f"search:{original_url}"

    cached = redis_client.get(cache_key)
    if cached:
        try:
            return [SearchLinkResponse(**item) for item in cached]
        except Exception:
            pass

    result = await db.execute(select(Link).where(Link.original_url == original_url))
    links = result.scalars().all()

    if not links:
        raise HTTPException(status_code=404, detail="Короткий URL не найден")

    response_data = [
        SearchLinkResponse(
            short_code=link.short_code,
            short_url=f"http://localhost:8000/{link.short_code}",
            original_url=link.original_url,
            created_at=link.created_at,
            expires_at=link.expires_at,
        )
        for link in links
    ]

    redis_client.setex(
        cache_key,
        600,
        json.dumps([item.model_dump(mode="json") for item in response_data]),
    )

    return response_data


# Получение статистики по ссылке
@app.get("/links/{short_code}/stats", tags=["Public"])
async def get_link_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """
    Получает статистику по коду в короткой ссылке.
    Результат кэшируется в Redis.
    """
    cache_key = f"stats:{short_code}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar()
    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    stats = {
        "original_url": link.original_url,
        "created_at": link.created_at.isoformat() if link.created_at else None,
        "access_count": link.access_count,
        "last_accessed_at": (
            link.last_accessed_at.isoformat() if link.last_accessed_at else None
        ),
    }

    redis_client.setex(cache_key, 600, json.dumps(stats))

    return stats


# Обновляет оригинальный URL по short_code. Только для владельца.
@app.patch("/links/{short_code}", tags=["Authorized only"])
async def update_short_link(
    short_code: str,
    new_url: str = Query(..., description="Новый URL для сокращения"),
    db: AsyncSession = Depends(get_db),
    token: str = Security(oauth2_scheme),  # для Swagger + авторизации
    user: User = Depends(current_active_user),
):
    """
    Обновляет оригинальный URL по short_code. Только для владельца.
    """
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalars().first()

    if not link:
        raise HTTPException(status_code=404, detail="Короткий URL не найден")

    if link.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой ссылки")

    # Очистка кэша Redis перед обновлением
    redis_client.delete(short_code)

    # Обновление ссылки в БД
    link.original_url = str(new_url)
    await db.commit()
    await db.refresh(link)

    return {
        "short_code": short_code,
        "original_url": str(new_url),
        "short_url": f"http://localhost:8000/{short_code}",
    }


# Удаляет короткую ссылку (только если пользователь — владелец) и сохраняет её в архив.
@app.delete("/links/{short_code}", tags=["Authorized only"])
async def delete_link(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    token: str = Security(oauth2_scheme),
    user: User = Depends(current_active_user),
):
    """
    Удаляет короткую ссылку (только если пользователь — владелец)
    и сохраняет её в архив.
    """
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar()

    if not link:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    if link.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этой ссылки")

    # Архивируем перед удалением
    archived = ExpiredLink(
        original_url=link.original_url,
        short_code=link.short_code,
        created_at=link.created_at,
        expires_at=link.expires_at,
        last_accessed_at=link.last_accessed_at,
        access_count=link.access_count,
        owner_id=link.owner_id,
        project_id=link.project_id,
    )
    db.add(archived)

    await db.delete(link)
    await db.commit()
    redis_client.delete(short_code)

    return {"message": "Ссылка успешно удалена и добавлена в архив"}


# Посмотреть удаленные и просроченные ссылки (только свои)
@app.get(
    "/links/expired", response_model=List[ExpiredLinkResponse], tags=["Authorized only"]
)
async def get_expired_links_for_user(
    db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)
):
    """
    Позволяет посмотреть в архив пользователя с мёртвыми ссылками.
    """
    cache_key = f"expired:{user.id}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    result = await db.execute(
        select(ExpiredLink).where(ExpiredLink.owner_id == user.id)
    )
    links = result.scalars().all()

    response_data = [
        {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "created_at": link.created_at.isoformat() if link.created_at else None,
            "expires_at": link.expires_at.isoformat() if link.expires_at else None,
            "access_count": link.access_count,
            "last_accessed_at": (
                link.last_accessed_at.isoformat() if link.last_accessed_at else None
            ),
            "project_id": link.project_id,
        }
        for link in links
    ]

    redis_client.setex(cache_key, 300, json.dumps(response_data))  # Кэш на 5 минут
    return response_data


# Создание проекта (только авторизованные)
@app.post("/projects", tags=["Authorized only"])
async def create_project(
    name: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """
    Создаёт проект для данного пользователя.
    """
    new_project = Project(name=name, owner_id=user.id)
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return {"id": new_project.id, "name": new_project.name}


# Список проектов
@app.get("/projects/full", tags=["Authorized only"])
async def get_projects_with_links(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """
    Возвращает все проекты пользователя с вложенными ссылками в каждом из них.
    """
    cache_key = f"projects_with_links:{user.id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Получаем проекты пользователя
    projects_result = await db.execute(
        select(Project).where(Project.owner_id == user.id)
    )
    projects = projects_result.scalars().all()

    result = []

    for project in projects:
        # Получаем ссылки, привязанные к проекту
        links_result = await db.execute(
            select(Link).where(Link.project_id == project.id)
        )
        links = links_result.scalars().all()

        result.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "created_at": project.created_at.isoformat(),
                "links": [
                    {
                        "short_code": link.short_code,
                        "original_url": link.original_url,
                        "short_url": f"http://localhost:8000/{link.short_code}",
                        "created_at": link.created_at.isoformat(),
                        "expires_at": (
                            link.expires_at.isoformat() if link.expires_at else None
                        ),
                    }
                    for link in links
                ],
            }
        )

    redis_client.setex(cache_key, 300, json.dumps(result))  # Кэш на 5 минут
    return result


# Топ среди ВСЕХ ссылок
@app.get("/links/popular", tags=["Public"])
async def get_most_popular_links(
    limit: int = Query(10, description="Максимальное количество ссылок в выдаче"),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает самые популярные ссылки по количеству переходов (для всех пользователей).
    Результат кэшируется на 5 минут.
    """
    cache_key = f"popular_links:{limit}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Link).order_by(desc(Link.access_count)).limit(limit)
    )
    links = result.scalars().all()

    response = [
        {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "access_count": link.access_count,
        }
        for link in links
    ]

    redis_client.setex(cache_key, 300, json.dumps(response))

    return response


# Удаление проекта (только авторизованные)
@app.delete("/projects/{project_id}", tags=["Authorized only"])
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    """
    Удаляет проект (если принадлежит пользователю) и все связанные с ним ссылки.
    Архивирует ссылки перед удалением.
    """
    # Проверка наличия проекта и принадлежности пользователю
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=404, detail="Проект не найден или не принадлежит вам"
        )

    # Удаление всех ссылок, привязанных к проекту
    links_result = await db.execute(select(Link).where(Link.project_id == project.id))
    links = links_result.scalars().all()

    for link in links:
        # Архивация перед удалением
        archived = ExpiredLink(
            original_url=link.original_url,
            short_code=link.short_code,
            created_at=link.created_at,
            expires_at=link.expires_at,
            last_accessed_at=link.last_accessed_at,
            access_count=link.access_count,
            owner_id=link.owner_id,
            project_id=link.project_id,
        )
        db.add(archived)

        redis_client.delete(link.short_code)
        await db.delete(link)

    # Удаление самого проекта
    await db.delete(project)
    await db.commit()

    return {
        "message": f"Проект {project.name} и все связанные ссылки архивированы и удалены"
    }
