# Django Multi-Tenant SaaS Boilerplate

A production-ready Django boilerplate showcasing **schema-based multi-tenancy** using `django-tenants`, Django REST Framework, and JWT authentication. Perfect for building SaaS applications where each organization needs complete data isolation.

## Features

- **Schema-Based Multi-Tenancy**: Each tenant gets its own PostgreSQL schema for complete data isolation
- **JWT Authentication**: Stateless authentication using `djangorestframework-simplejwt`
- **Public Tenant Registration**: API endpoint for self-service tenant creation
- **User Management**: Per-tenant user management with role-based access
- **RESTful API**: Clean API design using Django REST Framework
- **Docker Ready**: Complete Docker setup for easy deployment
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Production Ready**: Follows Django best practices and security standards

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation and diagrams.

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL 15 (required for schema-based tenancy)
- **Authentication**: JWT (Simple JWT)
- **Multi-Tenancy**: django-tenants
- **Containerization**: Docker & Docker Compose
- **API Docs**: drf-spectacular (OpenAPI 3.0)

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Django-Tenants-Boilerplate
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. The application will be available at:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs/
   - Admin Panel: http://localhost:8000/admin/

5. Default superuser credentials (public schema):
   - Username: `admin`
   - Password: `admin123`

## API Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tenants/register/` | Register a new tenant |

### Tenant-Specific Endpoints (Requires Authentication)

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/auth/login/` | Login and get JWT tokens |
| POST | `/api/users/auth/refresh/` | Refresh access token |

#### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users (Admin only) |
| POST | `/api/users/` | Create new user (Admin only) |
| GET | `/api/users/me/` | Get current user profile |
| PUT/PATCH | `/api/users/me/` | Update current user profile |
| POST | `/api/users/me/change-password/` | Change password |
| GET/PUT/DELETE | `/api/users/<id>/` | Manage specific user (Admin only) |

#### Tenant Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tenants/me/` | Get current tenant information |

#### Core/Items (Example)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/core/items/` | List all items |
| POST | `/api/core/items/` | Create new item |
| GET/PUT/DELETE | `/api/core/items/<id>/` | Manage specific item |

## Usage Examples

### 1. Register a New Tenant

```bash
curl -X POST http://localhost:8000/api/tenants/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Acme Corporation",
    "schema_name": "acme",
    "domain": "acme.localhost",
    "admin_email": "admin@acme.com",
    "admin_password": "securepassword123",
    "admin_first_name": "John",
    "admin_last_name": "Doe"
  }'
```

Response:
```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": 1,
    "name": "Acme Corporation",
    "schema_name": "acme",
    "is_active": true,
    "created_on": "2024-01-15T10:30:00Z"
  },
  "domain": "acme.localhost"
}
```

### 2. Login as Tenant Admin

```bash
curl -X POST http://acme.localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@acme.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Create a New User (Admin Only)

```bash
curl -X POST http://acme.localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "username": "jane@acme.com",
    "email": "jane@acme.com",
    "password": "password123",
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

### 4. Create an Item

```bash
curl -X POST http://acme.localhost:8000/api/core/items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "name": "First Item",
    "description": "This is a test item"
  }'
```

## Development

### Project Structure

```
Django-Tenants-Boilerplate/
├── apps/
│   ├── tenants/          # Tenant management and registration
│   ├── users/            # User management and authentication
│   └── core/             # Example tenant-specific app
├── config/               # Django settings and configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

### Running Migrations

For shared apps (affects all tenants):
```bash
docker-compose exec web python manage.py migrate_schemas --shared
```

For tenant-specific apps:
```bash
docker-compose exec web python manage.py migrate_schemas
```

### Creating a Superuser in Public Schema

```bash
docker-compose exec web python manage.py createsuperuser
```

### Accessing Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Running Tests

```bash
docker-compose exec web python manage.py test
```

## Multi-Tenancy Explained

### How It Works

1. **Tenant Registration**: When a new tenant registers via `/api/tenants/register/`, the system:
   - Creates a new `Tenant` record in the public schema
   - Creates a new PostgreSQL schema for that tenant
   - Runs migrations in the tenant's schema
   - Creates the admin user in the tenant's schema
   - Creates a `Domain` record linking the subdomain to the tenant

2. **Tenant Routing**: The `TenantMiddleware` automatically:
   - Extracts the domain from the request (e.g., `acme.localhost`)
   - Looks up the corresponding tenant
   - Sets the database connection to use that tenant's schema
   - All subsequent queries are isolated to that schema

3. **Data Isolation**: Each tenant's data is completely isolated:
   - Users in Tenant A cannot access data from Tenant B
   - Each tenant has its own set of users, items, etc.
   - Admin users in each tenant can only manage their own users

### Testing Multi-Tenancy Locally

To test with different tenants locally, you can:

1. **Use different ports with localhost**:
   ```bash
   # Edit your /etc/hosts file (sudo required)
   127.0.0.1 tenant1.localhost
   127.0.0.1 tenant2.localhost
   ```

2. **Use curl with Host header**:
   ```bash
   curl -H "Host: tenant1.localhost" http://localhost:8000/api/...
   ```

3. **Use tools like Postman** and set the Host header manually

## Security Considerations

- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` properly
- Use strong passwords for database and admin accounts
- Implement rate limiting for public endpoints
- Use HTTPS in production
- Configure CORS settings appropriately
- Regular security updates for dependencies

## Deployment

For production deployment:

1. Use a proper WSGI server (Gunicorn, uWSGI)
2. Set up Nginx as a reverse proxy
3. Use PostgreSQL with proper backup strategy
4. Configure environment variables securely
5. Set up proper logging and monitoring
6. Use Redis for caching (optional)
7. Implement proper SSL/TLS certificates

## Contributing

This is a boilerplate project. Feel free to fork and customize for your needs.

## License

MIT License - feel free to use this boilerplate for your projects.

## Author

Created as a portfolio project to demonstrate multi-tenancy implementation in Django.

## Support

For issues or questions, please open an issue on GitHub.
