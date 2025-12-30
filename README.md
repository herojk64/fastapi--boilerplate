# FastAPI Boilerplate — Users, Roles & Permissions

This repository is a production-ready FastAPI boilerplate with a complete Role-Based Access Control (RBAC) system. It provides a well-structured starting point with user, role, and permission management that can be cloned and adapted for any project.

## Key Features

- **Authentication & Authorization**
  - JWT-based authentication with HTTPBearer scheme
  - Permission-based access control (not just role-based)
  - Swagger UI with authorize button for testing protected endpoints
  - Secure password hashing with bcrypt and SHA-256 pre-hash

- **Database & ORM**
  - Async SQLAlchemy 2.x with declarative models
  - Alembic migrations (async-aware)
  - PostgreSQL and MySQL support
  - User, Role, Permission models with many-to-many associations

- **API Features**
  - Complete user CRUD with admin controls
  - Role and permission management endpoints
  - Paginated list endpoints (configurable page size)
  - Profile management (get profile, change password)
  - Guest signup endpoint
  - File management with permission-based access control

- **Helper Utilities**
  - File operations (upload, validation, type detection)
  - Email sending (SMTP)
  - String utilities (slugify, tokens, masking)
  - Date/time helpers (UTC, formatting, expiry)
  - Validators (email, phone, password, URL)
  - Standardized API responses

- **Docker & Deployment**
  - Multi-stage Dockerfile for production
  - Docker Compose with PostgreSQL and Nginx
  - Supervisord for process management
  - Nginx reverse proxy with static file serving
  - Development and production configurations

- **CI/CD**
  - GitHub Actions workflow for automated testing
  - PostgreSQL service container
  - Coverage reports

- **Code Quality**
  - Service layer for business logic separation
  - Async fixtures for testing
  - Type hints throughout
  - Proper error handling and validation

## Requirements

- Python 3.11+ (project requires >=3.11, <3.14)
- Poetry for dependency management
- PostgreSQL or MySQL database

## Quick Start

### 1. Install dependencies

```bash
poetry install
```

### 2. Configure environment

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_TYPE=postgres          # or 'mysql'
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432             # 3306 for MySQL
DB_NAME=fastapi_db

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
BCRYPT_ROUNDS=12

# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin Seeder (optional)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin

# CORS (optional)
CORS=["*"]  # Adjust for production
```

### 3. Run database migrations

```bash
# Create tables
poetry run alembic upgrade head
```

### 4. Seed default admin user and permissions

```bash
# Run with PYTHONPATH set
PYTHONPATH=/path/to/project poetry run python scripts/seed_admin.py

# Or use environment variables
ADMIN_EMAIL=admin@company.com ADMIN_PASSWORD=SecurePass123 poetry run python scripts/seed_admin.py
```

The seeder creates:
- Four default permissions: `administrator.create`, `administrator.read`, `administrator.update`, `administrator.delete`
- An `admin` role with all administrator permissions
- An admin user with the admin role

### 5. Run the application

```bash
# Development mode with auto-reload
poetry run uvicorn app.main:app --reload

# Production mode
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` (or port 8000).
API documentation: `http://localhost:8000/docs`

## API Endpoints

All routes are mounted under `/api/v1` prefix.

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/signup` | Register new user | No |
| POST | `/api/v1/auth/token` | Login and get JWT token | No |

### User Management (Admin Only)

| Method | Endpoint | Description | Permission Required |
|--------|----------|-------------|---------------------|
| GET | `/api/v1/users/` | List users (paginated) | `administrator.read` |
| GET | `/api/v1/users/{user_id}` | Get user by ID | `administrator.read` |
| PUT | `/api/v1/users/{user_id}` | Update user | `administrator.update` |
| DELETE | `/api/v1/users/{user_id}` | Delete user | `administrator.delete` |

### Profile Management (Own Profile Only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users/profile/` | Get own profile | Yes (JWT) |
| PUT | `/api/v1/users/profile/password` | Change own password | Yes (JWT) |

### Role Management

| Method | Endpoint | Description | Permission Required |
|--------|----------|-------------|---------------------|
| GET | `/api/v1/roles/` | List roles (paginated) | No |
| POST | `/api/v1/roles/` | Create role | `administrator.create` |
| POST | `/api/v1/roles/{role_id}/assign/{user_id}` | Assign role to user | `administrator.update` |

### Permission Management

| Method | Endpoint | Description | Permission Required |
|--------|----------|-------------|---------------------|
| GET | `/api/v1/permissions/` | List permissions (paginated) | No |
| POST | `/api/v1/permissions/` | Create permission | `administrator.create` |
| POST | `/api/v1/permissions/role/{role_id}/assign/{permission_id}` | Assign permission to role | `administrator.update` |
| POST | `/api/v1/permissions/user/{user_id}/assign/{permission_id}` | Assign permission to user | `administrator.update` |

