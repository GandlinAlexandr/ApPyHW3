from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


# Ответ после получения короткой ссылки
class ShortenResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    short_url: HttpUrl
    expires_at: Optional[datetime] = None


# Ответ при поиске ссылки
class SearchLinkResponse(BaseModel):
    short_code: str
    short_url: HttpUrl
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime]


# Ответ при обновлении ссылки
class UpdateLinkRequest(BaseModel):
    expires_at: Optional[datetime] = None


# Ответ при выводе мёртвых ссылок
class ExpiredLinkResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    access_count: int
    expires_at: Optional[datetime]
    last_accessed_at: Optional[datetime] = None
