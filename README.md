# 📝 Microblog Service

![CI — Whispr](https://github.com/SonyaNazaryshyna/project2_refactoring/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/django-5.0-green?logo=django)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=coverage)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=bugs)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)

---

## Зміст

1. [Опис проблеми](#1-опис-проблеми)
2. [Цільова аудиторія](#2-цільова-аудиторія)
3. [Обмеження та нефункціональні вимоги](#3-обмеження-та-нефункціональні-вимоги)
4. [Актори та сценарії використання](#4-актори-та-сценарії-використання)
5. [UML-моделювання](#5-uml-моделювання)
6. [Архітектура системи](#6-архітектура-системи)
7. [Модель даних](#7-модель-даних)
8. [REST API — документація](#8-rest-api--документація)
9. [Безпека (JWT)](#9-безпека-jwt)
10. [Асинхронність (Celery)](#10-асинхронність-celery)
11. [Тестування](#11-тестування)
12. [DevOps: Docker Compose та CI/CD](#12-devops-docker-compose-та-cicd)
13. [Швидкий старт](#13-швидкий-старт)
14. [Структура проєкту](#14-структура-проєкту)

---

## 1. Опис проблеми

Сучасні користувачі потребують простого та швидкого інструменту для обміну короткими думками, коментарями й новинами — без перевантаженого інтерфейсу великих соціальних мереж. Існуючі платформи або надто складні у використанні, або не надають достатнього контролю над власним контентом і аудиторією.

**Microblog Service** вирішує цю проблему: надає мінімалістичний, але функціонально повний мікроблогінговий сервіс, де кожен користувач може публікувати дописи (до 280 символів), формувати персональну стрічку через підписки, взаємодіяти з контентом через лайки та керувати власним профілем. Система побудована за принципами **Clean Architecture**, що забезпечує незалежність бізнес-логіки від фреймворків, легке тестування та масштабованість.

---

## 2. Цільова аудиторія

| Роль | Опис |
|---|---|
| **Гість (Anonymous)** | Переглядає публічні профілі та дописи без реєстрації |
| **Зареєстрований користувач (ROLE_USER)** | Створює дописи, ставить лайки, підписується на інших |
| **Адміністратор (ROLE_ADMIN)** | Модерує контент, деактивує акаунти, переглядає статистику |

---

## 3. Обмеження та нефункціональні вимоги

### Технологічні обмеження

- Мова: **Python 3.12**
- Фреймворк: **Django 5 + Django REST Framework**
- БД: **PostgreSQL 16** (міграції через Alembic / Django migrations)
- Черги: **Celery + Redis**
- Контейнеризація: **Docker Compose**
- Аутентифікація: **JWT (HS256)**

### Нефункціональні вимоги

| Категорія | Вимога |
|---|---|
| **Продуктивність** | Відповідь API ≤ 200 мс для 95% запитів |
| **Безпека** | JWT access token (60 хв), refresh token (7 днів), паролі через bcrypt |
| **Масштабованість** | Горизонтальне масштабування через Docker replicas |
| **Надійність** | Контейнер БД із healthcheck; застосунок не стартує до готовності БД |
| **Зручність** | Swagger UI на `/api/docs/`, глобальний JSON-обробник помилок |
| **Покриття тестами** | ≥ 80% для domain та application шарів |

---

## 4. Актори та сценарії використання

### Ролі користувачів

```
┌─────────────────────────────────────────────────┐
│                   Актори                        │
├──────────────┬──────────────────────────────────┤
│ Гість        │ Перегляд публічних профілів/постів│
│ ROLE_USER    │ CRUD постів, лайки, підписки      │
│ ROLE_ADMIN   │ Модерація, деактивація акаунтів   │
└──────────────┴──────────────────────────────────┘
```

### Use Cases (Сценарії використання)

#### UC-01: Реєстрація користувача
```
Актор:    Гість
Передумова: email та username не зайняті
Кроки:
  1. POST /api/v1/auth/register {username, email, password}
  2. Система валідує Value Objects (Email, Username)
  3. Хешується пароль (bcrypt)
  4. Зберігається новий User
  5. Надсилається welcome-повідомлення (async via Celery)
  6. Повертається JWT {access_token, refresh_token}
Постумова: Користувач авторизований
```

#### UC-02: Авторизація (Login)
```
Актор:    Зареєстрований користувач
Кроки:
  1. POST /api/v1/auth/login {email, password}
  2. Перевірка credentials
  3. Повернення JWT токенів
```

#### UC-03: Публікація допису
```
Актор:    ROLE_USER (авторизований)
Кроки:
  1. POST /api/v1/posts {content (≤280 символів)}
  2. Валідація через Post.create() (Rich Domain Model)
  3. Збереження в БД
  4. Повернення PostResponse з id, author, timestamps
```

#### UC-04: Перегляд персональної стрічки
```
Актор:    ROLE_USER
Кроки:
  1. GET /api/v1/feed?page=1&size=20
  2. Система вибирає пости від користувачів, на яких підписаний
  3. Сортування за created_at DESC
  4. Пагінація результатів
```

#### UC-05: Підписка / відписка
```
Актор:    ROLE_USER
Кроки:
  1. POST /api/v1/users/{username}/follow
  2. Перевірка: не підписуватись на себе, не дублювати підписку
  3. Follow зберігається в БД
  4. Надсилається сповіщення цільовому користувачу (async)
```

#### UC-06: Лайк / анлайк допису
```
Актор:    ROLE_USER
Кроки:
  1. POST /api/v1/posts/{id}/like
  2. Перевірка: не лайкати двічі
  3. post.increment_likes() — логіка в ентіті
  4. Like зберігається в таблиці likes
```

#### UC-07: Редагування профілю
```
Актор:    ROLE_USER
Кроки:
  1. PATCH /api/v1/users/me {bio, avatar_url}
  2. Валідація (bio ≤500 символів, URL формат)
  3. Оновлення та повернення UserResponse
```

---

## 5. UML-Моделювання

### 5.1 Діаграма варіантів використання (Use Case Diagram)

```
                    ┌─────────────────────────────────────────────────┐
                    │              Microblog System                   │
                    │                                                 │
        ┌──────┐    │  ┌──────────────────┐  ┌───────────────────┐  │
        │Guest │────│─▶│ View Public Feed │  │  View Profile     │  │
        └──────┘    │  └──────────────────┘  └───────────────────┘  │
                    │                                                 │
        ┌──────┐    │  ┌──────────────────┐  ┌───────────────────┐  │
        │ User │────│─▶│  Register/Login  │  │  Create Post      │  │
        └──┬───┘    │  └──────────────────┘  └───────────────────┘  │
           │        │                                                 │
           │        │  ┌──────────────────┐  ┌───────────────────┐  │
           ├────────│─▶│   Like/Unlike    │  │  Follow/Unfollow  │  │
           │        │  └──────────────────┘  └───────────────────┘  │
           │        │                                                 │
           │        │  ┌──────────────────┐  ┌───────────────────┐  │
           └────────│─▶│  Edit Profile    │  │  View My Feed     │  │
                    │  └──────────────────┘  └───────────────────┘  │
                    │                                                 │
        ┌───────┐   │  ┌──────────────────┐  ┌───────────────────┐  │
        │ Admin │───│─▶│ Deactivate User  │  │  Delete Any Post  │  │
        └───────┘   │  └──────────────────┘  └───────────────────┘  │
                    └─────────────────────────────────────────────────┘
```

### 5.2 Модель домену (Domain Model)

```
┌──────────────────────────────────────────────────────────────────┐
│                         DOMAIN MODEL                             │
│                                                                  │
│  ┌─────────────────────┐          ┌─────────────────────────┐   │
│  │        User          │          │          Post            │   │
│  ├─────────────────────┤          ├─────────────────────────┤   │
│  │ id: UUID             │   1    * │ id: UUID                 │   │
│  │ username: Username   │◄─────────│ author_id: UUID          │   │
│  │ email: Email         │          │ content: str (≤280)      │   │
│  │ password_hash: str   │          │ status: PostStatus       │   │
│  │ bio: str             │          │ like_count: int          │   │
│  │ avatar_url: str|None │          │ parent_id: UUID|None     │   │
│  │ is_active: bool      │          │ created_at: datetime     │   │
│  │ created_at: datetime │          │ updated_at: datetime     │   │
│  ├─────────────────────┤          ├─────────────────────────┤   │
│  │ + create()           │          │ + create()               │   │
│  │ + deactivate()       │          │ + edit()                 │   │
│  │ + update_bio()       │          │ + delete()               │   │
│  │ + update_avatar()    │          │ + increment_likes()      │   │
│  └─────────────────────┘          │ + decrement_likes()      │   │
│           │                        └─────────────────────────┘   │
│           │ follows                          │ likes              │
│           │                                  │                    │
│  ┌────────▼─────────────┐          ┌────────▼─────────────┐     │
│  │        Follow         │          │         Like          │     │
│  ├──────────────────────┤          ├──────────────────────┤     │
│  │ follower_id: UUID     │          │ user_id: UUID         │     │
│  │ following_id: UUID    │          │ post_id: UUID         │     │
│  │ created_at: datetime  │          │ created_at: datetime  │     │
│  └──────────────────────┘          └──────────────────────┘     │
│                                                                  │
│  VALUE OBJECTS (Immutable):                                      │
│  ┌──────────────────┐   ┌──────────────────────────────────┐    │
│  │ Email            │   │ Username                          │    │
│  │ value: str       │   │ value: str (3-30, alphanum+_)     │    │
│  │ [validated]      │   │ [validated]                       │    │
│  └──────────────────┘   └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 5.3 Діаграма класів (Class Diagram)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLASS DIAGRAM                                    │
│                                                                          │
│  DOMAIN LAYER                                                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐  │
│  │   Email     │    │  Username   │    │       DomainException        │  │
│  │ <<VO>>      │    │  <<VO>>     │    │       <<Exception>>          │  │
│  └─────────────┘    └─────────────┘    └─────────────────────────────┘  │
│         ▲                  ▲                                             │
│         │uses              │uses                                         │
│  ┌──────┴──────────────────┴──────┐    ┌──────────────────────────────┐ │
│  │            User                │    │            Post               │ │
│  │         <<Entity>>             │    │         <<Entity>>            │ │
│  └────────────────────────────────┘    └──────────────────────────────┘ │
│                                                                          │
│  PORTS (Interfaces)                                                      │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │
│  │ UserRepository   │  │ PostRepository  │  │  FollowRepository    │   │
│  │ <<interface>>    │  │ <<interface>>   │  │  <<interface>>       │   │
│  └────────┬─────────┘  └────────┬────────┘  └──────────┬───────────┘   │
│           │                     │                        │               │
│  APPLICATION LAYER              │                        │               │
│  ┌────────▼──────┐   ┌──────────▼──────┐   ┌───────────▼──────────┐   │
│  │  AuthService  │   │   PostService   │   │     UserService      │   │
│  └───────────────┘   └─────────────────┘   └──────────────────────┘   │
│                                                                          │
│  INFRASTRUCTURE LAYER                                                    │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐  │
│  │ DjangoUserRepo     │  │ DjangoPostRepo      │  │  JWTProvider    │  │
│  │ <<impl>>           │  │ <<impl>>            │  │  <<impl>>       │  │
│  └────────────────────┘  └─────────────────────┘  └─────────────────┘  │
│                                                                          │
│  PRESENTATION LAYER                                                      │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐                 │
│  │AuthController│  │PostController │  │UserController│                 │
│  └──────────────┘  └───────────────┘  └──────────────┘                 │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Архітектура системи

Проєкт реалізовано за **Clean Architecture** (концентричні шари):

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│         (Django REST Framework Controllers, Middleware)         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION LAYER                      │   │
│  │        (AuthService, PostService, UserService)          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │                DOMAIN LAYER                     │   │   │
│  │  │  Entities, Value Objects, Ports, Exceptions     │   │   │
│  │  │  (Pure Python — NO Django, NO SQLAlchemy)       │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                  INFRASTRUCTURE LAYER                           │
│      (Django ORM Repos, JWT, Celery, External Services)        │
└─────────────────────────────────────────────────────────────────┘
```

### Принципи SOLID у проєкті

| Принцип | Де застосовано |
|---|---|
| **S** — Single Responsibility | Кожен сервіс відповідає за один юз-кейс |
| **O** — Open/Closed | Нові репозиторії додаються без зміни сервісів |
| **L** — Liskov | `DjangoUserRepo` повністю замінює `UserRepository` |
| **I** — Interface Segregation | `LikeRepository`, `FollowRepository` — окремі інтерфейси |
| **D** — Dependency Inversion | Сервіси залежать від абстракцій (Ports), не від Django ORM |

### Потік запиту (Request Flow)

```
HTTP Request
    │
    ▼
┌──────────────────┐
│  Middleware       │  ← JWT Auth, Logging, CORS
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Controller       │  ← Validates HTTP input (Pydantic DTOs)
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Application      │  ← Orchestrates use case
│  Service          │
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Domain Entity    │  ← Business rules & validation
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Infrastructure   │  ← Django ORM, PostgreSQL
│  Repository       │
└──────────────────┘
         │
    ▼
HTTP Response (JSON)
```

---

## 7. Модель даних

### ERD (Entity-Relationship Diagram)

```
┌──────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                                 │
│                                                                      │
│  users                          posts                                │
│  ┌────────────────────┐         ┌────────────────────────────────┐  │
│  │ id         UUID PK │◄────────│ id          UUID PK            │  │
│  │ username   VARCHAR │  1:N    │ author_id   UUID FK → users.id │  │
│  │ email      VARCHAR │         │ content     VARCHAR(280)        │  │
│  │ password   VARCHAR │         │ status      VARCHAR(20)         │  │
│  │ bio        TEXT    │         │ like_count  INTEGER DEFAULT 0   │  │
│  │ avatar_url VARCHAR │         │ parent_id   UUID FK → posts.id  │  │
│  │ is_active  BOOLEAN │         │ created_at  TIMESTAMPTZ         │  │
│  │ role       VARCHAR │         │ updated_at  TIMESTAMPTZ         │  │
│  │ created_at TSTZ    │         └────────────────────────────────┘  │
│  └────────────────────┘                       │                      │
│           │                                   │                      │
│           │  follows                          │  likes               │
│           │  ┌────────────────────┐           │  ┌───────────────┐  │
│           ├─▶│ follower_id  UUID  │           ├─▶│ user_id  UUID │  │
│           └─▶│ following_id UUID  │           └─▶│ post_id  UUID │  │
│              │ created_at   TSTZ  │              │ created_at TSTZ│  │
│              │ PK(flwr, flwg)     │              │ PK(user, post)│  │
│              └────────────────────┘              └───────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### Індекси для продуктивності

```sql
-- Швидкий пошук постів за автором
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);

-- Стрічка: пости від тих, на кого підписаний
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);

-- Перевірка лайку
CREATE UNIQUE INDEX idx_likes_unique ON likes(user_id, post_id);
```

---

## 8. REST API — документація

**Base URL:** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost:8000/api/docs/`  
**OpenAPI Schema:** `http://localhost:8000/api/schema/`

### Аутентифікація

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
```

### Користувачі

```
GET    /api/v1/users/{username}                — Публічний профіль
GET    /api/v1/users/me                        — Мій профіль (auth)
PATCH  /api/v1/users/me                        — Оновити профіль (auth)
POST   /api/v1/users/{username}/follow         — Підписатись (auth)
DELETE /api/v1/users/{username}/follow         — Відписатись (auth)
GET    /api/v1/users/{username}/followers      — Список підписників
GET    /api/v1/users/{username}/following      — Список підписок
```

### Дописи

```
GET    /api/v1/posts?page=1&size=20&sort=created_at,desc   — Стрічка
POST   /api/v1/posts                           — Новий допис (auth)
GET    /api/v1/posts/{id}                      — Один допис
PATCH  /api/v1/posts/{id}                      — Редагувати (auth, owner)
DELETE /api/v1/posts/{id}                      — Видалити (auth, owner)
POST   /api/v1/posts/{id}/like                 — Лайк (auth)
DELETE /api/v1/posts/{id}/like                 — Анлайк (auth)
```

### Стрічка

```
GET    /api/v1/feed?page=1&size=20             — Персональна стрічка (auth)
```

### Пагінація

```json
GET /api/v1/feed?page=2&size=10

{
  "items": [...],
  "total": 87,
  "page": 2,
  "size": 10,
  "pages": 9
}
```

### Глобальна обробка помилок

```json
{
  "status": 400,
  "error": "Validation Error",
  "message": "Email format is invalid",
  "timestamp": "2025-06-01T12:00:00Z"
}
```

```json
{
  "status": 401,
  "error": "Unauthorized",
  "message": "JWT token is expired or invalid",
  "timestamp": "2025-06-01T12:00:00Z"
}
```

```json
{
  "status": 404,
  "error": "Not Found",
  "message": "User 'johndoe' not found",
  "timestamp": "2025-06-01T12:00:00Z"
}
```

---

## 9. Безпека (JWT)

### Flow авторизації

```
Client                          Server
  │                               │
  │──POST /auth/login ──────────▶│
  │   {email, password}           │ 1. Verify credentials
  │                               │ 2. Generate JWT pair
  │◀─ {access_token,             │
  │    refresh_token} ────────────│
  │                               │
  │──GET /feed ─────────────────▶│
  │  Authorization: Bearer <tok>  │ 3. Validate JWT signature
  │                               │ 4. Extract user_id + role
  │◀─ 200 OK {items: [...]} ─────│
  │                               │
  │──POST /auth/refresh ────────▶│
  │   {refresh_token}             │ 5. Issue new access_token
  │◀─ {access_token} ────────────│
```

### JWT Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "role": "ROLE_USER",
  "iat": 1717200000,
  "exp": 1717203600
}
```

### Ролі та дозволи

| Endpoint | ROLE_USER | ROLE_ADMIN |
|---|:---:|:---:|
| GET публічних ресурсів | ✅ | ✅ |
| Створити допис | ✅ | ✅ |
| Редагувати/видалити власний допис | ✅ | ✅ |
| Видалити будь-який допис | ❌ | ✅ |
| Деактивувати користувача | ❌ | ✅ |

---

## 10. Асинхронність (Celery)

### Сценарій: Welcome Email та сповіщення про підписника

```
User registers
     │
     ▼
POST /auth/register
     │
     ▼ (sync)
AuthService.register()
  → User saved in DB
  → Returns JWT immediately (202-like)
     │
     ▼ (async — enqueued to Redis)
Celery Task: send_welcome_email.delay(user_id)
  → Runs in background worker
  → Sends email via SMTP
```

### Задачі Celery

```python
# src/infrastructure/external/tasks.py

@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: str):
    """Надсилає welcome-email новому користувачу."""
    ...

@celery_app.task(bind=True, max_retries=3)
def notify_new_follower(self, user_id: str, follower_id: str):
    """Сповіщає користувача про нового підписника."""
    ...
```

---

## 11. Тестування

### Стратегія тестування

```
┌────────────────────────────────────────────────────┐
│              TEST PYRAMID                          │
│                                                    │
│         ┌──────────────────┐                       │
│         │  Integration Tests│  ← Repository layer  │
│         │    (pytest +      │     (real PostgreSQL) │
│         │   TestContainers) │                       │
│       ┌─┴──────────────────┴─┐                     │
│       │    Unit Tests          │ ← Domain + Service  │
│       │    (pytest + mock)     │   (mocked repos)    │
│       └────────────────────────┘                    │
└────────────────────────────────────────────────────┘
```

### Приклад unit-тесту (Domain)

```python
# tests/unit/test_post_entity.py

def test_post_cannot_exceed_280_chars():
    with pytest.raises(DomainException):
        Post.create(author_id=uuid4(), content="x" * 281)

def test_like_increments_count():
    post = Post.create(author_id=uuid4(), content="Hello")
    post.increment_likes()
    assert post.like_count == 1

def test_deleted_post_cannot_be_liked():
    post = Post.create(author_id=uuid4(), content="Hello")
    post.delete()
    with pytest.raises(DomainException):
        post.increment_likes()
```

### Приклад unit-тесту (Service)

```python
# tests/unit/test_post_service.py

def test_create_post_saves_and_returns_response():
    mock_repo = Mock(spec=PostRepository)
    mock_repo.save.return_value = fake_post
    service = PostService(mock_repo, mock_likes, mock_users)
    
    result = service.create_post(user_id, CreatePostRequest(content="Hi"))
    
    mock_repo.save.assert_called_once()
    assert result.content == "Hi"
```

### Запуск тестів

```bash
# Всі тести
pytest

# Тільки unit
pytest tests/unit/

# З покриттям
pytest --cov=src --cov-report=html

# Integration (потребує Docker)
pytest tests/integration/
```

---

## 12. DevOps: Docker Compose та CI/CD

### Docker Compose архітектура

```
┌──────────────────────────────────────────────────────────┐
│                   docker-compose.yml                     │
│                                                          │
│  ┌──────────┐    ┌────────────┐    ┌──────────────────┐ │
│  │  web     │    │ postgres   │    │     redis        │ │
│  │ :8000    │───▶│  :5432     │    │     :6379        │ │
│  │ Django   │    │ healthcheck│    │  Celery broker   │ │
│  └────┬─────┘    └────────────┘    └──────────────────┘ │
│       │                                   ▲              │
│  ┌────▼─────────────────────────────────┐ │              │
│  │          celery_worker               │─┘              │
│  │   (background task processor)        │                │
│  └──────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline (GitHub Actions)

```
Push / PR
    │
    ▼
┌──────────────────────────────────────┐
│  CI Pipeline (.github/workflows/)    │
│                                      │
│  1. Lint (flake8, black --check)     │
│  2. Type Check (mypy)                │
│  3. Unit Tests (pytest tests/unit/)  │
│  4. Build Docker Image               │
│  5. Integration Tests (pytest tests/)│
│                                      │
│  On main branch merge:               │
│  6. Push image to registry           │
│  7. Deploy (docker-compose pull+up)  │
└──────────────────────────────────────┘
```

---

## 13. Швидкий старт

### Передумови

- Docker Desktop ≥ 24
- Docker Compose v2
- Git

### Запуск одною командою

```bash
# 1. Клонувати репозиторій
git clone https://github.com/your-org/microblog.git
cd microblog

# 2. Скопіювати .env
cp .env.example .env

# 3. Запустити все середовище
docker-compose up -d

# 4. Застосувати міграції
docker-compose exec web python manage.py migrate

# 5. Створити superuser (опційно)
docker-compose exec web python manage.py createsuperuser
```

### Доступні сервіси після запуску

| Сервіс | URL |
|---|---|
| **API** | http://localhost:8000/api/v1/ |
| **Swagger UI** | http://localhost:8000/api/docs/ |
| **Django Admin** | http://localhost:8000/admin/ |
| **Flower (Celery Monitor)** | http://localhost:5555/ |

### Змінні середовища (.env.example)

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
POSTGRES_DB=microblog
POSTGRES_USER=microblog
POSTGRES_PASSWORD=microblog_pass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-jwt-secret
JWT_ACCESS_TTL_MINUTES=60
JWT_REFRESH_TTL_DAYS=7
ALLOWED_HOSTS=localhost 127.0.0.1
```

---

## 14. Структура проєкту

```
microblog/
├── src/
│   ├── domain/                     # ⭐ Ядро (Pure Python, no frameworks)
│   │   ├── entities/
│   │   │   ├── user.py             # Rich User entity
│   │   │   └── post.py             # Rich Post entity
│   │   ├── value_objects/
│   │   │   ├── email.py            # Immutable Email VO
│   │   │   └── username.py         # Immutable Username VO
│   │   ├── exceptions/
│   │   │   └── __init__.py         # DomainException
│   │   └── ports/
│   │       └── __init__.py         # Abstract Repository interfaces
│   │
│   ├── application/                # Use Cases (Orchestration)
│   │   ├── services/
│   │   │   ├── auth_service.py     # Register, Login
│   │   │   ├── post_service.py     # CRUD, Like/Unlike
│   │   │   └── user_service.py     # Profile, Follow/Unfollow
│   │   └── dtos/
│   │       └── __init__.py         # Pydantic request/response models
│   │
│   ├── infrastructure/             # Framework implementations
│   │   ├── database/
│   │   │   ├── models.py           # Django ORM models
│   │   │   ├── repositories.py     # Repository implementations
│   │   │   └── migrations/         # Django DB migrations
│   │   ├── security/
│   │   │   ├── jwt.py              # JWT Provider
│   │   │   ├── password.py         # bcrypt PasswordEncoder
│   │   │   └── authentication.py   # DRF custom authenticator
│   │   └── external/
│   │       ├── celery_app.py       # Celery configuration
│   │       ├── tasks.py            # Async tasks
│   │       └── notification.py     # NotificationSender impl
│   │
│   └── presentation/               # HTTP Layer
│       ├── controllers/
│       │   ├── auth_views.py       # /auth/register, /auth/login
│       │   ├── post_views.py       # /posts CRUD + likes
│       │   └── user_views.py       # /users profile + follows
│       ├── middleware/
│       │   ├── exception_handler.py # Global JSON error handler
│       │   └── logging.py          # Request logging
│       └── config/
│           ├── settings.py         # Django settings
│           ├── urls.py             # URL routing
│           └── wsgi.py
│
├── tests/
│   ├── unit/
│   │   ├── test_user_entity.py
│   │   ├── test_post_entity.py
│   │   ├── test_auth_service.py
│   │   └── test_post_service.py
│   └── integration/
│       ├── test_user_repository.py
│       └── test_post_repository.py
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI pipeline
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── pytest.ini
├── setup.cfg                       # flake8, mypy config
└── README.md                       # ← Цей файл
```

---

## Технологічний стек

| Компонент | Технологія | Версія |
|---|---|---|
| Мова | Python | 3.12 |
| Веб-фреймворк | Django | 5.0 |
| REST API | Django REST Framework | 3.15 |
| База даних | PostgreSQL | 16 |
| ORM | Django ORM | вбудований |
| Черга задач | Celery | 5.3 |
| Брокер | Redis | 7 |
| Аутентифікація | PyJWT (HS256) | 2.8 |
| Хешування паролів | bcrypt | 4.1 |
| Валідація | Pydantic v2 | 2.6 |
| Документація API | drf-spectacular (Swagger) | 0.27 |
| Тестування | pytest + pytest-django | latest |
| Лінтер | flake8 + black | latest |
| Контейнеризація | Docker + Compose | v2 |
| CI/CD | GitHub Actions | — |

---

*Документ підготовлено у рамках курсового проєкту. Microblog Service демонструє повний SDLC: від проектування архітектури та моделювання бази даних до REST API, тестування та DevOps.*
