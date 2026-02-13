🏗 multi-tenant-fastapi-template

  A production-oriented FastAPI backend template demonstrating multi-tenant architecture, database-level consistency, and centralized error handling patterns.

📌 Overview

  This project is designed as a backend foundation for SaaS-style or enterprise applications.

  It focuses on:

  Secure authentication

  Tenant isolation

  Database integrity enforcement

  Clean architecture principles

  Production-ready error handling

  Rather than being a simple CRUD API, this project demonstrates real-world backend design decisions.

🧠 Architecture Highlights
🔐 Authentication

  JWT-based access tokens

  Argon2 password hashing

  Dependency-based get_current_user

  Stateless API design

🏢 Multi-Tenancy

  Organization-based isolation

  org_id derived from authenticated user

  No cross-tenant data access

  All user queries scoped by tenant

🛡 Database-Level Safety

  PostgreSQL (Dockerized)

  Alembic migration management

  Composite unique constraint:

  UniqueConstraint("org_id", "email", name="uq_users_org_id_email")


  This ensures race-condition-safe user creation.
  
  Even if two concurrent requests attempt to create the same email within the same organization,
the database guarantees consistency.

⚙ Centralized Error Handling

  Global SQLAlchemy IntegrityError handler

  Database constraint violations mapped to HTTP 409

  Standardized API error response format

  Example response:

{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "Duplicate value violates unique constraint"
  }
}


This approach ensures predictable API contracts and avoids leaking raw database errors.

🏛 Project Structure
app/
 ├── api/              # Route definitions
 ├── core/             # Security, config, error handling
 ├── db/               # Database session management
 ├── models/           # SQLAlchemy models
 ├── repositories/     # Data access layer
 ├── schemas/          # Pydantic schemas
 └── main.py           # FastAPI app entry point


The project follows a layered architecture:

  API Layer

  Service/Repository Layer

  Database Layer

  Centralized configuration & error handling

🗄 Database

  PostgreSQL 16 (Docker)

  SQLAlchemy ORM

  Alembic for version-controlled migrations

  Run migrations:

  alembic upgrade head

🚀 Quick Start
1️⃣ Install dependencies
  pip install -r requirements.txt

2️⃣ Start PostgreSQL (Docker)
  docker compose up -d


  (or run your existing PostgreSQL container)

3️⃣ Run migrations
  alembic upgrade head

4️⃣ Start the API
  python -m uvicorn app.main:app --reload

🧪 Example Flow

  Register / login

  Receive JWT token

  Use token to access tenant-scoped endpoints

  Attempt duplicate email creation within same org → HTTP 409

🎯 Engineering Goals

  This template demonstrates:

  Dependency injection patterns

  Multi-tenant isolation

  Database-first consistency enforcement

  Clean separation of concerns

  Production-grade error mapping

  Docker-based local development

🔮 Planned Improvements

  Role-Based Access Control (RBAC)

  Refresh token rotation

  Audit fields (created_at, updated_at)

  Soft delete support

  Request ID & structured logging

  Background jobs / outbox pattern

🧑‍💻 Author

  Atakan Avsever
  Backend-focused developer building production-oriented systems.

Request ID & structured logging

Background jobs / outbox pattern
