# Testing Guide

This guide explains how to test the multi-tenancy features of this Django boilerplate.

## Setup for Testing

1. Start the application:
```bash
docker-compose up --build
```

2. Wait for the application to be ready. You should see:
```
Superuser created: admin / admin123
Starting Django development server...
```

## Testing Multi-Tenancy

### Step 1: Register First Tenant (Acme Corp)

```bash
curl -X POST http://localhost:8000/api/tenants/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Acme Corporation",
    "schema_name": "acme",
    "domain": "acme.localhost",
    "admin_email": "admin@acme.com",
    "admin_password": "acme123",
    "admin_first_name": "John",
    "admin_last_name": "Doe"
  }'
```

Expected response:
```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": 1,
    "name": "Acme Corporation",
    "schema_name": "acme",
    ...
  },
  "domain": "acme.localhost"
}
```

### Step 2: Register Second Tenant (Beta Inc)

```bash
curl -X POST http://localhost:8000/api/tenants/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Beta Inc",
    "schema_name": "beta",
    "domain": "beta.localhost",
    "admin_email": "admin@beta.com",
    "admin_password": "beta123",
    "admin_first_name": "Jane",
    "admin_last_name": "Smith"
  }'
```

### Step 3: Login to Acme Corp

```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -d '{
    "username": "admin@acme.com",
    "password": "acme123"
  }'
```

Save the `access` token from the response.

### Step 4: Create an Item in Acme Corp

```bash
curl -X POST http://localhost:8000/api/core/items/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer YOUR_ACME_ACCESS_TOKEN" \
  -d '{
    "name": "Acme Item 1",
    "description": "This belongs to Acme Corp"
  }'
```

### Step 5: Login to Beta Inc

```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Host: beta.localhost" \
  -d '{
    "username": "admin@beta.com",
    "password": "beta123"
  }'
```

Save the `access` token from the response.

### Step 6: Create an Item in Beta Inc

```bash
curl -X POST http://localhost:8000/api/core/items/ \
  -H "Content-Type: application/json" \
  -H "Host: beta.localhost" \
  -H "Authorization: Bearer YOUR_BETA_ACCESS_TOKEN" \
  -d '{
    "name": "Beta Item 1",
    "description": "This belongs to Beta Inc"
  }'
```

### Step 7: Verify Tenant Isolation

List items from Acme Corp:
```bash
curl -X GET http://localhost:8000/api/core/items/ \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer YOUR_ACME_ACCESS_TOKEN"
```

Should return only "Acme Item 1".

List items from Beta Inc:
```bash
curl -X GET http://localhost:8000/api/core/items/ \
  -H "Host: beta.localhost" \
  -H "Authorization: Bearer YOUR_BETA_ACCESS_TOKEN"
```

Should return only "Beta Item 1".

**This proves complete data isolation between tenants!**

## Testing with Postman

1. Import the `postman_collection.json` file into Postman

2. Update the collection variables:
   - `base_url`: `http://localhost:8000`
   - `tenant_domain`: `acme.localhost:8000`

3. Run the requests in order:
   - Public Endpoints → Register New Tenant
   - Authentication → Login (automatically saves tokens)
   - Items → Create New Item
   - Items → List All Items

4. To test another tenant:
   - Update `tenant_domain` to `beta.localhost:8000`
   - Repeat the authentication and item creation steps

## Testing User Management

### Create Additional User in Acme Corp

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer YOUR_ACME_ADMIN_TOKEN" \
  -d '{
    "username": "user@acme.com",
    "email": "user@acme.com",
    "password": "password123",
    "first_name": "Regular",
    "last_name": "User"
  }'
```

### Login as Regular User

```bash
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -d '{
    "username": "user@acme.com",
    "password": "password123"
  }'
