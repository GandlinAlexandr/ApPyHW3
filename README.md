<a name="readme-top"></a>

[license-shield]: https://img.shields.io/github/license/GandlinAlexandr/ApPyHW3.svg?style=for-the-badge
[license-url]: https://github.com/GandlinAlexandr/ApPyHW3/blob/main/LICENSE

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
        <ul><li><a href="#авторизация">Авторизация</a></li></ul>
        <ul><li><a href="#для-авторизованных-пользователей">Для авторизованных пользователей</a></li></ul>
        <ul><li><a href="#публичные">Публичные</a></li></ul></li>
    <li><a href="#примеры-запросов">Примеры запросов</a></ul>
        <ul><ul><li><a href="#эндпоинты-для-авторизованных-пользователей">Эндпоинты для авторизованных пользователей</a></li></ul>
        <ul><li><a href="#публичные-эндпоинты">Публичные эндпоинты</a></li></ul></ul>
    <ul><li><a href="#структура-базы-данных">Структура базы данных</a></li></ul>
        <ul><ul><li><a href="#таблица-links">Таблица links</a></li></ul>
        <ul><li><a href="#таблица-user">Таблица user</a></li></ul>
        <ul><li><a href="#таблица-expired_links">Таблица expired_links</a></li></ul></ul>
    <ul><li><a href="#кэширование">Кэширование</a></li></ul>
    <ul><li><a href="#время-жизни-ссылок">Время жизни ссылок</a></li></ul>
    <ul><li><a href="#итог">Итог</a></li></ul>
      <li><a href="#лицензия">Лицензия</a></li>
    <li><a href="#контакты">Контакты</a></li>
  </ol>
</details>


## О проекте

Сервис, который позволяет пользователям сокращать длинные ссылки, получать их аналитику и управлять ими. Основная идея — пользователь вводит длинный URL, а ваш сервис генерирует для него короткую ссылку, которую можно использовать для быстрого доступа.

## Технологии

Для реализации проекта использовались следующие технологии:
* [![Docker][DockerBadge]][Docker-url]
* [![Python][Python.org]][Python-url]
  * [![FastAPI][FastAPI-Badge]][FastAPI-url]
* [![Postgres][Postgres-Badge]][Postgres-url]
* [![Redis][Redis-Badge]][Redis-url]


<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

# Содержание проекта

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

Login и Logout производяется по клику `Authorize` в правом верхнем углу Swagger (или соотвествующим запросом) после регистрации посредством POST-запроса.

### Для авторизованных пользователей
Данные ручки работают только для авторизованных пользователей. В противном случае выдают ошибку.
| Метод | Путь | Описание | Тип |
|-------|------|----------|-----|
| `POST` | `/links/shorten` | Создать короткую ссылку (авторизованный) |Authorized only|
| `POST` | `/projects` | Создать пустой проект для ссылок (только владелец) |Authorized only|
| `GET` | `/links/expired` | Получить архив мёртвых ссылок (только владелец) |Authorized only|
| `GET` | `/projects/full` | Получить перечень всех проектов и ссылок в них (только владелец) |Authorized only|
| `PATCH` | `/links/{short_code}` | Обновить URL (только владелец) |Authorized only|
| `DELETE` | `/links/{short_code}` | Удалить ссылку (только владелец) |Authorized only|
| `DELETE` | `/projects/{project_id}` | Удалить проект и все его ссылки (только владелец) |Authorized only|

