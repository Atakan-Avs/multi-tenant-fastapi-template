📦 multi-tenant-fastapi-template

A production-oriented FastAPI backend template demonstrating multi-tenant architecture, centralized error handling, and database-level consistency patterns.

🚀 Overview

This project showcases a real-world backend structure built with:

JWT-based authentication

Argon2 password hashing

Multi-tenant isolation (organization-based)

PostgreSQL (Dockerized)

Alembic migrations

Composite unique constraints (org_id + email)

Centralized exception handling

Clean dependency-based authorization design

The goal of this project is to demonstrate backend engineering practices beyond simple CRUD APIs.

🧠 Architecture Highlights
🔐 Authentication

JWT access tokens

Password hashing with Argon2

Dependency-based current user injection

🏢 Multi-Tenancy

Organization-based tenant isolation

org_id derived from authenticated user

No cross-tenant data access

🛡 Database-Level Safety

Composite unique constraint on (org_id, email)

Race-condition safe user creation

IntegrityError mapped to HTTP 409 (Conflict)

⚙ Centralized Error Handling

Global SQLAlchemy IntegrityError handler

Standardized API error response structure:

{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "Duplicate value violates unique constraint"
  }
}


This ensures predictable API contracts and production-grade error responses.

🧩 Tech Stack

FastAPI

SQLAlchemy

PostgreSQL

Alembic

Docker

Argon2

JWT (python-jose)

📂 Project Structure
app/
 ├── api/
 ├── core/
 ├── db/
 ├── models/
 ├── repositories/
 ├── schemas/
 └── main.py


The project follows a layered architecture:

API layer

Repository layer

Database layer

Centralized configuration & error handling

🗄 Database

PostgreSQL is containerized using Docker.

Example composite constraint:

UniqueConstraint("org_id", "email", name="uq_users_org_id_email")


Migrations are handled via Alembic.

🎯 Why This Project

This template demonstrates:

Clean dependency injection

Multi-tenant design principles

Database-driven consistency enforcement

Production-ready error handling

Clear separation of concerns

It is designed as a foundation for SaaS-style backends or enterprise APIs.

🔮 Planned Improvements

Role-Based Access Control (RBAC)

Refresh token rotation

Audit fields (created_at / updated_at)

Soft delete support

Request ID & structured logging

Background jobs / outbox pattern
