# Railway Reservation System

A complete full-stack railway reservation platform for B.Tech/CSE portfolio and academic use.

## Stack

- React + Vite frontend with React Router, Axios, dashboard UI, Recharts, and responsive CSS.
- Django + Django REST Framework backend for authentication, admin CRUD, bookings, payments, cancellations, and reports.
- FastAPI service for high-performance train search, schedule, availability, fare calculation, PNR lookup, and analytics.
- PostgreSQL as the shared relational database.
- Docker Compose for local development.

## Quick Start

1. Copy environment values:

   ```bash
   cp .env.example .env
   ```

2. Start the stack:

   ```bash
   docker compose up --build
   ```

3. Seed demo data:

   ```bash
   docker compose exec django python manage.py makemigrations
   docker compose exec django python manage.py migrate
   docker compose exec django python manage.py seed_demo
   ```

4. Open the apps:

   - Frontend: http://localhost:5173
   - Django API: http://localhost:8000/api/
   - FastAPI Swagger: http://localhost:8001/docs
   - Django admin: http://localhost:8000/admin/

## Demo Accounts

The seed command creates demo accounts using environment variables so credentials are not hard-coded in source:

- Admin email: `ADMIN_EMAIL` from `.env`
- Admin password: `ADMIN_PASSWORD` from `.env`
- Passenger email: `PASSENGER_EMAIL` from `.env`
- Passenger password: `PASSENGER_PASSWORD` from `.env`

## Core Workflows

- Passenger registration and JWT login.
- Train search by source, destination, date, class, passengers, filters, and sorting.
- Train details, route, coach-level seat map, availability, fare calculation.
- Multi-passenger booking with transaction-protected seat allocation.
- Simulated payment generation, transaction id, booking confirmation, PNR lookup.
- E-ticket view with printable/downloadable browser output.
- Cancellation, seat release, configurable refund calculation, refund status.
- Admin dashboards and CRUD management APIs for users, trains, stations, routes, coaches, seats, fares, bookings, cancellations, refunds, and reports.

## Local Development Without Docker

Backend:

```bash
cd django_backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

FastAPI:

```bash
cd fastapi_backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

- Django REST endpoints are available under `/api/`.
- FastAPI OpenAPI docs are available at `/docs`.
- JWT auth uses `Authorization: Bearer <access_token>`.

## Notes

This project intentionally uses a simulated payment gateway only. It never processes real card, UPI, or banking payments.