### Pagination

List endpoints support pagination with query parameters:
- `page`: Page number (default: 1, min: 1)
- `page_size`: Items per page (default: 10, min: 1, max: 100)

Example: `GET /api/v1/users/?page=2&page_size=20`

Response format:
```json
{
  "items": [...],
  "total": 100,
  "page": 2,
  "page_size": 20,
  "total_pages": 5
}
```

## Database & Migrations

This project uses async SQLAlchemy with Alembic for schema migrations. Alembic is configured to share the same database URL as the application.

### Creating migrations

```bash
# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "describe your changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

### Migration notes

- Alembic uses a synchronous database URL for migrations (automatically configured in `src/database/migrations/env.py`)
- All models are automatically imported so Alembic can detect schema changes
- The initial migration creates all tables: `users`, `roles`, `permissions`, and their association tables

## RBAC System

### How It Works

The boilerplate uses a **permission-based** authorization system, not just role-based:

1. **Permissions** define specific actions (e.g., `administrator.create`, `blog.publish`)
2. **Roles** are collections of permissions (e.g., `admin` role has all `administrator.*` permissions)
3. **Users** get permissions through:
   - Roles they're assigned to
   - Direct permission assignments

### Default Permissions

The seeder creates these permissions:
- `administrator.create` - Create resources (users, roles, permissions)
- `administrator.read` - View admin resources
- `administrator.update` - Update resources and assignments
- `administrator.delete` - Delete resources

### Protecting Endpoints

Use the `require_permission()` dependency to protect endpoints:

```python
from fastapi import APIRouter, Security
from src.routes.deps import require_permission

@router.post("/articles/")
async def create_article(
    _=Security(require_permission("blog.create"))
):
    # Only users with 'blog.create' permission can access
    pass
```

### Adding Custom Permissions

1. Create permissions via API or directly in database:
```bash
curl -X POST http://localhost:8000/api/v1/permissions/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"blog.create","description":"Can create blog posts"}'
```

2. Assign to roles or users:
```bash
# Assign to role
curl -X POST http://localhost:8000/api/v1/permissions/role/1/assign/5 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Assign directly to user
curl -X POST http://localhost:8000/api/v1/permissions/user/3/assign/5 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

3. Protect your endpoints:
```python
@router.post("/blog/")
async def create_post(
    _=Security(require_permission("blog.create"))
):
    pass
```

## Admin Seeder

The `scripts/seed_admin.py` script creates a default admin user with full permissions.

### Configuration

Set these environment variables before running:

```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin
```

### Running the seeder

```bash
# Option 1: Set PYTHONPATH
PYTHONPATH=/path/to/project poetry run python scripts/seed_admin.py

# Option 2: Use inline environment variables
ADMIN_EMAIL=admin@company.com poetry run python scripts/seed_admin.py
```

### What it creates

