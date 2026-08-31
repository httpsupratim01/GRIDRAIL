# GRIDRAIL Publishing Guide

GRIDRAIL is a full-stack app. To publish it properly, deploy all four parts:

- React frontend
- Django backend
- FastAPI search backend
- PostgreSQL database

## Best Simple Option

Use a VPS or Docker host where Docker Compose is available.

## 1. Prepare `.env`

Copy `.env.example` to `.env` on the server and update these values:

```bash
POSTGRES_PASSWORD=your-strong-database-password
SECRET_KEY=your-long-random-django-secret
JWT_SECRET=your-long-random-jwt-secret
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
VITE_DJANGO_API_URL=https://your-domain.com:8000/api
VITE_FASTAPI_URL=https://your-domain.com:8001/api
RAZORPAY_KEY_ID=your-live-razorpay-key
RAZORPAY_KEY_SECRET=your-live-razorpay-secret
```

For local testing, keep localhost values.

## 2. Start Production Stack

Run this from the project root:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## 3. Seed Initial Data

Run this once after the containers start:

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py seed_demo
```

This creates stations, trains, fares, and the first admin/passenger accounts. It will not reset changed passwords or uploaded profile photos.

## 4. Open The Site

Frontend:

```text
http://your-domain.com
```

Django API:

```text
http://your-domain.com:8000/api
```

FastAPI search API:

```text
http://your-domain.com:8001/api
```

## 5. Push Changes To GitHub

After changing code locally:

```bash
/usr/bin/git add .
/usr/bin/git commit -m "Update GRIDRAIL"
/usr/bin/git push origin main
```

GitHub changes do not update the live website automatically unless the host is connected to your GitHub repo for auto-deploy.

## Important

Real payments need live Razorpay keys and your published domain must be allowed inside the Razorpay dashboard.
