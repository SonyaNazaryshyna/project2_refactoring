# Whispr — Мікроблогінговий Сервіс

![CI — Whispr](https://github.com/SonyaNazaryshyna/project2_refactoring/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/django-5.0-green?logo=django)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=alert_status&token=fb62d898d5a25df51697f20e08bc3148cbe745a4)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=coverage&token=fb62d898d5a25df51697f20e08bc3148cbe745a4)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=bugs&token=fb62d898d5a25df51697f20e08bc3148cbe745a4)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=code_smells&token=fb62d898d5a25df51697f20e08bc3148cbe745a4)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=SonyaNazaryshyna_project2_refactoring&metric=duplicated_lines_density&token=fb62d898d5a25df51697f20e08bc3148cbe745a4)](https://sonarcloud.io/summary/new_code?id=SonyaNazaryshyna_project2_refactoring)

---

![Demo](assets/demo_gif.gif)

## Зміст

1. [Про проєкт](#1-про-проєкт)
2. [Функціонал](#2-функціонал)
3. [Технологічний стек](#3-технологічний-стек)
4. [Архітектура](#4-архітектура)
5. [Структура проєкту](#5-структура-проєкту)
6. [Модель даних](#6-модель-даних)
7. [REST API](#7-rest-api)
8. [Безпека](#8-безпека)
9. [Фронтенд](#9-фронтенд)
10. [Тестування](#10-тестування)
11. [SonarQube](#11-sonarqube)
12. [CI/CD](#12-cicd)
13. [DevOps](#13-devops)
14. [Швидкий старт](#14-швидкий-старт)
15. [Змінні середовища](#15-змінні-середовища)
16. [Корисні команди](#16-корисні-команди)

---

## 1. Про проєкт

**Whispr** — повноцінний мікроблогінговий сервіс, побудований як демонстрація  розуміння повного циклу розробки програмного забезпечення (SDLC). Проєкт охоплює всі етапи: від проєктування архітектури до розгортання у production.

### Проблема яку вирішує

Сучасні соціальні мережі перевантажені функціоналом. Whispr пропонує мінімалістичний, але повнофункціональний простір для коротких думок — до 280 символів — з можливістю коментувати, лайкати та підписуватись на інших.

### Ключові принципи розробки

- **Clean Architecture** — чітке розділення на шари, бізнес-логіка незалежна від фреймворків
- **Domain-Driven Design (DDD)** — Rich Domain Model замість анемічних моделей
- **SOLID** — кожен клас має одну відповідальність, залежності направлені всередину
- **TDD** — тести написані для domain та application шарів з покриттям 94%+
- **DevOps** — Docker Compose, GitHub Actions CI/CD, SonarQube аналіз якості коду

---

## 2. Функціонал

### Автентифікація
- Реєстрація нового акаунту з валідацією (username 3-30 символів, валідний email, пароль мінімум 8 символів)
- Вхід через email + пароль
- JWT токени (access 60 хв + refresh 7 днів)
- Автоматичне оновлення токену при зміні профілю
- Захищений вихід з очищенням cookie

### Дописи (Posts)
- Публікація текстових дописів до 280 символів
- Редагування власних дописів
- М'яке видалення (статус DELETED, дані зберігаються)
- Лайки та анлайки з оптимістичним UI оновленням
- Лічильник лайків в реальному часі

### Коментарі
- Відповідь на будь-який допис
- Перший коментар відображається одразу під дописом
- Кнопка з кількістю коментарів — натискаєш і розгортаються всі
- Форма для написання нового коментаря прямо під дописом
- Коментарі сортуються від найстарішого до найновішого

### Стрічка (Feed)
- Персональна стрічка — лише дописи користувачів на яких підписаний
- Розділ "Всі дописи" — дописи від усіх користувачів платформи
- Сортування за датою (найновіші зверху)
- Кнопка оновлення стрічки

### Профіль
- Публічна сторінка профілю з аватаром, ім'ям, біо
- Всі дописи користувача на його сторінці
- Лічильники: кількість дописів, підписників, підписок
- Підписатись / відписатись одним кліком
- Списки підписників та підписок з переходом на профілі

### Редагування профілю
- Зміна імені користувача (username)
- Зміна біографії (до 500 символів)
- Завантаження фото профілю з комп'ютер
- Попередній перегляд фото перед збереженням
- Автоматичне оновлення JWT після зміни username

### Пошук користувачів
- Пошук за username (часткове співпадіння)
- Результати відображають аватар, ім'я, біо, кількість підписників
- Швидкий пошук з правої панелі на будь-якій сторінці
- Окрема сторінка пошуку `/search`

### Теми оформлення
- **Темна тема** (за замовчуванням) — темний фон, золоті акценти
- **Світла тема** — світлий фон, чіткі контури
- Перемикач у нижній частині бокової панелі
- Вибрана тема зберігається в localStorage між сесіями
- Миттєве перемикання без перезавантаження сторінки

### Адмін панель
- Доступна тільки користувачам з роллю `ROLE_ADMIN`
- Статистика платформи: кількість користувачів, дописів, лайків, підписок
- Таблиця всіх користувачів з пошуком
- Блокування (бан) та розблокування користувачів
- Видалення акаунтів з підтвердженням
- Перегляд останніх 10 дописів платформи

---

## 3. Технологічний стек

| Компонент | Технологія | Версія |
|---|---|---|
| Мова | Python | 3.12 |
| Веб-фреймворк | Django | 5.0.6 |
| REST API | Django REST Framework | 3.15.2 |
| База даних | PostgreSQL | 16 |
| Черга задач | Celery | 5.3.6 |
| Брокер | Redis | 7 |
| Аутентифікація | PyJWT (HS256) | 2.8.0 |
| Хешування паролів | bcrypt | 4.1.3 |
| Валідація | Pydantic v2 | 2.7.1 |
| API документація | drf-spectacular (Swagger) | 0.27.2 |
| Static files | Whitenoise | 6.6.0 |
| Тестування | pytest + pytest-django | latest |
| Лінтер | flake8 + black + isort | latest |
| Контейнеризація | Docker + Compose | v2 |
| CI/CD | GitHub Actions | — |
| Якість коду | SonarQube 10 Community | — |

---

## 4. Архітектура

Проєкт реалізовано за принципами **Clean Architecture** (концентричні шари). Залежності направлені тільки всередину — зовнішні шари залежать від внутрішніх, але не навпаки.

```mermaid
graph TB
    subgraph Frontend
        HTML[HTML Templates]
        JS[JavaScript]
    end
    subgraph Presentation
        Controllers[REST Controllers]
        FrontendViews[Frontend Views]
    end
    subgraph Application
        PostService[Post Service]
        UserService[User Service]
        AuthService[Auth Service]
    end
    subgraph Domain
        Entities[Entities]
        Ports[Repository Interfaces]
    end
    subgraph Infrastructure
        DjangoRepos[Django Repositories]
        ORM[Django ORM Models]
        JWT[JWT Auth]
    end
    subgraph Database
        PG[(PostgreSQL)]
    end

    HTML --> Controllers
    JS --> Controllers
    Controllers --> PostService
    Controllers --> UserService
    Controllers --> AuthService
    PostService --> Ports
    UserService --> Ports
    Ports <|.. DjangoRepos
    DjangoRepos --> ORM
    ORM --> PG
    JWT --> Controllers
  
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│         Django Views, Templates, REST Controllers               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION LAYER                       │   │
│  │      AuthService, PostService, UserService               │   │
│  │      DTOs (Pydantic), Use Cases                          │   │
│  │                                                          │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │                DOMAIN LAYER                        │  │   │
│  │  │  Entities: User, Post                              │  │   │
│  │  │  Value Objects: Email, Username (immutable)        │  │   │
│  │  │  Domain Exceptions: DomainException                │  │   │
│  │  │  Ports (interfaces): UserRepository, PostRepo...   │  │   │
│  │  │                                                    │  │   │
│  │  │  ⭐ Pure Python — NO Django, NO SQLAlchemy         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                  INFRASTRUCTURE LAYER                           │
│    Django ORM, PostgreSQL, JWT, bcrypt, Celery, Redis           │
└─────────────────────────────────────────────────────────────────┘
```

[!Service](/assets/service.png)

### SOLID у проєкті

| Принцип | Реалізація |
|---|---|
| **S** — Single Responsibility | `AuthService` тільки для auth, `PostService` тільки для posts |
| **O** — Open/Closed | Новий репозиторій додається без зміни сервісів |
| **L** — Liskov | `DjangoUserRepository` повністю замінює `UserRepository` |
| **I** — Interface Segregation | `LikeRepository`, `FollowRepository` — окремі інтерфейси |
| **D** — Dependency Inversion | Сервіси залежать від абстракцій (Ports), не від Django ORM |

### Patters
[!Patterns](/assets/patterns.png)

### Потік запиту

```
HTTP Request
    ↓
Middleware (JWT Auth, CSRF, Logging)
    ↓
Controller / View (валідація HTTP input)
    ↓
Application Service (оркестрація use case)
    ↓
Domain Entity (бізнес-правила)
    ↓
Repository Interface (Port)
    ↓
Django ORM (Infrastructure)
    ↓
PostgreSQL
    ↓
HTTP Response (JSON або HTML)
```

[!Sequence](/assets/sequence.png)
---

## 5. Структура проєкту

```
whispr/
├── src/
│   ├── domain/                          # ⭐ Ядро (Pure Python, без фреймворків)
│   │   ├── entities/
│   │   │   ├── user.py                  # Rich User entity
│   │   │   └── post.py                  # Rich Post entity (DRAFT/PUBLISHED/DELETED)
│   │   ├── value_objects/
│   │   │   ├── email.py                 # Immutable, самовалідуючий Email VO
│   │   │   └── username.py              # Immutable Username VO (3-30 символів)
│   │   ├── exceptions/
│   │   │   └── __init__.py              # DomainException
│   │   └── ports/
│   │       └── __init__.py              # Абстрактні репозиторії (інтерфейси)
│   │
│   ├── application/                     # Use Cases (Оркестрація)
│   │   ├── services/
│   │   │   ├── auth_service.py          # Register, Login
│   │   │   ├── post_service.py          # CRUD, Like/Unlike, Feed
│   │   │   └── user_service.py          # Profile, Follow/Unfollow
│   │   └── dtos/
│   │       └── __init__.py              # Pydantic request/response моделі
│   │
│   ├── infrastructure/                  # Реалізації інтерфейсів
│   │   ├── database/
│   │   │   ├── models.py                # Django ORM: UserORM, PostORM, FollowORM, LikeORM
│   │   │   ├── repositories.py          # Реалізації репозиторіїв
│   │   │   ├── migrations/              # Django міграції БД
│   │   │   │   └── 0001_initial.py      # Початкова міграція
│   │   │   └── management/commands/
│   │   │       └── make_admin.py        # python manage.py make_admin <username>
│   │   ├── security/
│   │   │   ├── jwt_provider.py          # JWT encode/decode (importlib trick)
│   │   │   ├── password.py              # bcrypt хешування
│   │   │   └── authentication.py        # DRF custom JWT authenticator
│   │   └── external/
│   │       ├── celery_app.py            # Celery конфігурація
│   │       ├── tasks.py                 # Async tasks (welcome email, notifications)
│   │       └── notification.py          # CeleryNotificationSender
│   │
│   └── presentation/                    # HTTP шар
│       ├── controllers/
│       │   ├── auth_views.py            # POST /api/v1/auth/register, /login
│       │   ├── post_views.py            # CRUD posts + likes API
│       │   ├── user_views.py            # Profile + follow API
│       │   └── frontend_views.py        # Django template views (SSR)
│       ├── middleware/
│       │   ├── exception_handler.py     # Глобальний JSON error handler
│       │   └── logging.py               # Request logging
│       └── config/
│           ├── settings.py              # Django settings
│           ├── urls.py                  # URL routing
│           ├── wsgi.py                  # WSGI entry point
│           └── container.py             # Dependency Injection
│
├── templates/                           # Django HTML templates (SSR)
│   ├── base.html                        # Базовий layout: sidebar, модалки, теми
│   ├── auth/
│   │   ├── login.html                   # Сторінка входу
│   │   └── register.html               # Сторінка реєстрації
│   ├── feed/
│   │   ├── feed.html                    # Персональна стрічка
│   │   ├── explore.html                 # Всі дописи
│   │   └── search.html                  # Пошук користувачів
│   ├── profile/
│   │   ├── profile.html                 # Профіль з дописами
│   │   └── follow_list.html             # Підписники / підписки
│   ├── admin_panel/
│   │   └── dashboard.html               # Адмін панель
│   └── partials/
│       └── post_card.html               # Картка допису (reusable)
│
├── static/                              # CSS та JavaScript
│   ├── css/
│   │   ├── base.css                     # Змінні тем, компоненти, пости, модалки
│   │   ├── layout.css                   # Сайдбар, grid layout, responsive
│   │   ├── auth.css                     # Сторінки логіну/реєстрації
│   │   ├── profile.css                  # Профіль користувача
│   │   └── admin.css                    # Адмін панель
│   └── js/
│       ├── utils.js                     # apiCall(), getCookie(), showToast()
│       ├── theme.js                     # Перемикач темна/світла тема
│       ├── compose.js                   # Модалка нового допису + превью фото
│       ├── posts.js                     # Лайки, видалення постів
│       ├── comments.js                  # Розгортання коментарів, lightbox
│       └── profile.js                   # Follow/unfollow
│
├── tests/
│   ├── unit/
│   └── integration/                    
│
├── docker/
│   └── sonarqube.yml                    # Окремий docker-compose для SonarQube
│
├── .github/
│   └── workflows/
│       └── ci.yml                       # CI/CD: lint → tests → sonar → build
│
├── docker-compose.yml                   # Основне середовище
├── Dockerfile                           # Production образ
├── sonar-project.properties             # SonarQube конфігурація
├── requirements.txt                     # Python залежності
├── setup.cfg                            # flake8, isort, mypy конфіг
├── pytest.ini                           # pytest конфіг
├── manage.py                            # Django entry point
├── .env.example                         # Шаблон змінних середовища
└── README.md                            # Цей файл
```

---

## 6. Модель даних

### ERD (Entity-Relationship Diagram)

[!ERD](/assets/ER.png)

### Ролі користувачів

| Роль | Опис | Доступ |
|---|---|---|
| `ROLE_USER` | Звичайний користувач | Свої пости, лайки, підписки |
| `ROLE_ADMIN` | Адміністратор | + Адмін панель, бан/видалення |

### Use Cases
[!US](/assets/uc.png)

---

## 7. REST API

**Base URL:** `http://localhost:8000/api/v1`
**Swagger UI:** `http://localhost:8000/api/docs/`

### Автентифікація

```
POST /api/v1/auth/register   — Реєстрація
POST /api/v1/auth/login      — Вхід
POST /api/v1/auth/refresh    — Оновлення токену
```

### Дописи

```
GET    /api/v1/posts                    — Всі дописи (explore)
POST   /api/v1/posts                    — Створити допис
GET    /api/v1/posts/{id}               — Один допис
PATCH  /api/v1/posts/{id}               — Редагувати
DELETE /api/v1/posts/{id}               — Видалити
POST   /api/v1/posts/{id}/like          — Лайк
DELETE /api/v1/posts/{id}/like          — Анлайк
GET    /api/v1/feed                     — Персональна стрічка
```

### Користувачі

```
GET    /api/v1/users/me                 — Мій профіль
PATCH  /api/v1/users/me/update          — Оновити профіль
GET    /api/v1/users/{username}         — Профіль користувача
POST   /api/v1/users/{username}/follow  — Підписатись
DELETE /api/v1/users/{username}/follow  — Відписатись
GET    /api/v1/users/{username}/followers — Підписники
GET    /api/v1/users/{username}/following — Підписки
```

### Пагінація

```
GET /api/v1/feed?page=1&size=20

{
  "items": [...],
  "total": 87,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### Відповідь на помилку (завжди JSON)

```json
{
  "status": 422,
  "error": "Domain Rule Violation",
  "message": "Post content cannot be empty.",
  "timestamp": "2025-06-01T12:00:00+00:00"
}
```

---

## 8. Безпека

### JWT Flow

```
Клієнт                              Сервер
  │                                    │
  │── POST /auth/login ───────────────▶│
  │   {email, password}                │ 1. Перевірка credentials
  │                                    │ 2. bcrypt.checkpw()
  │◀── {access_token, refresh_token} ──│ 3. JWT.encode(payload, secret)
  │                                    │
  │── GET /feed ──────────────────────▶│
  │   Authorization: Bearer <token>    │ 4. JWT.decode(token, secret)
  │                                    │ 5. Перевірка exp, type=="access"
  │◀── 200 OK {items: [...]} ──────────│ 6. UserORM.objects.get(id=sub)
```

### JWT Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "role": "ROLE_USER",
  "type": "access",
  "iat": 1717200000,
  "exp": 1717203600
}
```

### Захист паролів

Паролі хешуються через **bcrypt** з автоматичним salt:
```python
bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### CSRF захист

Всі POST форми містять Django CSRF token:
```html
<form method="POST">
  {% csrf_token %}
  ...
</form>
```

---

## 9. Фронтенд

Фронтенд реалізований як **Server-Side Rendering (SSR)** через Django Templates. JavaScript використовується тільки для інтерактивності (лайки, коментарі, теми) без повного перезавантаження сторінки.

### Сторінки

| URL | Опис |
|---|---|
| `/` | Персональна стрічка |
| `/explore` | Всі дописи всіх користувачів |
| `/search?q=sofia` | Пошук користувачів |
| `/profile` | Мій профіль (редирект) |
| `/user/{username}` | Профіль будь-якого користувача |
| `/user/{username}/followers` | Підписники |
| `/user/{username}/following` | Підписки |
| `/login` | Сторінка входу |
| `/register` | Реєстрація |
| `/admin-panel` | Адмін панель (тільки ROLE_ADMIN) |

### Теми оформлення

Реалізовані через CSS змінні:

```css
/* Темна тема (за замовчуванням) */
:root {
  --bg: #0d0d0f;
  --bg-card: #1a1a1f;
  --text: #f5f4f0;
  --accent: #e8b86d;
}

/* Світла тема */
[data-theme="light"] {
  --bg: #f2f1f7;
  --bg-card: #ffffff;
  --text: #1a1a2e;
}
```

Тема зберігається в `localStorage` і застосовується до завантаження сторінки через inline script у `<head>`.

### JavaScript модулі

| Файл | Відповідальність |
|---|---|
| `utils.js` | `apiCall()` з JWT, `getCookie()`, `showToast()` |
| `theme.js` | Перемикач темна/світла тема |
| `compose.js` | Модалка нового допису, превью фото |
| `posts.js` | Лайки (optimistic UI), видалення |
| `comments.js` | Розгортання коментарів, image lightbox |
| `profile.js` | Follow/unfollow |

### Оптимістичний UI для лайків

Лайк оновлюється миттєво на екрані, а потім підтверджується через API. При помилці — відкочується назад:

```javascript
// Миттєво оновлюємо UI
btn.classList.toggle('liked', !isLiked);
countEl.textContent = count + (isLiked ? -1 : 1);

// Потім підтверджуємо через API
try {
  await apiCall(`/api/v1/posts/${id}/like`, {method: liked ? 'DELETE' : 'POST'});
} catch {
  // Відкочуємо при помилці
  btn.classList.toggle('liked', isLiked);
  countEl.textContent = count + (isLiked ? 1 : -1);
}
```

---

## 10. Тестування

### Стратегія

```
        ┌──────────────────────────┐
        │    Integration Tests      │  ← Репозиторії (реальна PostgreSQL)
        ├──────────────────────────┤
        │       Unit Tests          │  ← Domain + Application (mocked repos)
        └──────────────────────────┘
```

## Тестування

**Unit тести** — domain entities, value objects, сервіси через моки.

**Integration тести** — REST API endpoints, frontend views, репозиторії з реальною БД, management команди.

**Покриття: 94%** — `pytest --cov=src`

### Запуск тестів

```bash
# Всі unit тести
docker compose exec web pytest tests/unit/ tests/integration/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --junitxml=junit.xml

# Конкретний файл
docker-compose exec web pytest tests/unit/test_domain_entities.py -v

# Конкретний клас
docker-compose exec web pytest tests/unit/test_services.py::TestPostServiceLike -v
```

### Очікуване покриття

| Шар | Покриття |
|---|---|
| `src/domain` | ~95% |
| `src/application` | ~90% |
| `src/presentation/middleware` | ~95% |

---

## 11. SonarQube

SonarQube аналізує якість коду: баги, вразливості, code smells, дублювання, покриття тестами.

### Запуск SonarQube локально

```bash
# Запусти SonarQube (окремо від основного проєкту)
docker compose -f docker/sonarqube.yml up -d

open http://localhost:9000

# Логін: admin / admin
# Змінити пароль при першому вході
```

### Створення проєкту в SonarQube

1. Натисни **"Create a local project"**
2. **Project key:** `whispr-microblog`
3. **Display name:** `Whispr Microblog`
4. Натисни **"Set Up"** → **"Locally"**
5. **Generate a token** → скопіюй токен

### Локальний аналіз

```bash
docker-compose exec web pytest tests/unit/ \
  --cov=src \
  --cov-report=xml:coverage.xml

docker run --rm \
  --network=host \
  -e SONAR_HOST_URL=http://localhost:9000 \
  -e SONAR_TOKEN=твій_токен_з_sonarqube \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli

# Результати на http://localhost:9000/dashboard?id=whispr-microblog
```

### Конфігурація (sonar-project.properties)

```properties
sonar.projectKey=whispr-microblog
sonar.projectName=Whispr Microblog
sonar.sources=src
sonar.tests=tests
sonar.language=py
sonar.python.version=3.12
sonar.python.coverage.reportPaths=coverage.xml
sonar.exclusions=**/migrations/**,**/staticfiles/**,**/templates/**
```

### SonarCloud (хмарний варіант для GitHub)

Для автоматичного аналізу при кожному push на GitHub:

1. Зайди на **sonarcloud.io** через GitHub акаунт
2. Натисни **"+"** → **"Analyze new project"** → вибери репозиторій
3. Отримай токен
4. Додай до `sonar-project.properties`:
   ```properties
   sonar.organization=твій_organization_key
   ```
5. Додай секрети в GitHub (Settings → Secrets):
   - `SONAR_TOKEN` — токен з SonarCloud
   - `SONAR_HOST_URL` — `https://sonarcloud.io`

---

## 12. CI/CD

### Pipeline (.github/workflows/ci.yml)

```
Push / Pull Request
        │
        ▼
┌───────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  1. Lint      │    │ 2. Unit Tests   │    │ 3. Integration   │
│               │    │                 │    │    Tests         │
│ • black       │    │ • pytest        │    │                  │
│ • isort       │    │ • coverage.xml  │    │ • real postgres  │
│ • flake8      │    │                 │    │ • real redis     │
└───────────────┘    └────────┬────────┘    └──────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  4. SonarQube       │
                   │  (main/develop only)│
                   │  • code quality     │
                   │  • coverage report  │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  5. Docker Build    │
                   │  • build image      │
                   │  • validate compose │
                   └──────────┬──────────┘
                              │
                    (тільки main branch)
                              ▼
                   ┌─────────────────────┐
                   │  6. Deploy          │
                   │  • SSH to server    │
                   │  • git pull         │
                   │  • docker compose   │
                   │  • migrate          │
                   └─────────────────────┘
```

### Необхідні GitHub Secrets

| Secret | Опис |
|---|---|
| `SONAR_TOKEN` | Токен з SonarQube/SonarCloud |
| `SONAR_HOST_URL` | URL SonarQube (`http://...` або `https://sonarcloud.io`) |
| `DEPLOY_HOST` | IP адреса production сервера |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_SSH_KEY` | Приватний SSH ключ |

---

## 13. DevOps

### Docker Compose архітектура

```
┌─────────────────────────────────────────────────────┐
│                docker-compose.yml                   │
│                                                     │
│  ┌──────────┐   ┌───────────┐   ┌───────────────┐  │
│  │   web    │   │ postgres  │   │     redis     │  │
│  │ :8000    │──▶│  :5432    │   │     :6379     │  │
│  │ Django   │   │ healthchk │   │  Celery broker│  │
│  └────┬─────┘   └───────────┘   └───────────────┘  │
│       │                                 ▲           │
│  ┌────▼──────────────────────────────┐  │           │
│  │        celery_worker              │──┘           │
│  │  (background tasks processor)    │              │
│  └───────────────────────────────────┘              │
│  ┌────────────────────────────────────┐             │
│  │   flower :5555 (task monitor)      │             │
│  └────────────────────────────────────┘             │
└─────────────────────────────────────────────────────┘
```

### Healthchecks

Сервіс `web` не стартує поки postgres і redis не пройдуть healthcheck:

```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

---

## 14. Швидкий старт

### Вимоги

- Docker Desktop 24+
- Docker Compose v2
- Git

### Запуск

```bash
# 1. Клонуй репозиторій
git clone https://github.com/your-org/whispr.git
cd whispr

# 2. Скопіюй змінні середовища
cp .env.example .env

# 3. Збери та запусти (перший раз ~3 хвилини)
docker-compose build --no-cache
docker-compose up -d

# 4. Перевір що все запустилось
docker-compose ps
# Всі контейнери мають бути Up/healthy

# 5. Перевір логи web
docker-compose logs web --tail=20
# Має бути: "Starting gunicorn ... Listening at: http://0.0.0.0:8000"
```

### Доступні адреси

| Сервіс | URL |
|---|---|
| **Сайт** | http://localhost:8000 |
| **Swagger API** | http://localhost:8000/api/docs/ |
| **Django Admin** | http://localhost:8000/admin/ |
| **Flower (Celery)** | http://localhost:5555 |

### Створити адміна

```bash
# Зареєструйся через сайт, потім:
docker-compose exec web python manage.py make_admin твій_username

# Тепер у sidebar з'явиться пункт "Адмін"
# та відкриється /admin-panel
```

---

## 15. Змінні середовища

Скопіюй `.env.example` у `.env` і заміни значення:

```env
# Django
DJANGO_SECRET_KEY=your-very-secret-key-change-in-production
DEBUG=False
ALLOWED_HOSTS=localhost 127.0.0.1

# PostgreSQL
POSTGRES_DB=microblog
POSTGRES_USER=microblog
POSTGRES_PASSWORD=strong-password-here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis / Celery
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET=your-jwt-secret-change-in-production
JWT_ACCESS_TTL_MINUTES=60
JWT_REFRESH_TTL_DAYS=7

# SonarQube (для локального аналізу)
SONAR_TOKEN=your-sonarqube-token
SONAR_HOST_URL=http://localhost:9000
```

---

## 16. Корисні команди

```bash
# ── Docker ────────────────────────────────────────
# Запустити
docker-compose up -d

# Зупинити (зберегти дані)
docker-compose down

# Зупинити і видалити дані БД
docker-compose down -v

# Перебудувати без кешу
docker-compose build --no-cache

# Логи конкретного сервісу
docker-compose logs web -f
docker-compose logs celery_worker -f

# ── Django ────────────────────────────────────────
# Django shell
docker-compose exec web python manage.py shell

# Міграції
docker-compose exec web python manage.py migrate

# Зробити адміном
docker-compose exec web python manage.py make_admin username

# Createsuperuser (для Django Admin /admin/)
docker-compose exec web python manage.py createsuperuser

# ── Тести ─────────────────────────────────────────
# Всі unit тести
docker-compose exec web pytest tests/unit/ -v

# З покриттям
docker-compose exec web pytest tests/unit/ \
  --cov=src/domain --cov=src/application \
  --cov-report=term-missing

# ── База даних ────────────────────────────────────
# Підключитись до psql
docker-compose exec postgres psql -U microblog -d microblog

# Переглянути користувачів
docker-compose exec postgres psql -U microblog -d microblog \
  -c "SELECT username, email, role, is_active FROM users;"

# ── SonarQube ─────────────────────────────────────
# Запустити SonarQube
docker compose -f docker/sonarqube.yml up -d

# Зупинити SonarQube
docker compose -f docker/sonarqube.yml down

# Запустити аналіз
docker run --rm --network=host \
  -e SONAR_HOST_URL=http://localhost:9000 \
  -e SONAR_TOKEN=твій_токен \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli

# ── Git / CI ──────────────────────────────────────
# Запушити і запустити CI
git add . && git commit -m "feat: your change" && git push origin main

# Переглянути статус CI
# github.com/your-org/whispr/actions
```