Видеодемонстрация ограничений доступа неавторизованным пользователям [тут](https://drive.google.com/file/d/1W2vi_za7pZWblNNooPPG2c2M535juTRN/view?usp=sharing). Показана работа всех непубличных эндпоинтов.

Видеодемонстрация аутентификации и работы эндпоинтов для авторизованных пользователей [тут](https://drive.google.com/file/d/1cWvMyLWd9C2UXF5Qiw9R1ZqNHu4qLzEC/view?usp=sharing). Показана работа всех публичных эндпоинтов, а также механизм самоудаления ссылок по указанию даты их смерти при создании. Тот же механизм реализован и для непубличного эндпоинта `POST /links/shorten` для авторизованных пользователей.

### Публичные
Данные ручки доступны для всех пользователей.
| Метод | Путь | Описание | Тип |
|-------|------|----------|-----|
| `POST` | `/links/public` | Создать короткую ссылку |Puplic|
| `GET` | `/{short_code}` | Перенаправление по ссылке |Puplic|
| `GET` | `/links/search?original_url=...` | Поиск по оригинальному URL |Puplic|
| `GET` | `/links/{short_code}/stats` | Получить статистику по ссылке (дата создания, количество переходов, дата последнего использования) |Puplic|
| `GET` | `/links/popular` | Топ популярных ссылок по количеству переходов |Puplic|

Видеодемонстрация работы публичных эндпоинтов [тут](https://drive.google.com/file/d/1Gxi8miXPbfQz2vAmBX7EJGsXi1gr4yN3/view?usp=sharing).

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>


## Примеры запросов

### Эндпоинты для авторизованных пользователей

* Ручка `POST /links/shorten` - Создать короткую ссылку (авторизованный). Обязательные параметры: url. Опциональные параметры: id проекта и дата смерти ссылки и кастомный alias (должен быть уникальным, иначе ошибка).

```powershell
$TOKEN = "your_jwt_token_here"
curl -X POST "http://localhost:8000/links/shorten" `
     -H "Authorization: Bearer $TOKEN" `
     -H "Content-Type: application/json" `
     -d '{
           "original_url": "https://example.com",
           "expires_at": "2025-12-31T23:59:59",
           "project": "MyProject",
           "custom_alias": "my-custom-code"
         }'
```
* `POST /projects` - Создать пустой проект для ссылок (только владелец). Обязательный параметр: название проекта.
```powershell
$TOKEN = "your_jwt_token_here"
curl -X POST "http://localhost:8000/projects" `
     -H "Authorization: Bearer $TOKEN" `
     -H "Content-Type: application/json" `
     -d '{"name":"MyProject"}'
```
* `GET /links/expired` - Получить архив мёртвых ссылок (только владелец). Без параметров.
```powershell
$TOKEN = "your_jwt_token_here"
curl -X GET "http://localhost:8000/links/expired" `
     -H "Authorization: Bearer $TOKEN"
```
* `GET /projects/full` - Получить перечень всех проектов и ссылок в них (только владелец). Без параметров.
```powershell
$TOKEN = "your_jwt_token_here"
curl -X GET "http://localhost:8000/projects/full" `
     -H "Authorization: Bearer $TOKEN"
```
* `PATCH /links/{short_code}` - Обновить URL (только владелец). Обязательный параметр: код ссылки, новая ссылка.
```powershell
$TOKEN = "your_jwt_token_here"
$SHORT = "abc123"
$NEW_URL = "https://updated-url.com"
curl -X PATCH "http://localhost:8000/links/$SHORT?new_url=$NEW_URL" `
     -H "Authorization: Bearer $TOKEN"

```
* `DELETE /links/{short_code}` - Удалить ссылку (только владелец). Обязательный параметр: код ссылки.
```powershell
$TOKEN = "your_jwt_token_here"
$SHORT = "abc123"
curl -X DELETE "http://localhost:8000/links/$SHORT" `
     -H "Authorization: Bearer $TOKEN"
```
* `DELETE /projects/{project_id}` - Удалить проект и все его ссылки (только владелец). Обязательный параметр: id проекта.
```powershell
$TOKEN = "your_jwt_token_here"
$PROJECT_ID = "your_project_id_here"
curl -X DELETE "http://localhost:8000/projects/$PROJECT_ID" `
     -H "Authorization: Bearer $TOKEN"
```
### Публичные эндпоинты

* `POST /links/public` - Создать короткую ссылку. Обязательные параметры: url. Опциональные параметры: дата смерти ссылки и кастомный alias (должен быть уникальным, иначе ошибка).
```powershell
curl -X POST "http://localhost:8000/links/public" `
     -H "Content-Type: application/json" `
     -d '{
           "original_url": "https://example.com",
           "expires_at": "2025-12-31T23:59:59",
           "custom_alias": "my-custom-code"
         }'
```
* `GET /{short_code}` - Перенаправление по ссылке. Без параметров. Ручка срабатывает автоматически при переходе по короткой ссылке.
```powershell
curl -X GET "http://localhost:8000/abc123"
```
* `GET /links/search?original_url=...` - Поиск по оригинальному URL. Обязательный параметр: url.
```powershell
curl -X GET "http://localhost:8000/links/search?original_url=https://example.com"
```
* `GET /links/{short_code}/stats` - Получить статистику по ссылке (дата создания, количество переходов, дата последнего использования). Обязательный параметр: код ссылки.
```powershell
curl -X GET "http://localhost:8000/links/abc123/stats"
```
* `GET /links/popular` - Топ популярных ссылок по количеству переходов. Без параметров.
```powershell
curl -X GET "http://localhost:8000/links/popular"
```

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Структура базы данных

### Таблица `user`
Используется для хранения данных пользователей.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Уникальный идентификатор |
| email | str | Почта/Логин |
| hashed_password | str | Пароль |
| ... | ... | ... |

### Таблица `links`
Используется для хранения данных о живых ссылках.

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
Используется для хранения данных о мёртвых ссылках (архивная база данных).

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

### Таблица `projects`
Хранит данные о проектах пользователя.
| Поле | Тип |
|------|-----|
| id | int |
| name | str |
| created_at | datetime |
| owner_id | UUID, optional |

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Кэширование
В проекте используется Redis для кэширования ответов от наиболее часто запрашиваемых эндпоинтов, что снижает нагрузку на базу данных и ускоряет отклик API. Кэширование реализовано вручную, с помощью redis-py.

Что кэшируется:
* `GET /links/search` — поиск всех коротких ссылок по оригинальному URL (10 минут).
* `GET /links/{short_code}/stats` — статистика по конкретной ссылке (10 минут).
* `GET /links/popular` — топ ссылок по количеству переходов (5 минут).
* `GET /projects/full` — список проектов пользователя с вложенными ссылками (5 минут).
* `GET /links/expired` — просмотр архива просроченных ссылок (5 минут).

Каждый кэшируемый эндпоинт:
* Проверяет наличие данных в Redis по уникальному cache_key.
* Если данные есть — возвращает их сразу.
* Если нет — делает запрос в базу данных, сериализует результат, сохраняет в Redis с TTL и возвращает клиенту.

В некоторых случаях кэш сбрасывается в случае измения таблиц. Например, в случае `GET /links/search`, чтобы сразу было видно, что ссылка удалена или истекала и не висела в ответе эндпоинта, фактически отсутствуя в базе (как, например, в проектах — я намеренно оставил кэш работать в них ради примера: если ссылка удаляктся отдельно от проекта, она какое-то время еще числится в проекте, хотя фактически удалена).

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Время жизни ссылок

Ссылки автоматически удаляются через 30 дней после последнего использования или же, если ссылки ни разу не были использованы, спустя 30 дней после их создания. Кроме того, пользователь сам может указать при её создании, когда она должна удалиться, или удалить её самостоятельно.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

## Итог

Реализованы следующие требования:
- [x] Основные функции реализованы в полном объёме (`POST /links/shorten`, `GET /links/{short_code}`, `DELETE /links/{short_code}`, `PUT /links/{short_code}`, `GET /links/{short_code}/stats`, `GET /links/search`).
- [x] Кэширование ручек.
- [x] Регистрация и привязывание к ней некоторых функционалов сервиса.
- [x] Дополнительные функции:
  - [x] Логика удаления ссылок. Ссылки удаляются спустя 30 дней (переменная в `.env`) после последнего использования. Или, если ссылка не использована, супастя 30 дней после создания.
  - [x] Отображение истории всех истекших ссылок с информацией о них, причём только для авторизованнаго пользователя.
  - [x] Группировка ссылок по проектам. Проект можно создать и помещать в него ссылки при их создании. Проект можно удалить со всеми ссылками. Есть отдельная ручка для просмотра проектов.
  - [x] Создание коротких ссылок для незарегистрированных пользователей. Существует в виде отдельной ручки `POST /links/public`.
  - [x] Вывод самых популярных ссылок среди всех пользователей по числу посещений.

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

# Лицензия

Распространяется по лицензии MIT. Дополнительную информацию см. в файле [`LICENSE`][license-url].

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

# Контакты

Гандлин Александр — [Stepik](https://stepik.org/users/79694206/profile)

Ссылка на проект: [https://github.com/GandlinAlexandr/ApPyHW3](https://github.com/GandlinAlexandr/ApPyHW3)

<p align="right">(<a href="#readme-top">Вернуться к началу</a>)</p>

[FastAPI-Badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/

[Postgres-Badge]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/

[DockerBadge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/

[Python-url]: https://python.org/
[Python.org]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue

[Redis-Badge]: https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
