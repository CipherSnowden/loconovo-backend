# Quick Start Guide - Running Locally

## Steps to Run the Server

### 1. Install Dependencies

```bash
# Make sure you're in the project directory
cd /Users/cipher/projects/loconovo-backend

# Activate your virtual environment (if not already activated)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment File

```bash
# Copy the example file
cp .env.example .env.prod

# Edit .env.prod with your Cloud SQL connection details
# You'll need to update:
# - DATABASE_URL (connection string)
# - JWT_SECRET_KEY (generate a random string)
# - JWT_REFRESH_SECRET_KEY (generate a random string)
```

### 3. Connect to Cloud SQL (Choose One Method)

#### Option A: Cloud SQL Proxy (Recommended)

```bash
# Start Cloud SQL Proxy in a separate terminal
# Replace <INSTANCE_CONNECTION_NAME> with your actual connection name
./cloud-sql-proxy <INSTANCE_CONNECTION_NAME>

# Example:
# ./cloud-sql-proxy myproject:us-central1:loconovo-postgres
```

Your `.env.prod` should have:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/loconovo_db
```

#### Option B: Direct Connection (If Public IP Enabled)

Your `.env.prod` should have:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_password@<PUBLIC_IP>:5432/loconovo_db
```

### 4. Generate JWT Secrets

```bash
# Generate random secrets for JWT
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_REFRESH_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Add these to your `.env.prod` file.

### 5. Run the Server

```bash
# Make sure you're in the project directory and venv is activated
cd /Users/cipher/projects/loconovo-backend
source venv/bin/activate

# Run with auto-reload (development mode)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Test the API

### 1. Send OTP

```bash
curl -X POST "http://localhost:8000/v1/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1234567890"}'
```

The OTP will be printed in the server console (development mode).

### 2. Verify OTP and Get Tokens

```bash
curl -X POST "http://localhost:8000/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1234567890", "otp_code": "1234"}'
```

Replace `1234` with the actual OTP from the console.

### 3. Get Current User Info

```bash
curl -X GET "http://localhost:8000/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### Database Connection Issues

- Make sure Cloud SQL Proxy is running (if using Option A)
- Verify your DATABASE_URL in `.env.prod` is correct
- Check that the database exists: `loconovo_db`
- Ensure your Cloud SQL instance is running

### Import Errors

- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

If port 8000 is busy, use a different port:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