```

### Try to List All Users (Should Fail)

Regular users cannot access the user list endpoint:
```bash
curl -X GET http://localhost:8000/api/users/ \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN"
```

Expected: 403 Forbidden (only admins can list users)

## Database Verification

### Check PostgreSQL Schemas

```bash
docker-compose exec db psql -U postgres -d django_tenants -c "\dn"
```

You should see:
- `public` (shared schema)
- `acme` (Acme Corp schema)
- `beta` (Beta Inc schema)

### Check Users in Public Schema

```bash
docker-compose exec db psql -U postgres -d django_tenants -c "
  SELECT * FROM public.tenants_tenant;
"
```

### Check Users in Acme Schema

```bash
docker-compose exec db psql -U postgres -d django_tenants -c "
  SET search_path TO acme;
  SELECT id, username, email, is_staff FROM auth_user;
"
```

### Check Users in Beta Schema

```bash
docker-compose exec db psql -U postgres -d django_tenants -c "
  SET search_path TO beta;
  SELECT id, username, email, is_staff FROM auth_user;
"
```

Notice that each schema has completely separate user tables!

## Admin Panel Testing

### Access Public Admin

1. Go to http://localhost:8000/admin/
2. Login with: `admin` / `admin123`
3. You'll see the Tenant and Domain models (shared data)

### Access Tenant-Specific Admin

1. Update your `/etc/hosts` file:
```
127.0.0.1 acme.localhost
127.0.0.1 beta.localhost
```

2. Go to http://acme.localhost:8000/admin/
3. Login with: `admin@acme.com` / `acme123`
4. You'll see Users, Items (only Acme's data)

5. Go to http://beta.localhost:8000/admin/
6. Login with: `admin@beta.com` / `beta123`
7. You'll see Users, Items (only Beta's data)

## Common Testing Scenarios

### Test 1: Cross-Tenant Data Access Prevention

Try to access Beta's data using Acme's token:
```bash
curl -X GET http://localhost:8000/api/core/items/ \
  -H "Host: beta.localhost" \
  -H "Authorization: Bearer ACME_ACCESS_TOKEN"
```

Expected: 401 Unauthorized (token is not valid for Beta's schema)

### Test 2: Token Refresh

After 60 minutes, the access token expires. Use refresh token:
```bash
curl -X POST http://localhost:8000/api/users/auth/refresh/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Test 3: Password Change

```bash
curl -X POST http://localhost:8000/api/users/me/change-password/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password": "acme123",
    "new_password": "newacme456"
  }'
```

### Test 4: User Profile Update

```bash
curl -X PATCH http://localhost:8000/api/users/me/ \
  -H "Content-Type: application/json" \
  -H "Host: acme.localhost" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Updated"
  }'
```

## Swagger/OpenAPI Testing

1. Go to http://localhost:8000/api/docs/
2. You'll see interactive API documentation
3. Click "Authorize" and enter your JWT token: `Bearer YOUR_ACCESS_TOKEN`
4. Test endpoints directly from the browser

Note: Remember to set the correct Host header when testing tenant-specific endpoints.

## Automated Testing

You can write automated tests using Django's test framework:

```python
# apps/core/tests.py
from django.test import TestCase
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from apps.tenants.models import Tenant, Domain

class ItemTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        # Tenant is created automatically by TenantTestCase

    def test_item_creation(self):
        # Your test code here
        pass
```

Run tests:
```bash
docker-compose exec web python manage.py test
```

## Troubleshooting

### Can't connect to tenant domain

Make sure you're using the correct Host header or have updated `/etc/hosts`.

### 401 Unauthorized

- Check if token is expired (60 min for access tokens)
- Make sure you're using the correct tenant domain
- Verify the token format: `Bearer <token>`

### Database connection errors

Restart the containers:
```bash
docker-compose down
docker-compose up --build
```

### Tenant not found

Make sure the domain exactly matches what you registered.

## Conclusion

This testing guide demonstrates:
- Complete data isolation between tenants
- JWT authentication working correctly
- Role-based access control (admin vs regular users)
- Multi-schema architecture in PostgreSQL

These tests prove the boilerplate implements true multi-tenancy with schema-based isolation!
