# Project Structure

```
Django-Tenants-Boilerplate/
│
├── apps/                           # Django applications
│   ├── __init__.py
│   │
│   ├── tenants/                    # Tenant management (SHARED APP)
│   │   ├── __init__.py
│   │   ├── admin.py               # Admin interface for tenants
│   │   ├── apps.py
│   │   ├── models.py              # Tenant & Domain models
│   │   ├── serializers.py         # Tenant registration serializer
│   │   ├── urls.py                # Public registration endpoint
│   │   └── views.py               # Tenant registration view
│   │
│   ├── users/                      # User management (TENANT APP)
│   │   ├── __init__.py
│   │   ├── admin.py               # User admin interface
│   │   ├── apps.py
│   │   ├── models.py              # Uses Django's default User model
│   │   ├── serializers.py         # User CRUD & JWT serializers
│   │   ├── urls.py                # Auth & user management endpoints
│   │   └── views.py               # User management views
│   │
│   └── core/                       # Business logic (TENANT APP)
│       ├── __init__.py
│       ├── admin.py               # Item admin interface
│       ├── apps.py
│       ├── models.py              # Example: Item model
│       ├── serializers.py         # Business object serializers
│       ├── urls.py                # Business API endpoints
│       └── views.py               # CRUD views for items
│
├── config/                         # Django configuration
│   ├── __init__.py
│   ├── asgi.py                    # ASGI configuration
│   ├── settings.py                # Django settings with multi-tenancy
│   ├── urls.py                    # Main URL configuration
│   └── wsgi.py                    # WSGI configuration
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── ARCHITECTURE.md                 # Detailed architecture documentation
├── CONTRIBUTING.md                 # Contribution guidelines
├── docker-compose.yml              # Docker Compose configuration
├── docker-entrypoint.sh            # Docker startup script
├── Dockerfile                      # Docker image definition
├── LICENSE                         # MIT License
├── manage.py                       # Django management script
├── postman_collection.json         # Postman API collection
├── README.md                       # Main documentation
├── requirements.txt                # Python dependencies
└── TESTING.md                      # Testing guide

## Key Files Explained

### Configuration Files

- **settings.py**: Core Django settings with django-tenants configuration
  - `SHARED_APPS`: Apps stored in public schema (tenants)
  - `TENANT_APPS`: Apps replicated in each tenant schema (users, core)
  - JWT authentication configuration
  - Database router for multi-tenancy

- **docker-compose.yml**: Defines two services
  - `db`: PostgreSQL 15 database
  - `web`: Django application

- **.env.example**: Template for environment variables
  - Database credentials
  - Django secret key
  - Debug mode settings

### App Structure

#### Shared Apps (Public Schema)
- **tenants**: Manages tenant provisioning and routing
  - Stores: Tenant info, domain mappings
  - Endpoints: Public registration

#### Tenant Apps (Per-Tenant Schema)
- **users**: User management within each tenant
  - Stores: Users (completely isolated per tenant)
  - Endpoints: JWT auth, user CRUD, password change

- **core**: Example business logic
  - Stores: Items (example tenant-specific data)
  - Endpoints: CRUD operations for items
  - Demonstrates: Tenant data isolation

### Documentation Files

- **README.md**: Quick start, features, API reference
- **ARCHITECTURE.md**: Deep dive into multi-tenancy design
- **TESTING.md**: Step-by-step testing instructions
- **CONTRIBUTING.md**: Guidelines for contributors

### Development Files

- **docker-entrypoint.sh**: Automated setup script
  - Waits for PostgreSQL
  - Runs migrations
  - Creates default superuser
  - Starts Django server

- **postman_collection.json**: Ready-to-use API collection
  - All endpoints documented
  - Auto-saves JWT tokens
  - Organized by functionality

## Data Flow

1. **Request arrives** → TenantMiddleware extracts domain
2. **Tenant lookup** → Domain mapped to tenant in public schema
3. **Schema switch** → Database connection set to tenant's schema
4. **Authentication** → JWT validated, user loaded from tenant schema
5. **Business logic** → Views/serializers operate on tenant-specific data
6. **Response** → Data returned only from current tenant

## Schema Organization

```
PostgreSQL Database: django_tenants
│
├── PUBLIC SCHEMA
│   ├── tenants_tenant      (All tenants)
│   └── tenants_domain      (Domain → Tenant mapping)
│
├── SCHEMA: acme
│   ├── auth_user           (Acme's users)
│   ├── core_item           (Acme's items)
│   └── ... (all TENANT_APPS tables)
│
├── SCHEMA: beta
│   ├── auth_user           (Beta's users)
│   ├── core_item           (Beta's items)
│   └── ... (all TENANT_APPS tables)
│
└── ... (one schema per tenant)
```

## File Count by Type

- Python files: 25
- Markdown docs: 5
- Config files: 6
- Total files: ~36

## Lines of Code

Approximately:
- Python code: ~1,500 lines
- Documentation: ~2,500 lines
- Configuration: ~300 lines

## Adding New Features

To add a new tenant-specific feature:

1. Create new app in `apps/`
2. Add models, serializers, views
3. Add to `TENANT_APPS` in settings.py
4. Create URL patterns
5. Run `migrate_schemas`
6. Update documentation

To add a shared feature:

1. Add to `SHARED_APPS` in settings.py
2. Models go in public schema
3. Accessible across all tenants
4. Run `migrate_schemas --shared`