- ✅ Four administrator permissions (create, read, update, delete)
- ✅ Admin role with all administrator permissions
- ✅ Admin user with the admin role
- ✅ Idempotent: Safe to run multiple times (won't create duplicates)

## Testing

The project includes pytest with async fixtures.

### Running tests

```bash
# Install dependencies
make install

# Run all tests
make test

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_security.py -v

# Run CI-style (fail fast)
make test-ci
```

### Test configuration

- Tests use in-memory SQLite by default (fast)
- Set `TEST_DATABASE_URL` environment variable to test against real database
- Async fixtures in `tests/conftest.py` provide database session

### Example: Testing the seeder

```bash
# Run seeder with test database
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory: \
  poetry run python scripts/seed_admin.py
```

## Password Security

Passwords are hashed using **bcrypt with SHA-256 pre-hash**:

1. Password + `SECRET_KEY` → SHA-256 hash (solves bcrypt's 72-byte limit)
2. SHA-256 output → bcrypt with 12 rounds (configurable via `BCRYPT_ROUNDS`)

This approach:
- ✅ Handles passwords of any length
- ✅ Uses bcrypt's strong algorithm
- ✅ Adds application-specific secret
- ✅ Prevents rainbow table attacks

**Important**: Set a strong `SECRET_KEY` in production!

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── bootstrap/              # App lifecycle and setup
│   │   ├── lifespan.py        # Startup/shutdown events
│   │   ├── middlewares.py     # CORS and other middleware
│   │   ├── setup.py           # Bootstrap configuration
│   │   └── storage.py         # Static file mounting
│   └── configs/
│       └── origins.py         # CORS origins configuration
│
├── src/
│   ├── configs/
│   │   └── db.py              # Database URL builder
│   │
│   ├── database/
│   │   ├── db.py              # SQLAlchemy engine and session
│   │   └── migrations/        # Alembic migrations
│   │       ├── env.py         # Alembic environment
│   │       └── versions/      # Migration files
│   │
│   ├── models/
│   │   ├── __init__.py        # Model registry
│   │   ├── users.py           # User model
│   │   ├── roles.py           # Role model
│   │   ├── permissions.py     # Permission model
│   │   ├── user_role.py       # User-Role association
│   │   ├── user_permission.py # User-Permission association
│   │   ├── role_permission.py # Role-Permission association
│   │   └── schemas/           # Pydantic schemas
│   │       ├── user.py
│   │       ├── role.py
│   │       └── permission.py
│   │
│   ├── routes/
│   │   ├── config.py          # Router registration
│   │   ├── deps.py            # Auth dependencies
│   │   ├── auth/              # Authentication routes
│   │   ├── users/             # User management routes
│   │   ├── roles/             # Role management routes
│   │   └── permissions/       # Permission management routes
│   │
│   ├── services/
│   │   └── authorization.py   # RBAC business logic
│   │
│   └── utils/
│       ├── jwt.py             # JWT token handling
│       └── security.py        # Password hashing
│
├── scripts/
│   ├── seed_admin.py          # Admin seeder script
│   └── run_tests.sh           # Test runner script
│
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── test_security.py       # Security tests
│   └── test_services.py       # Service layer tests
│
├── storage/
│   ├── public/                # Public static files
│   └── private/               # Private uploads
│
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Poetry dependencies
├── pytest.ini                 # Pytest configuration
├── Makefile                   # Development commands
└── README.md                  # This file
```

## Key Design Decisions

### 1. Permission-Based Authorization

Instead of checking role names in route handlers, we use granular permissions:

**❌ Role-based (inflexible)**
```python
if user.role.name != "admin":
    raise Forbidden
```

**✅ Permission-based (flexible)**
```python
_=Security(require_permission("administrator.create"))
```

Benefits:
- Roles can be customized without changing code
- Users can have direct permissions
- Easier to implement complex access rules

### 2. Async Everything

All database operations use async/await:
- Better performance under load
- Non-blocking I/O operations
- Aligns with FastAPI's async capabilities

### 3. Service Layer

Business logic is separated from route handlers:
- Easier to test
- Reusable across different endpoints
- Clear separation of concerns

### 4. Eager Loading

User authentication eagerly loads roles and permissions:
- Prevents lazy-loading issues
- More efficient (fewer queries)
- Avoids "greenlet" errors in async contexts

## Deployment

### Prerequisites

1. Set up production database (PostgreSQL recommended)
2. Set strong `SECRET_KEY` in environment
3. Configure allowed CORS origins
4. Set up reverse proxy (Nginx, Traefik, etc.)

### Environment Variables for Production

```env
DB_TYPE=postgres
DB_USER=prod_user
DB_PASSWORD=strong_password_here
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=prod_db

SECRET_KEY=your-super-secure-secret-key-min-32-chars
BCRYPT_ROUNDS=12
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS=["https://app.example.com","https://admin.example.com"]
```

### Deployment Steps

1. **Run migrations**
```bash
poetry run alembic upgrade head
```

2. **Seed admin user**
```bash
ADMIN_EMAIL=admin@company.com \
ADMIN_PASSWORD=SecurePassword123! \
poetry run python scripts/seed_admin.py
```

3. **Run with Gunicorn + Uvicorn workers**
```bash
poetry run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Use HTTPS in production
- [ ] Configure CORS properly (don't use `["*"]`)
- [ ] Enable database connection pooling
- [ ] Set up rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Monitor logs and errors
- [ ] Update dependencies regularly

## Common Issues & Solutions

### Issue: "A transaction is already begun on this Session"

**Cause**: Service functions trying to manage their own transactions when FastAPI's dependency already provides one.

**Solution**: Service functions should not use `async with session.begin()` - they receive a session that's already in a transaction.

### Issue: "MissingGreenlet" or "greenlet_spawn has not been called"

**Cause**: Accessing lazy-loaded relationships outside of an async context.

**Solution**: Use eager loading with `selectinload()`:
```python
result = await db.execute(
    select(Users)
    .options(selectinload(Users.roles))
)
```

### Issue: Import errors when running seeder

**Cause**: Python can't find the `src` module.

**Solution**: Set PYTHONPATH before running:
```bash
PYTHONPATH=/path/to/project poetry run python scripts/seed_admin.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write tests for new features
- Update README if adding new features
- Keep commits atomic and well-described

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, SQLAlchemy, and Alembic
