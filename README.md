# 📝 Whispr — Microblog Service

[![CI/CD Pipeline](https://github.com/SonyaNazaryshyna/project2_refactoring/actions/workflows/ci.yml/badge.svg)](https://github.com/SonyaNazaryshyna/project2_refactoring/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/django-5.0-green?logo=django)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=coverage)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=bugs)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)

Мінімалістичний мікроблогінговий сервіс побудований на **Clean Architecture**. Користувачі публікують дописи до 280 символів, підписуються один на одного, ставлять лайки та керують профілем. Бізнес-логіка повністю незалежна від фреймворків і покрита тестами на 94%.

---

## Зміст

1. [Опис проблеми](#1-опис-проблеми)
2. [Цільова аудиторія](#2-цільова-аудиторія)
3. [Нефункціональні вимоги](#3-нефункціональні-вимоги)
4. [Актори та сценарії використання](#4-актори-та-сценарії-використання)
5. [UML-моделювання](#5-uml-моделювання)
6. [Архітектура системи](#6-архітектура-системи)
7. [Модель даних](#7-модель-даних)
8. [REST API](#8-rest-api)
9. [Безпека (JWT)](#9-безпека-jwt)
10. [Асинхронність (Celery)](#10-асинхронність-celery)
11. [Тестування](#11-тестування)
12. [DevOps: Docker Compose та CI/CD](#12-devops-docker-compose-та-cicd)
13. [Швидкий старт](#13-швидкий-старт)
14. [Структура проєкту](#14-структура-проєкту)
15. [Технологічний стек](#15-технологічний-стек)

---

## 1. Опис проблеми

Сучасні користувачі потребують простого інструменту для обміну короткими думками без перевантаженого інтерфейсу великих соціальних мереж.

**Whispr** вирішує цю проблему: надає мінімалістичний, але функціонально повний мікроблогінговий сервіс з публікацією дописів, персональною стрічкою через підписки, лайками та управлінням профілем. Система побудована за принципами **Clean Architecture** — бізнес-логіка незалежна від Django, легко тестується і масштабується.

---

## 2. Цільова аудиторія

| Роль | Опис |
|---|---|
| **Гість** | Переглядає публічні профілі та дописи без реєстрації |
| **ROLE_USER** | Створює дописи, ставить лайки, підписується на інших |
| **ROLE_ADMIN** | Модерує контент, деактивує акаунти, переглядає статистику |

---

## 3. Нефункціональні вимоги

| Категорія | Вимога |
|---|---|
| **Продуктивність** | Відповідь API ≤ 200 мс для 95% запитів |
| **Безпека** | JWT access (60 хв) + refresh (7 днів), паролі через bcrypt |
| **Масштабованість** | Горизонтальне масштабування через Docker replicas |
| **Надійність** | Healthcheck на БД, застосунок не стартує до готовності PostgreSQL |
| **Зручність** | Swagger UI на `/api/docs/`, глобальний JSON-обробник помилок |
| **Покриття тестами** | ≥ 80% для domain та application шарів (фактично 94%) |

---

## 4. Актори та сценарії використання

#### UC-01: Реєстрація
POST /api/v1/auth/register {username, email, password}
→ Валідація Email і Username Value Objects
→ bcrypt хешування пароля
→ Збереження User
→ Welcome-повідомлення через Celery (async)
→ Повернення {access_token, refresh_token}

#### UC-02: Публікація допису
POST /api/v1/posts/create {content ≤ 280 символів}
→ Post.create() — валідація в доменній сутності
→ Збереження в БД
→ Повернення PostResponse

#### UC-03: Персональна стрічка
GET /api/v1/feed?page=1&size=20
→ Пости від користувачів, на яких підписаний
→ Сортування created_at DESC, пагінація

#### UC-04: Підписка
POST /api/v1/users/{username}/follow
→ Перевірка: не на себе, не дублювати
→ Follow зберігається в БД
→ Сповіщення цільовому юзеру через Celery (async)

#### UC-05: Лайк
POST /api/v1/posts/{id}/like
→ Перевірка: не лайкати двічі
→ post.increment_likes() — бізнес-логіка в entity
→ Like зберігається в таблиці likes

---

## 5. UML-моделювання

### Модель домену
┌──────────────────────────────────────────────────────────────────┐
│                         DOMAIN MODEL                             │
│                                                                  │
│  ┌─────────────────────┐          ┌─────────────────────────┐   │
│  │        User          │  1 : N   │          Post            │   │
│  ├─────────────────────┤◄─────────├─────────────────────────┤   │
│  │ id: UUID             │          │ id: UUID                 │   │
│  │ username: Username   │          │ author_id: UUID          │   │
│  │ email: Email         │          │ content: str (≤280)      │   │
│  │ password_hash: str   │          │ status: PostStatus       │   │
│  │ bio: str             │          │ like_count: int          │   │
│  │ avatar_url: str|None │          │ parent_id: UUID|None     │   │
│  │ is_active: bool      │          │ created_at: datetime     │   │
│  ├─────────────────────┤          ├─────────────────────────┤   │
│  │ + create()           │          │ + create()               │   │
│  │ + deactivate()       │          │ + edit()                 │   │
│  │ + update_bio()       │          │ + delete()               │   │
│  └─────────────────────┘          │ + increment_likes()      │   │
│                                   └─────────────────────────┘   │
│  VALUE OBJECTS (Immutable):                                      │
│  ┌──────────────────┐   ┌──────────────────────────────────┐    │
│  │ Email            │   │ Username                          │    │
│  │ value: str       │   │ value: str (3–30, \w only)        │    │
│  └──────────────────┘   └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

### Діаграма класів
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLASS DIAGRAM                                    │
│                                                                          │
│  DOMAIN                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────────┐ │
│  │   Email VO  │  │ Username VO │  │       DomainException            │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────────────────────────────┘ │
│         └────────┬────────┘                                              │
│  ┌───────────────▼──────────────┐    ┌──────────────────────────────┐   │
│  │         User entity          │    │         Post entity           │   │
│  └──────────────────────────────┘    └──────────────────────────────┘   │
│                                                                          │
│  PORTS (Abstract Interfaces)                                             │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────────┐   │
│  │ UserRepository   │  │ PostRepository  │  │  FollowRepository    │   │
│  └────────┬─────────┘  └────────┬────────┘  └──────────┬───────────┘   │
│           │                     │                        │               │
│  APPLICATION                    │                        │               │
│  ┌────────▼──────┐   ┌──────────▼──────┐   ┌───────────▼──────────┐   │
│  │  AuthService  │   │   PostService   │   │     UserService      │   │
│  └───────────────┘   └─────────────────┘   └──────────────────────┘   │
│                                                                          │
│  INFRASTRUCTURE (Implementations)                                        │
│  ┌────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐  │
│  │ DjangoUserRepo     │  │ DjangoPostRepo      │  │  JWTProvider    │  │
│  └────────────────────┘  └─────────────────────┘  └─────────────────┘  │
│                                                                          │
│  PRESENTATION                                                            │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐                 │
│  │ auth_views   │  │ post_views    │  │ user_views   │                 │
│  └──────────────┘  └───────────────┘  └──────────────┘                 │
└──────────────────────────────────────────────────────────────────────────┘

---

## 6. Архітектура системи

Проєкт реалізовано за **Clean Architecture**:
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│         Django Views · REST Controllers · Middleware            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  APPLICATION LAYER                      │    │
│  │        AuthService · PostService · UserService          │    │
│  │        DTOs (Pydantic) · Use Cases                      │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │                DOMAIN LAYER                     │    │    │
│  │  │  User, Post entities · Email, Username VO       │    │    │
│  │  │  Ports (interfaces) · DomainException           │    │    │
│  │  │  ★ Pure Python — NO Django, NO SQLAlchemy       │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                  INFRASTRUCTURE LAYER                           │
│      Django ORM · PostgreSQL · JWT · bcrypt · Celery · Redis    │
└─────────────────────────────────────────────────────────────────┘

### Принципи SOLID

| Принцип | Де застосовано |
|---|---|
| **S** — Single Responsibility | Кожен сервіс відповідає за один юз-кейс |
| **O** — Open/Closed | Нові репозиторії додаються без зміни сервісів |
| **L** — Liskov | `DjangoUserRepo` повністю замінює `UserRepository` |
| **I** — Interface Segregation | `LikeRepository`, `FollowRepository` — окремі інтерфейси |
| **D** — Dependency Inversion | Сервіси залежать від абстракцій (Ports), не від Django ORM |

### Потік запиту
HTTP Request
↓
Middleware (JWT Auth · Logging · CORS)
↓
Controller (Pydantic DTO validation)
↓
Application Service (orchestrate use case)
↓
Domain Entity (business rules & validation)
↓
Infrastructure Repository (Django ORM · PostgreSQL)
↓
HTTP Response (JSON)

---

## 7. Модель даних
users                                posts
┌────────────────────┐               ┌────────────────────────────────┐
│ id         UUID PK │◄──────────────│ id          UUID PK            │
│ username   VARCHAR │   1 : N       │ author_id   UUID FK            │
│ email      VARCHAR │               │ content     VARCHAR(280)       │
│ password   VARCHAR │               │ status      VARCHAR(20)        │
│ bio        TEXT    │               │ like_count  INTEGER DEFAULT 0  │
│ avatar_url VARCHAR │               │ parent_id   UUID FK → posts.id │
│ is_active  BOOLEAN │               │ created_at  TIMESTAMPTZ        │
│ role       VARCHAR │               │ updated_at  TIMESTAMPTZ        │
│ created_at TSTZ    │               └───|────────────────────────────┘
└────────────────────┘                   | 
│                                        │
│  follows                               │  likes
│  ┌────────────────────┐                │  ┌───────────────┐
├─▶│ follower_id  UUID  │                ├─▶│ user_id  UUID │
└─▶│ following_id UUID  │                └─▶│ post_id  UUID │
   │ PK(flwr, flwg)     │                   │ PK(user, post)│
   └────────────────────┘                   └───────────────┘

### Індекси

```sql
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE UNIQUE INDEX idx_likes_unique ON likes(user_id, post_id);
```

---

## 8. REST API

**Base URL:** `http://localhost:8000/api/v1`
**Swagger UI:** `http://localhost:8000/api/docs/`

### Аутентифікація
POST /api/v1/auth/register    — реєстрація
POST /api/v1/auth/login       — логін
POST /api/v1/auth/refresh     — оновлення токена

### Користувачі
GET    /api/v1/users/{username}           — публічний профіль
GET    /api/v1/users/me                   — мій профіль (auth)
PATCH  /api/v1/users/me/update            — оновити профіль (auth)
POST   /api/v1/users/{username}/follow    — підписатись (auth)
DELETE /api/v1/users/{username}/follow    — відписатись (auth)
GET    /api/v1/users/{username}/followers — підписники
GET    /api/v1/users/{username}/following — підписки

### Дописи
GET    /api/v1/posts/                     — всі дописи
POST   /api/v1/posts/create/              — новий допис (auth)
GET    /api/v1/posts/{id}/                — один допис
PATCH  /api/v1/posts/{id}/edit/           — редагувати (auth, owner)
DELETE /api/v1/posts/{id}/delete/         — видалити (auth, owner)
POST   /api/v1/posts/{id}/like/           — лайк (auth)
DELETE /api/v1/posts/{id}/unlike/         — анлайк (auth)
GET    /api/v1/feed/                      — персональна стрічка (auth)

### Пагінація
```json
{
  "items": [...],
  "total": 87,
  "page": 2,
  "size": 10,
  "pages": 9
}
```

### Формат помилок
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
Client                        Server
│                               │
│── POST /auth/login ──────────▶│
│   {email, password}           │  1. Verify credentials
│                               │  2. Generate JWT pair
│◀─ {access_token,              │
│    refresh_token} ────────────│
│                               │
│── GET /feed ─────────────────▶│
│  Authorization: Bearer <tok>  │  3. Validate JWT signature
│                               │  4. Extract user_id + role
│◀─ 200 OK ───────────────────-─│
│                               │
│── POST /auth/refresh ────────▶│
│   {refresh_token}             │  5. Issue new access_token
│◀─ {access_token} ──────────-──│

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
POST /auth/register
↓ (sync)
AuthService.register()
→ User saved in DB
→ JWT повернуто одразу
↓ (async → Redis)
Celery: send_welcome_email.delay(user_id)
→ Email відправлено у фоні

**Задачі:**
- `send_welcome_email` — welcome email новому користувачу (3 спроби)
- `notify_new_follower` — сповіщення про нового підписника (3 спроби)

**Моніторинг:** Flower UI доступний на `http://localhost:5555`

---

## 11. Тестування
┌────────────────────────────────────────────────┐
│              TEST PYRAMID                      │
│                                                │
│       ┌──────────────────────┐                 │
│       │  Integration Tests   │  ← real DB      │
│       │  (pytest-django)     │                 │
│     ┌─┴──────────────────────┴─┐               │
│     │      Unit Tests          │  ← mocks      │
│     │  (pytest + Mock)         │               │
│     └──────────────────────────┘               │
└────────────────────────────────────────────────┘

**Unit тести** — domain entities, value objects, сервіси через mock-репозиторії.

**Integration тести** — REST API endpoints, frontend views, ORM репозиторії з реальною PostgreSQL, management команди.

**Покриття: 94%**

### Запуск

```bash
# Всі тести з покриттям
docker compose exec web pytest tests/unit/ tests/integration/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --junitxml=junit.xml

# Тільки unit
docker compose exec web pytest tests/unit/

# Тільки integration
docker compose exec web pytest tests/integration/
```

### Приклади тестів

```python
# Domain — валідація бізнес-правил
def test_post_cannot_exceed_280_chars():
    with pytest.raises(DomainException):
        Post.create(author_id=uuid4(), content="x" * 281)

def test_deleted_post_cannot_be_liked():
    post = Post.create(author_id=uuid4(), content="Hello")
    post.delete()
    with pytest.raises(DomainException):
        post.increment_likes()

# Service — оркестрація через моки
def test_create_post_saves_and_returns_response():
    mock_repo = Mock(spec=PostRepository)
    mock_repo.save.return_value = fake_post
    service = PostService(mock_repo, mock_likes, mock_users)
    result = service.create_post(user_id, CreatePostRequest(content="Hi"))
    mock_repo.save.assert_called_once()
    assert result.content == "Hi"
```

---

## 12. DevOps: Docker Compose та CI/CD

### Сервіси Docker Compose
┌──────────────────────────────────────────────────────────┐
│                   docker-compose.yml                     │
│                                                          │
│  ┌──────────┐    ┌────────────┐    ┌──────────────────┐  │
│  │   web    │    │ postgres   │    │     redis        │  │
│  │  :8000   │───▶│  :5432     │    │     :6379        │  │
│  │  Django  │    │ healthcheck│    │  Celery broker   │  │
│  └────┬─────┘    └────────────┘    └──────────────────┘  │
│       │                                   ▲              │
│  ┌────▼─────────────────────────────────┐ │              │
│  │        celery_worker                 │─┘              │
│  │   (background task processor)        │                │
│  └──────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────┘

### CI/CD Pipeline (GitHub Actions)
Push / PR to main
↓

Lint        — black, isort, flake8
Unit Tests  — pytest tests/unit/ + coverage
Docker Build — docker build
Integration Tests — pytest tests/integration/ (PostgreSQL + Redis)
SonarCloud Analysis — Quality Gate


---

## 13. Швидкий старт

### Передумови
- Docker Desktop ≥ 24
- Docker Compose v2

```bash
# 1. Клонувати
git clone https://github.com/SonyaNazaryshyna/project2_refactoring.git
cd project2_refactoring

# 2. Налаштувати змінні середовища
cp .env.example .env

# 3. Запустити
docker compose up -d

# 4. Міграції
docker compose exec web python manage.py migrate

# 5. Створити адміна (опційно)
docker compose exec web python manage.py make_admin <username>
```

### Доступні сервіси

| Сервіс | URL |
|---|---|
| Застосунок | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |
| Flower (Celery) | http://localhost:5555 |

### Змінні середовища (.env.example)

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=whispr
POSTGRES_USER=whispr
POSTGRES_PASSWORD=whispr_pass
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
project2_refactoring/
├── src/
│   ├── domain/                     # ★ Pure Python — no frameworks
│   │   ├── entities/
│   │   │   ├── user.py             # Rich User entity
│   │   │   └── post.py             # Rich Post entity
│   │   ├── value_objects/
│   │   │   ├── email.py            # Immutable Email VO
│   │   │   └── username.py         # Immutable Username VO
│   │   ├── exceptions/
│   │   │   └── init.py         # DomainException
│   │   └── ports/
│   │       └── init.py         # Abstract repository interfaces
│   │
│   ├── application/
│   │   ├── services/
│   │   │   ├── auth_service.py     # Register, Login
│   │   │   ├── post_service.py     # CRUD, Like/Unlike, Feed
│   │   │   └── user_service.py     # Profile, Follow/Unfollow
│   │   └── dtos/
│   │       └── init.py         # Pydantic request/response models
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models.py           # Django ORM models
│   │   │   ├── repositories.py     # Repository implementations
│   │   │   └── migrations/
│   │   ├── security/
│   │   │   ├── jwt_provider.py     # JWT Provider (HS256)
│   │   │   ├── password.py         # bcrypt PasswordEncoder
│   │   │   └── authentication.py   # DRF custom authenticator
│   │   └── external/
│   │       ├── celery_app.py
│   │       ├── tasks.py            # send_welcome_email, notify_new_follower
│   │       └── notification.py
│   │
│   └── presentation/
│       ├── controllers/
│       │   ├── auth_views.py
│       │   ├── post_views.py
│       │   ├── user_views.py
│       │   └── frontend_views.py   # Server-side rendered templates
│       ├── middleware/
│       │   ├── exception_handler.py
│       │   └── logging.py
│       └── config/
│           ├── settings.py
│           ├── urls.py
│           ├── container.py        # Dependency injection
│           └── wsgi.py
│
├── tests/
│   ├── unit/
│   │   ├── test_domain_entities.py
│   │   └── test_services.py
│   └── integration/
│       ├── test_repositories.py
│       ├── test_auth_views.py
│       ├── test_frontend_views.py
│       ├── test_post_views.py
│       ├── test_user_views.py
│       ├── test_container.py
│       └── test_make_admin.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── pytest.ini
├── sonar-project.properties
└── README.md

---

## 15. Технологічний стек

| Компонент | Технологія | Версія |
|---|---|---|
| Мова | Python | 3.12 |
| Веб-фреймворк | Django | 5.0 |
| REST API | Django REST Framework | 3.15 |
| База даних | PostgreSQL | 16 |
| Черга задач | Celery | 5.3 |
| Брокер | Redis | 7 |
| Аутентифікація | PyJWT (HS256) | 2.8 |
| Хешування | bcrypt | 4.1 |
| Валідація | Pydantic v2 | 2.6 |
| API документація | drf-spectacular (Swagger) | 0.27 |
| Тестування | pytest + pytest-django | latest |
| Лінтер | flake8 + black + isort | latest |
| Code Quality | SonarCloud | — |
| Контейнеризація | Docker + Compose v2 | — |
| CI/CD | GitHub Actions | — |
