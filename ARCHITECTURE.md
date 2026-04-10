# Architecture Documentation

## Overview

This Django multi-tenant SaaS boilerplate implements **schema-based multi-tenancy** using PostgreSQL schemas. Each tenant (organization/client) gets their own isolated database schema, ensuring complete data separation and security.

## Multi-Tenancy Architecture

### Schema-Based Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │          PUBLIC SCHEMA (Shared)                    │    │
│  │                                                     │    │
│  │  ├── Tenant Table                                  │    │
│  │  │   ├── id: 1, name: "Acme Corp", schema: "acme" │    │
│  │  │   ├── id: 2, name: "Beta Inc", schema: "beta"  │    │
│  │  │   └── ...                                       │    │
│  │                                                     │    │
│  │  ├── Domain Table                                  │    │
│  │  │   ├── domain: "acme.app.com" → tenant_id: 1    │    │
│  │  │   ├── domain: "beta.app.com" → tenant_id: 2    │    │
│  │  │   └── ...                                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │        SCHEMA: "acme" (Tenant 1)                   │    │
│  │                                                     │    │
│  │  ├── Users                                          │    │
│  │  │   ├── admin@acme.com                            │    │
│  │  │   └── user@acme.com                             │    │
│  │                                                     │    │
│  │  ├── Items                                          │    │
│  │  │   ├── Item 1 (created by admin@acme.com)       │    │
│  │  │   └── Item 2 (created by user@acme.com)        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │        SCHEMA: "beta" (Tenant 2)                   │    │
│  │                                                     │    │
│  │  ├── Users                                          │    │
│  │  │   ├── admin@beta.com                            │    │
│  │  │   └── jane@beta.com                             │    │
│  │                                                     │    │
│  │  ├── Items                                          │    │
│  │  │   ├── Item 1 (created by admin@beta.com)       │    │
│  │  │   └── Item 2 (created by jane@beta.com)        │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Request Flow Diagram                        │
└─────────────────────────────────────────────────────────────────┘

1. Client Request
   │
   ├─→ http://acme.app.com/api/core/items/
   │   Host: acme.app.com
   │   Authorization: Bearer <JWT>
   │
   ↓
2. TenantMiddleware
   │
   ├─→ Extract domain: "acme.app.com"
   ├─→ Lookup tenant in public schema
   ├─→ Find: Tenant(id=1, schema_name="acme")
   ├─→ Set PostgreSQL search_path to "acme"
   │
   ↓
3. JWT Authentication
   │
   ├─→ Verify JWT token
   ├─→ Extract user from token
   ├─→ Load user from "acme" schema
   │
   ↓
4. View/Serializer
   │
   ├─→ Query items from "acme" schema
   ├─→ Only returns items belonging to Acme Corp
   │
   ↓
5. Response
   │
   └─→ JSON response with tenant-specific data
```

## Application Architecture

### Django Apps Structure

```
apps/
├── tenants/              # Tenant Management (Shared App)
│   ├── models.py        # Tenant, Domain models
│   ├── serializers.py   # Tenant registration serializer
│   ├── views.py         # Public tenant registration endpoint
│   └── admin.py         # Tenant admin interface
│
├── users/               # User Management (Tenant-Specific App)
│   ├── serializers.py   # User CRUD serializers
│   ├── views.py         # User management endpoints
│   └── urls.py          # JWT auth, user CRUD endpoints
│
└── core/                # Business Logic (Tenant-Specific App)
    ├── models.py        # Example: Item model
    ├── serializers.py   # Business object serializers
    ├── views.py         # Business API endpoints
    └── admin.py         # Admin interface for tenant data
```

### Shared vs Tenant Apps

**Shared Apps** (stored in public schema):
- `apps.tenants` - Tenant and Domain models
- Only accessible in public schema
- Used for tenant provisioning and routing

**Tenant Apps** (stored in each tenant's schema):
- `apps.users` - User management
- `apps.core` - Business logic and models
- Replicated in every tenant schema
- Complete data isolation between tenants

## API Architecture

### Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   Authentication Flow                         │
└──────────────────────────────────────────────────────────────┘

1. User Login
   POST /api/users/auth/login/
   {
     "username": "admin@acme.com",
     "password": "password123"
   }
   │
   ↓
2. JWT Token Generation
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  # Valid for 60 min
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..." # Valid for 7 days
   }
   │
   ↓
3. Authenticated Request
   GET /api/core/items/
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   │
   ↓
4. Token Validation
   ├─→ Verify signature
   ├─→ Check expiration
   ├─→ Extract user_id
   ├─→ Load user from current tenant schema
   │
   ↓
5. Return Protected Resource
```

### Tenant Registration Flow

```
┌──────────────────────────────────────────────────────────────┐
│               Tenant Registration Flow                        │
└──────────────────────────────────────────────────────────────┘

1. Public Registration Request
   POST /api/tenants/register/
   {
     "tenant_name": "Acme Corporation",
     "schema_name": "acme",
     "domain": "acme.app.com",
     "admin_email": "admin@acme.com",
     "admin_password": "securepass123"
   }
   │
   ↓
2. Create Tenant Record (Public Schema)
   Tenant(
     name="Acme Corporation",
     schema_name="acme"
   )
   │
   ↓
3. Create PostgreSQL Schema
   CREATE SCHEMA "acme"
   │
   ↓
4. Run Migrations in Tenant Schema
   SET search_path TO "acme"
   - Create users table
   - Create items table
   - Create all tenant app tables
   │
   ↓
5. Create Domain Record (Public Schema)
   Domain(
     domain="acme.app.com",
     tenant=tenant_obj,
     is_primary=True
   )
   │
   ↓
6. Create Admin User (Tenant Schema)
   SET search_path TO "acme"
   User.objects.create_superuser(
     username="admin@acme.com",
     password="securepass123",
     is_staff=True,
     is_superuser=True
   )
   │
   ↓
7. Return Success Response
   {
     "message": "Tenant created successfully",
     "tenant": { ... },
     "domain": "acme.app.com"
   }
```

