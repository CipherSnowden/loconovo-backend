# Loconovo Backend API

FastAPI-based monolith backend for Loconovo mobile application with JWT-based OTP authentication.

## Features

- Mobile number + OTP authentication
- JWT access and refresh tokens
- PostgreSQL database (GCP Cloud SQL)
- RESTful API endpoints
- Async/await architecture
- CORS support for Flutter app

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Async ORM
- **PostgreSQL** - Database (GCP Cloud SQL)
- **python-jose** - JWT token handling
- **Pydantic** - Data validation

## Project Structure

```
loconovo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── api/v1/                 # API routes
│   ├── core/                   # Core logic (security, OTP)
│   └── dependencies.py         # Common dependencies
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- GCP Cloud SQL PostgreSQL instance (`loconovo-postgres`)
- For local development: Cloud SQL Proxy

### 1. Clone and Setup

```bash
# Navigate to project directory
cd loconovo-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. GCP Cloud SQL Setup

#### Option A: Local Development with Cloud SQL Proxy (Recommended)

1. **Install Cloud SQL Proxy**:
   ```bash
   # macOS
   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
   chmod +x cloud-sql-proxy
   
   # Or use Homebrew
   brew install cloud-sql-proxy
   ```

2. **Get your instance connection name** from GCP Console:
   - Format: `PROJECT_ID:REGION:INSTANCE_NAME`

3. **Start Cloud SQL Proxy**:
   ```bash
   ./cloud-sql-proxy <INSTANCE_CONNECTION_NAME>
   # Example: ./cloud-sql-proxy myproject:us-central1:loconovo-postgres
   ```
   The proxy will forward connections to `127.0.0.1:5432`

4. **Configure `.env.prod` file**:
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod and set:
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/loconovo_db
   ```
   
   **Note**: The application loads `.env.prod` by default. For development, you can create `.env.dev` and set `ENV_FILE=.env.dev` environment variable, or use `.env.prod` for both.

#### Option B: Production (GCP Compute Engine)

1. Ensure Compute Engine instance and Cloud SQL are in the same VPC network
2. Get the **private IP** of your Cloud SQL instance from GCP Console
3. Configure `.env.prod` file:
   ```bash
   cp .env.example .env.prod
   # Edit .env.prod and set:
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@<PRIVATE_IP>:5432/loconovo_db
   ```

### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env.prod

# Edit .env.prod with your settings:
# - DATABASE_URL (from Cloud SQL setup above)
# - JWT_SECRET_KEY (generate strong random strings)
# - JWT_REFRESH_SECRET_KEY (generate strong random strings)
# - CORS_ORIGINS (add your Flutter app origins)
```

**Note**: The application uses `.env.prod` by default. To use a different file (e.g., `.env.dev`), set the `ENV_FILE` environment variable:
```bash
export ENV_FILE=.env.dev
```

**Generate secure JWT secrets**:
```bash
# On macOS/Linux
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run the Application

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### 5. Database Tables

Tables are automatically created on first application startup via SQLAlchemy models. No migrations needed.

## API Endpoints

### Authentication

- `POST /v1/auth/send-otp` - Send OTP to phone number
- `POST /v1/auth/verify-otp` - Verify OTP and get JWT tokens
- `POST /v1/auth/refresh` - Refresh access token
- `POST /v1/auth/logout` - Logout
- `GET /v1/auth/me` - Get current user info

### User

- `GET /v1/user/profile` - Get user profile

### Health

- `GET /health` - Health check endpoint

## API Usage Examples

### 1. Send OTP

```bash
curl -X POST "http://localhost:8000/v1/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1234567890"}'
```

### 2. Verify OTP

```bash
curl -X POST "http://localhost:8000/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1234567890", "otp_code": "1234"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 3. Use Access Token

```bash
curl -X GET "http://localhost:8000/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Token

```bash
curl -X POST "http://localhost:8000/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## Development Notes

- **OTP Storage**: Currently in-memory (lost on restart). For production, use Redis.
- **SMS Integration**: OTP is logged to console in dev mode. Integrate SMS provider (Twilio, AWS SNS, etc.) for production.
- **Database**: Tables are auto-created. Schema changes require manual updates.

## Deployment to GCP Compute Engine

1. **Create Compute Engine instance**:
   - Choose appropriate machine type
   - Ensure it's in the same VPC as Cloud SQL
   - Enable private IP connection to Cloud SQL

2. **Setup on instance**:
   ```bash
   # Clone repository
   git clone <your-repo>
   cd loconovo-backend
   
   # Install Python and dependencies
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env.prod
   # Edit .env.prod with production values
   
   # Run with systemd or process manager
   ```

3. **Configure environment variables** on the instance (`.env.prod` file or systemd service)

4. **Run with process manager** (systemd, supervisor, etc.)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `JWT_SECRET_KEY` | Secret for access tokens | - |
| `JWT_REFRESH_SECRET_KEY` | Secret for refresh tokens | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 |
| `OTP_LENGTH` | OTP code length | 4 |
| `OTP_EXPIRE_MINUTES` | OTP expiry time | 5 |
| `OTP_RATE_LIMIT_REQUESTS` | Max OTP requests per hour | 5 |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | - |

## Security Notes

- Never commit `.env.prod` or `.env.dev` files to version control
- Use strong, random JWT secrets in production
- Enable private IP connection between Compute Engine and Cloud SQL
- Configure firewall rules appropriately
- Use HTTPS in production
- Implement rate limiting at infrastructure level for production

## License

[Your License Here]

