<a name="readme-top"></a>

[![MIT][license-shield]][license-url]
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[!['Black'](https://img.shields.io/badge/code_style-black-black?style=for-the-badge)](https://github.com/psf/black)


  <h1 align="center">Сервис генерации коротких ссылок</h1>

  <p align="center">
    Проект в рамках домашней работы по дисциплине "Прикладное программирование на Python"
  </p>


<details>
  <summary>Содержание</summary>
  <ol>
    <li>
      <a href="#о-проекте">О проекте</a>
        <li><a href="#технологии">Технологии</a></li>
    </li>
    <li>
      <a href="#содержание-проекта">Содержание проекта</a>
    </li>
    <ul>
    <li><a href="#зависимости">Зависимости</a></li>
    <li><a href="#начало-работы">Начало работы</a></li>
    <li><a href="#основные-ручки-api">Основные ручки API</a></li>
    <li><a href="#примеры-запросов">Примеры запросов</a></li></ul>
    <li><a href="#структура-базы-данных">Структура базы данных</a></li></ul>
    <li><a href="#кэширование">Кэширование</a></li>
      <li><a href="#лицензия">Лицензия</a></li>
    <li><a href="#контакты">Контакты</a></li>
  </ol>
</details>


## О проекте


## Технологии

Для реализации проекта использовались следующие технологии:
* [![Docker][DockerBadge]][Docker-url]
* [![Python][Python.org]][Python-url]
  * [![FastAPI][FastAPI-Badge]][FastAPI-url]
* [![Postgres][Postgres-Badge]][Postgres-url]
* [![Redis][Redis-Badge]][Redis-url]


<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Содержание проекта

## Зависимости

- Docker + Docker Compose
- Python 3.12 (если запуск вне контейнера)
- PostgreSQL (через docker-compose)
- Redis (кэширование редиректов)

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Начало работы

```bash
# Клонируем репозиторий
git clone https://github.com/your/repo.git
cd repo

# Запуск через Docker Compose
docker compose up --build
```

Swagger-документация будет доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Основные ручки API

### Авторизация

- `POST /auth/register` — регистрация
- `POST /auth/jwt/login` — вход (JWT)
- `GET /users/me` — текущий пользователь

#### 🔗 Работа со ссылками

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/links/shorten` | Создать короткую ссылку (авторизованный) |
| `POST` | `/links/public` | Создать короткую ссылку (анонимный пользователь) |
| `GET` | `/{short_code}` | Перенаправление по ссылке |
| `GET` | `/links/search?original_url=...` | Поиск по оригинальному URL |
| `GET` | `/links/{short_code}/stats` | Получить статистику по ссылке |
| `PATCH` | `/links/{short_code}` | Обновить URL (только владелец) |
| `DELETE` | `/links/{short_code}` | Удалить ссылку (только владелец) |

### Архив и история

- `GET /links/expired` — Получить список истекших/удалённых ссылок (только для владельца)

### Популярные ссылки

- `GET /links/popular` — Топ популярных ссылок по количеству переходов

### Проекты

- `POST /projects` — Создать проект
- `GET /projects/full` — Получить все проекты с их ссылками

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>


## Примеры запросов

### Создание ссылки (авторизованный)

```bash
curl -X POST "http://localhost:8000/links/shorten?original_url=https://google.com"  -H "Authorization: Bearer <TOKEN>"
```

### Создание ссылки (анонимный)

```bash
curl -X POST "http://localhost:8000/links/public?original_url=https://google.com"
```

### Получить статистику

```bash
curl http://localhost:8000/links/abc123/stats
```

### Поиск по URL

```bash
curl http://localhost:8000/links/search?original_url=https://google.com
```

### Все проекты с ссылками

```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/projects/full
```

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Структура базы данных

### Таблица `user`

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Уникальный идентификатор |
| email | str | Почта |
| hashed_password | str | Пароль |
| ... | ... | ... |

### Таблица `links`

| Поле | Тип |
|------|-----|
| id | int |
| original_url | str |
| short_code | str |
| created_at | datetime |
| expires_at | datetime, optional |
| access_count | int |
| last_accessed_at | datetime |
| owner_id | UUID, optional |
| project_id | int, optional |

### Таблица `expired_links`

Хранит истекшие или удалённые ссылки с полной информацией.

### Таблица `projects`

Позволяет группировать ссылки по категориям.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Кэширование

- Redis используется для кэширования редиректов по short_code (1 час).
- Кэш автоматически очищается при удалении или обновлении ссылок.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Лицензия

Распространяется по лицензии MIT. Дополнительную информацию см. в файле [`LICENSE`][license-url].

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Контакты

Гандлин Александр - [Stepik](https://stepik.org/users/79694206/profile)

Ссылка на проект: [https://github.com/GandlinAlexandr/ApPyHW2](https://github.com/GandlinAlexandr/ApPyHW3)

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

[FastAPI-Badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/

[Postgres-Badge]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/

[license-shield]: https://img.shields.io/github/license/GandlinAlexandr/ApPyHW3.svg?style=for-the-badge
[license-url]: https://github.com/GandlinAlexandr/ApPyHW3/blob/main/LICENSE

[DockerBadge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/

[Python-url]: https://python.org/
[Python.org]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue

[Redis-Badge]: https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