## Database Schema

### Public Schema Tables

**Tenant Table**
```sql
CREATE TABLE tenants_tenant (
    id SERIAL PRIMARY KEY,
    schema_name VARCHAR(63) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_on TIMESTAMP NOT NULL,
    updated_on TIMESTAMP NOT NULL,
    max_users INTEGER DEFAULT 10
);
```

**Domain Table**
```sql
CREATE TABLE tenants_domain (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(253) UNIQUE NOT NULL,
    tenant_id INTEGER REFERENCES tenants_tenant(id),
    is_primary BOOLEAN DEFAULT TRUE
);
```

### Tenant Schema Tables

**User Table** (in each tenant schema)
```sql
CREATE TABLE auth_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP NOT NULL
);
```

**Item Table** (in each tenant schema)
```sql
CREATE TABLE core_item (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Security Architecture

### Data Isolation

1. **Schema-Level Isolation**: Each tenant's data is in a separate PostgreSQL schema
2. **Automatic Routing**: Middleware ensures users can only access their tenant's schema
3. **No Cross-Tenant Queries**: Impossible to query another tenant's data
4. **User Isolation**: Users exist only in their tenant's schema

### Authentication & Authorization

1. **JWT Tokens**: Stateless authentication
2. **Token Expiration**: Access tokens expire after 60 minutes
3. **Refresh Tokens**: 7-day validity with rotation
4. **Role-Based Access**: Admin vs regular user permissions
5. **Password Validation**: Django's built-in password validators

### Best Practices Implemented

- Environment variables for sensitive configuration
- CORS configuration
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection (DRF serialization)
- Secure password hashing (PBKDF2)

## Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: JWT enables load balancing across multiple Django instances
- **Database Connection Pooling**: Use PgBouncer for connection management
- **Caching**: Add Redis for session/API caching

### Database Performance

- **Schema Limit**: PostgreSQL handles thousands of schemas efficiently
- **Indexing**: Each tenant schema has its own indexes
- **Vacuum**: Regular maintenance per schema
- **Backup**: Schema-level backup and restore

### Monitoring

- **Per-Tenant Metrics**: Track usage per tenant
- **Schema Size**: Monitor schema growth
- **Query Performance**: Identify slow queries per tenant
- **User Activity**: Track active users per tenant

## Technology Decisions

### Why Schema-Based Multi-Tenancy?

**Advantages:**
- Complete data isolation (security & compliance)
- Easy backup/restore per tenant
- Per-tenant customization possible
- Clear separation of concerns

**Trade-offs:**
- More complex migrations
- PostgreSQL-specific
- Schema limit considerations

### Why JWT?

**Advantages:**
- Stateless (no session storage)
- Scalable across multiple servers
- Mobile-friendly
- Standard industry practice

**Trade-offs:**
- Cannot invalidate tokens before expiration
- Slightly larger request size

### Why Django REST Framework?

**Advantages:**
- Industry-standard for Django APIs
- Built-in serialization
- Authentication/permissions framework
- Auto-generated API docs
- Browsable API for development

## Extension Points

### Adding New Tenant Apps

1. Add app to `TENANT_APPS` in settings.py
2. Run `migrate_schemas` to create tables in all tenant schemas
3. Create models, serializers, views as normal

### Custom Tenant Model Fields

Extend the `Tenant` model in `apps/tenants/models.py`:
```python
class Tenant(TenantMixin):
    # Existing fields...
    max_users = models.IntegerField(default=10)

    # Add custom fields:
    subscription_plan = models.CharField(max_length=50)
    stripe_customer_id = models.CharField(max_length=100)
    features_enabled = models.JSONField(default=dict)
```

### Custom User Model

Replace Django's User model with a custom one in `apps/users/models.py` and update settings.

### Background Tasks

Use Celery for:
- Sending welcome emails after tenant registration
- Generating reports per tenant
- Scheduled tasks per tenant

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Production Deployment                       │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                           ↓
                    ┌─────────────┐
                    │  Nginx/LB   │  (SSL/TLS, Load Balancing)
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         ↓                 ↓                 ↓
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │ Django  │      │ Django  │      │ Django  │
    │ (Web 1) │      │ (Web 2) │      │ (Web 3) │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          ↓
                   ┌─────────────┐
                   │ PostgreSQL  │  (with multiple schemas)
                   └─────────────┘
```

## Conclusion

This architecture provides:
- **Complete tenant isolation** through PostgreSQL schemas
- **Scalable API design** with DRF and JWT
- **Easy tenant onboarding** with public registration
- **Production-ready** security and best practices
- **Extensible structure** for adding features

Perfect for SaaS applications requiring strong data isolation and multi-tenant capabilities.
