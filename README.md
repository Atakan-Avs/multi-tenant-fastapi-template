# 🏗 TaskEngine – Multi-Tenant FastAPI Backend

A production-oriented FastAPI backend demonstrating multi-tenant architecture, secure authentication, session management, and permission-based RBAC.

This project focuses on real-world backend engineering patterns rather than simple CRUD APIs.

---

# 📌 Overview

TaskEngine is designed as a backend foundation for SaaS-style or enterprise applications.

Key concepts implemented:

- Multi-tenant architecture
- JWT authentication with refresh token rotation
- Session management with reuse detection
- Permission-based RBAC system
- Database-level consistency enforcement
- Centralized error handling
- Layered backend architecture

---

# 🧠 Architecture Highlights

## 🔐 Authentication & Session Management

Features:

- JWT access tokens
- Argon2 password hashing
- Refresh token rotation
- Refresh token reuse detection
- Session revocation (logout / logout-all)
- Hash-based refresh token storage

Security design:

Access tokens are short-lived and stateless.  
Refresh tokens are stored as **hashed values** in the database to prevent token leakage.

If a revoked refresh token is reused, **all sessions for the user are revoked** to mitigate potential token theft.

---

## 🏢 Multi-Tenant Architecture

Tenant isolation is enforced using organization scoping.

Each user belongs to an organization.

All queries are automatically scoped by:


org_id
This guarantees:

- No cross-tenant data access
- Safe multi-tenant SaaS backend design

---

## 🛡 Permission-Based RBAC

The system implements a **role → permission → user** hierarchy.

Database tables:
roles
permissions
user_roles
role_permissions



Permissions control access to API endpoints.

Example permissions:
task.create
task.read
task.update
task.delete
rbac.manage


Authorization is enforced through FastAPI dependency guards:
require_permission("task.delete")



This allows flexible authorization without hardcoding roles in business logic.

---

## 🗄 Database Design

Stack:

- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations

Important constraint:
UniqueConstraint("org_id", "email")



This ensures safe concurrent user creation within tenants.

Even under race conditions the database guarantees consistency.

---

## 📊 Task System

The system includes a task workflow module.

Features:

- Create tasks
- Update tasks
- List tasks
- Soft delete tasks
- Restore tasks

Task lifecycle events are stored in:
task_events

Example events:

task_created
task_deleted
task_restored
task_updated



This enables audit history and future analytics.

---

## ⚙ Request Middleware & Observability

Each request includes contextual metadata:

- request_id
- user_id
- org_id
- client_ip
- user_agent

Structured logs allow easier debugging and production monitoring.

---

# 🏛 Project Structure
app/
├── api/ # Route definitions
├── core/ # Security, middleware, configuration
├── db/ # Database session
├── models/ # SQLAlchemy models
├── repositories/ # Data access layer
├── services/ # Business logic layer
├── schemas/ # Pydantic schemas
└── main.py # FastAPI entrypoint



Architecture layers:
API Layer
Service Layer
Repository Layer
Database Layer



---

# 🎯 Engineering Goals

This project demonstrates:

- Secure authentication patterns
- Multi-tenant backend architecture
- Permission-based RBAC
- Session security (refresh rotation & reuse detection)
- Database-first consistency
- Layered backend architecture
- Structured request logging

---

# 🔮 Future Improvements

Possible extensions:

- Redis caching layer
- Background jobs (Celery / RQ)
- Rate limiting
- Notification system
- Webhooks / event streaming
- Permission caching

---

# 🧑‍💻 Author

**Atakan Avsever**

Backend-focused developer building production-oriented systems.
