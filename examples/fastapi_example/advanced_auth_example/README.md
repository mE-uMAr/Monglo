# Advanced Example with JWT Authentication

Complete example demonstrating Monglo Admin with JWT authentication using FastAPI HTTPBearer.

## Features

- ✅ JWT (JSON Web Token) authentication
- ✅ HTTPBearer scheme
- ✅ Custom ModelAdmin configurations
- ✅ Database seeding
- ✅ Protected admin panel
- ✅ REST API endpoints

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn motor pymongo pyjwt passlib[bcrypt]
```

### 2. Run the Application

```bash
uvicorn app:app --reload
```

### 3. Access the Admin Panel

1. **Get JWT Token:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

2. **Access Admin Panel:**
   - Visit: http://localhost:8000/admin/login
   - Use credentials: `admin` / `admin123`
   - Token will be stored in browser

3. **API Documentation:**
   - http://localhost:8000/docs

## Authentication Flow

### Login

```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

Response:
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Access Protected Routes

```bash
GET /admin
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## File Structure

```
advanced_with_auth_example/
├── app.py              # Main application with JWT routes
├── auth.py             # JWT authentication helpers
├── db.py               # Database seeding
├── admin_setup.py      # Custom ModelAdmin configs
└── README.md           # This file
```

## Security Notes

⚠️ **For Production:**

1. **Change Secret Key:**
   ```python
   SECRET_KEY = os.getenv("SECRET_KEY")
   ```

2. **Use Environment Variables:**
   ```python
   ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
   ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
   ```

3. **Store Users in Database:**
   - Replace hardcoded credentials with DB lookup
   - Hash passwords with bcrypt

4. **Add Rate Limiting:**
   - Prevent brute force attacks
   - Use libraries like `slowapi`

5. **HTTPS Only:**
   - Never use JWT over HTTP in production

## Collections

- **Users** - Customer and admin users
- **Products** - Product catalog
- **Orders** - Customer orders with items
- **Categories** - Product categories

## Default Credentials

- Username: `admin`
- Password: `admin123`

**Change these immediately in production!**
