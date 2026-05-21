# Backend - School PS

This repository contains the backend for the School PS system, a school payment clearance (Paz y Salvo) platform. It provides the services and project structure used to support development, collaboration, and deployment of the application.

---

## Table of Contents

- [Naming Conventions](#naming-conventions)
- [Development Workflow](#development-workflow)
- [Branch Protection Rules](#branch-protection-rules)
- [Team Internal Rules](#team-internal-rules)
- [Conflict Prevention & Resolution](#conflict-prevention-resolution)
- [Quick Reference Guide](#quick-reference-guide)
- [Critical Reminders](#critical-reminders)
- [Getting Started](#getting-started)
- [Notes](#notes)
- [Support](#support)
- [Additional documentation](#additional-documentation)
  - [Create the database](#creating-the-database)

---

## 📋 Naming Conventions

**Establish naming conventions from the start to maintain consistency and organization across the project. ALL team members MUST follow these standards.**

### 🌿 Branch Naming

Use clear, descriptive branch names following this pattern:

```
<type>/<description>
```

**Types:**

- `feature/` - New features
- `fix/` - Bug fixes
- `hotfix/` - Critical fixes for production
- `refactor/` - Code improvements without changing functionality
- `docs/` - Documentation updates
- `test/` - Test additions or improvements

**Examples (School Paz y Salvo Context):**

```
feature/student-balance-tracking
feature/payment-verification-endpoint
feature/certificate-generation
fix/balance-calculation-error
fix/payment-status-update
hotfix/certificate-download-issue
refactor/database-queries-optimization
docs/api-endpoints-documentation
test/payment-processing-unit-tests
```

**✅ DO:**

- Use lowercase letters
- Use hyphens to separate words
- Be descriptive and concise
- Reference issue number when applicable: `feature/PS-123-student-balance`

**❌ DON'T:**

- Use underscores or dots
- Use uppercase letters
- Use vague names like `fix/stuff` or `feature/update`
- Use domain-unrelated examples (this is NOT an ecommerce system)

---

### 🔄 Pull Request Workflow

**⚠️ IMPORTANT FOR DEVELOPERS:**

#### PR Submission Rules:

1. **ALL PRs must be submitted to the `develop` branch ONLY** - Never directly to `main` or `master`
2. **Branches are protected** - Direct commits to main/develop are not allowed
3. **CI/CD Checks Required** - Your PR must pass all automated checks before merging:
   - ✅ Tests must pass
   - ✅ Code linting must pass
   - ✅ Build must succeed
   - ✅ Code coverage requirements must be met (if applicable)
4. **Code Review Required** - At least one team member approval is required
5. **Merge Strategy** - Squash and merge or regular merge (as per team policy)

#### PR Title Format:

```
<type>: <description>
```

**Examples:**

```
feat: add student balance tracking endpoint
feat: implement payment verification logic
fix: correct balance calculation for scholarships
fix: resolve certificate generation issue
refactor: optimize database queries for performance
docs: add API documentation for payment endpoints
test: add unit tests for balance service
```

#### PR Template

The PR template is managed in `.github/pull_request_template.md`. When you create a new PR, the template will be automatically populated with the required sections:

- **Description** - Explain what this PR does and why
- **Type of Change** - Select the appropriate change type
- **Related Issues** - Reference any related issues (e.g., `Fixes #123`)
- **Testing** - Describe how you tested your changes
- **Checklist** - Verify all items before requesting review

---

### 📝 Commit Messages

Follow conventional commit format for clear and organized commit history:

```
<type>(<scope>): <subject>
```

**Types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation changes
- `test:` - Test additions/modifications
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Build, dependencies, or other maintenance tasks

**Examples (School Context):**

```
feat: add payment status endpoint
feat(auth): implement admin authentication
fix: correct student balance calculation
fix(certificates): resolve PDF generation error
refactor: simplify payment service logic
docs: update API documentation
test: add unit tests for balance service
chore: update dependencies to latest versions
```

**✅ DO:**

- Start with lowercase
- Be concise but descriptive
- Use present tense
- Include scope when relevant
- Link to issues: `fix: resolve balance issue #45`

**❌ DON'T:**

- Write long, verbose messages
- Use past tense
- Mix multiple unrelated changes in one commit

---

## 🎯 Development Workflow

### Step-by-Step Process:

1. **Create Feature Branch**

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/student-payment-tracking
   ```

2. **Develop and Commit**

   ```bash
   git add .
   git commit -m "feat: add payment tracking system"
   git commit -m "test: add unit tests for payment service"
   ```

3. **Push to Remote**

   ```bash
   git push origin feature/student-payment-tracking
   ```

4. **Create Pull Request**
   - Go to GitHub/GitLab and create PR to `develop` branch
   - Fill in the PR description template
   - Request review from team members

5. **Address Feedback**
   - Wait for CI/CD checks to pass
   - Fix any linting or test errors
   - Respond to code review comments
   - Add commits to address feedback

6. **Merge to Develop**
   - After approval and all checks pass
   - Delete the feature branch

7. **Release to Production**
   - When ready for release, merge `develop` → `main`
   - Tag with version number

---

## 🛡️ Branch Protection Rules

**All branches are protected with the following rules:**

- ✅ **Direct commits are disabled** - Use branches and PRs only
- ✅ **PRs must be reviewed** - At least 1 approval required
- ✅ **CI/CD checks must pass** - All automated tests and builds must succeed
- ✅ **No force pushes** - Prevents accidental history rewrites
- ✅ **Dismiss stale reviews** - New commits dismiss previous approvals

### Protected Branches:

- `main` - Production branch (release only)
- `develop` - Development branch (PRs only)
- All feature branches are read-only until PR is merged

---

## 👥 Team Internal Rules

**These are human rules that complement GitHub's technical protections. GitHub enforces what it can, but team discipline ensures what it can't.**

### Core Team Agreements:

1. **🚫 No one commits directly to `main`**
   - This is absolute. Even if you think you're a maintainer, use a PR
   - Direct commits to `main` may be rejected or reverted

2. **👥 No self-merges - Peer review is mandatory**
   - You **CANNOT** approve and merge your own PR
   - Your PR must be approved by at least one other team member
   - If your team agrees on mandatory cross-review, then EVERYONE needs approval from someone else
   - This ensures fresh eyes on every change

3. **🎫 Every change must come from an issue or task**
   - Before creating a branch, verify there's a corresponding issue/ticket
   - Reference it in your PR title or description: `fix: resolve #45`
   - This maintains traceability and context for future developers

4. **📦 Every PR should be small and focused**
   - One logical intention per PR
   - Easier to review, test, and revert if needed
   - Target: Keep PRs under 400 lines of code changes

5. **🔪 If a PR exceeds the size limit, split it**
   - Large PRs take longer to review and are harder to understand
   - Split into multiple smaller PRs targeting logical features
   - Example: Instead of "feat: complete payment system", split into:
     - `feat: add payment gateway endpoint`
     - `feat: implement payment validation`
     - `feat: add payment success notification`

6. **⚔️ If there are conflicts, the PR author resolves them**
   - It's the author's responsibility to keep their branch updated
   - Before requesting merge, update your branch with `develop`
   - Fix conflicts yourself before asking for review
   - This prevents bottlenecks and keeps the process flowing

7. **👀 Reviewers must actually validate the code**
   - **Don't approve "blindly"** - this defeats the purpose of code review
   - Reviewers should:
     - ✅ Read and understand the code
     - ✅ Run tests locally (when possible)
     - ✅ Verify the changes work as intended
     - ✅ Check for security issues
     - ✅ Ask questions if anything is unclear
   - Approval is a professional commitment, not a checkbox

---

## 🤝 Conflict Prevention & Resolution

**Conflicts are reduced dramatically with discipline and coordination. Here's how to minimize and handle them:**

### Prevention Strategy:

**1. Keep branches short-lived**

- Features should be completed and merged within 1-3 days
- The longer a branch exists, the more likely conflicts arise
- Quick, frequent merges to `develop` reduce integration problems

**2. Always work from the latest `develop`**

- Before starting a branch: `git pull origin develop`
- Before requesting merge: `git pull origin develop` (again)
- Before merging: Ensure your branch is up-to-date
- GitHub can enforce this rule, but manual discipline helps too

**3. Don't leave branches open for days**

- Abandoned branches cause stale PRs
- If you need to pause, communicate it in the PR
- Other developers shouldn't have to wait for your branch

**4. Coordinate if working on related modules**

- If two team members will work on the same file/module, discuss it first via an issue
- Assign tasks clearly in your issue tracker
- Prevent overlapping work before it happens
- Example:
  - Dev A: "I'm doing payment validation logic"
  - Dev B: "I'll do payment endpoint routing"
  - Agreed: Coordinate via PR before merge

### GitHub's Enforcement:

- ✅ **Require branches to be up-to-date before merge** - GitHub setting enabled
- ✅ **This automatically detects conflicts** before entering `main`
- ✅ **Force push disabled** - Prevents accidental history rewrites

### Handling Conflicts When They Occur:

1. **Author receives a conflict notification**

   ```bash
   # Update your branch
   git fetch origin
   git merge origin/develop

   # Manually resolve conflicts (editor will show them)
   # Then commit the merge
   git add .
   git commit -m "merge: resolve conflicts with develop"
   git push origin feature/your-feature
   ```

2. **Review the conflict carefully**
   - Don't just delete code blindly
   - Understand what changed in `develop` vs your branch
   - Test after resolving to ensure nothing broke

3. **Re-request review**
   - Add a comment: "Conflicts resolved, ready for re-review"
   - Wait for approval again if needed

### ⏰ Ideal Workflow Timeline

| Stage     | Time    | Action                  |
| --------- | ------- | ----------------------- |
| Create PR | Day 1   | Open PR, request review |
| Review    | Day 1-2 | Reviewer tests locally  |
| Feedback  | Day 2   | Address comments        |
| Merge     | Day 2-3 | PR merged to `develop`  |
| Close     | Day 3   | Branch deleted          |

**Total time per PR: 1-3 days maximum**

### 🚨 Conflict Resolution Example

Scenario: You and a teammate both modified a core service file

```bash
# 1. Fetch latest
git fetch origin

# 2. Try to rebase
git rebase origin/develop

# Output:
# CONFLICT (content): Merge conflict in src/services/student.service
# error: could not apply abc123... feat: add payment retry logic

# 3. Edit the file, look for markers:
# <<<<<<<< HEAD
# Your changes here
# ========
# Teammate's changes here
# >>>>>>> origin/develop

# 4. Decide what to keep, remove markers:
# Final version with both changes merged properly

# 5. Mark as resolved and continue
git add src/services/student.service
git rebase --continue

# 6. Push (with lease to be safe)
git push origin feature/student-retry --force-with-lease

# 7. PR is now clean and ready to merge
```

### 📋 Conflict Checklist

Before pushing after resolving conflicts:

- [ ] Conflict markers are completely removed
- [ ] Code compiles/lints without errors
- [ ] Tests pass locally
- [ ] Functionality works as expected
- [ ] Both sets of changes are preserved (if applicable)
- [ ] Teammate notified (if their code was involved)

---

<a id="quick-reference-guide"></a>

## 📊 Quick Reference Guide

| Element   | Pattern                | Example                              |
| --------- | ---------------------- | ------------------------------------ |
| Branch    | `<type>/<description>` | `feature/payment-verification`       |
| Commit    | `<type>: <message>`    | `feat: add balance endpoint`         |
| PR Title  | `<type>: <message>`    | `feat: add student balance tracking` |
| PR Target | Always `develop`       | Never directly to `main`             |

---

<a id="critical-reminders"></a>

## ⚠️ Critical Reminders for All Developers

1. **⛔ NEVER commit directly to main or develop** - Branch protection is enabled
2. **✅ ALL PRs to develop branch ONLY** - PRs to other branches will be rejected
3. **✅ ALL checks must pass** - Failing tests or linting blocks merging
4. **✅ Code review required** - No self-merging, always wait for approval
5. **✅ Use atomic commits** - One logical change per commit
6. **✅ Consistency is mandatory** - No exceptions to naming conventions
7. **❓ Questions?** - Ask the tech lead before pushing

---

## 🚀 Getting Started

### Prerequisites

- Git
- Your preferred development environment setup (tech stack will be defined separately)

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd school-ps/backend
   ```

2. **Configure Git**

   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Create develop branch locally** (if not already present)

   ```bash
   git checkout -b develop origin/develop
   ```

4. **Follow project setup documentation** - Refer to the project's tech-specific setup guide for environment configuration and dependencies

---

## 📝 Notes

- This is a Paz y Salvo (payment clearance) system for schools
- All examples should reflect school/payment context
- Branch protection is in place for safety and quality assurance
- CI/CD pipeline ensures code quality before production
- Technology stack details are documented in separate setup guides

---

## 📞 Support

For questions about this workflow or branch protection rules, reach out to the tech lead or team.

---

**Last Updated:** 2026
**Repository:** School PS Backend
**Team:** Development Team

## 📚 Additional documentation — Backend (migrations, environment variables, queries, Makefile)

This section documents recent and important backend additions: Alembic migrations, recommended environment variables, an example database query (based on the `health` endpoint), and Makefile commands used during development.

---

### 🔁 Migrations (Alembic)

Where:

- Migration directory: `alembic/`
- Config: `alembic.ini`
- Alembic's env uses `SQLModel.metadata` and reads the database URL from application settings (`app/core/config.py`).

Key notes:

- `alembic/env.py` reads the DB URL from `settings.database_url` and imports model modules so `autogenerate` can detect schema changes.
- Check `alembic/versions/` for generated migration files (the folder may be empty until you create revisions).

Basic commands (run from `school-ps/backend`):

1. Install development dependencies (includes Alembic):
   - `make install-dev` (runs `uv sync --group dev`)

2. Create a migration (autogenerate):
   - `uv run alembic revision --autogenerate -m "describe change"`
   - or `alembic revision --autogenerate -m "describe change"` inside your venv

3. Apply migrations:
   - `uv run alembic upgrade head`
   - or `alembic upgrade head`

Best practices:

- Review generated files under `alembic/versions/` before committing.
- Commit migration files together with the PR that changes models.
- If `autogenerate` doesn't detect changes, ensure models are imported by `alembic/env.py`.

References:

```school-ps/backend/alembic/env.py#L1-200
# env.py uses `get_settings()` to read the DB URL and `SQLModel.metadata`.
```

---

### 🔐 Environment variables (important)

The application uses `pydantic-settings` and automatically loads `.env` (or `.env.test` in testing). See `app/core/config.py` for default values.

Important variables:

- `DATABASE_URL`
  - Example: `postgresql://postgres:password@localhost:5432/postgres`
  - Used by the app to create the SQLAlchemy engine (`app.core.db`).

- `ENVIRONMENT`
  - `development` | `testing` | `production`
  - When set to `testing` (or when pytest is running), the app uses `.env.test`.

- `SECRET_KEY` — secret for signing tokens.
- `ALGORITHM` — JWT signing algorithm (e.g. `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES` — token expiry in minutes (e.g. `30`).
- `PORT` — application port (e.g. `8000`).
- `PREFIX_API` — API prefix (default `/api/v1`).

Minimal `.env` example:

```/dev/null/.env.example#L1-20
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres
SECRET_KEY=super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
PREFIX_API=/api/v1
```

If you use `docker-compose` for the DB, the `db` service already defines `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` in `docker-compose.yml`.

Repository reference:

```school-ps/backend/app/core/config.py#L1-200
# Settings and default values (get_env_file, Settings)
```

---

### 🗄️ Creating the database (PostgreSQL)

There are two common ways to create or ensure the database exists for local development: using Docker Compose (recommended) or creating it manually with Postgres client tools. The compose service defines the DB name, user and password and will create the database automatically when started.

Docker Compose (recommended):

```/dev/null/docker_compose_up.sh#L1-4
# Start only the postgres service (recommended for local dev)
docker compose up -d db
# or (legacy)
docker-compose up -d db
```

To start the whole stack:

```/dev/null/docker_compose_up_all.sh#L1
docker compose up -d
```

The `db` service in this repo uses these env vars:

```school-ps/backend/docker-compose.yml#L1-20
services:
  db:
    image: postgres:17-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

Manual creation (if you have Postgres client installed):

```/dev/null/create_db.sh#L1-4
# Using createdb (Postgres client must be installed)
PGPASSWORD=password createdb -h localhost -p 5432 -U postgres postgres

# Or with psql:
PGPASSWORD=password psql -h localhost -U postgres -p 5432 -c "CREATE DATABASE postgres;"
```

After the database is available, run migrations to create tables and schema:

```/dev/null/migrations_cmds.sh#L1-2
uv run alembic upgrade head
```

If you use a different database name, update `DATABASE_URL` in your `.env` accordingly before running migrations.

---

### 🧪 Example: querying the database (health pattern)

The existing `health` endpoint demonstrates the pattern: it receives a DB session via dependency and executes a minimal statement (`select(1)`) to verify connectivity.

Existing example (health ping):

```school-ps/backend/app/modules/health/api/routes.py#L1-40
from fastapi import APIRouter
from sqlmodel import select

from app.core.db import SessionDep

router = APIRouter(
    responses={
        200: {"description": "OK"},
    }
)


@router.get("")
async def health(session: SessionDep):
    session.exec(select(1))
    print("¡Ping exitoso! Conexión a la base de datos establecida.")
    return {"status": "ok"}
```

Pattern for reading rows from a model (example with `TipoInventario`):

```/dev/null/example_query.py#L1-40
from fastapi import APIRouter
from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.models import TipoInventario

router = APIRouter(prefix="/inventory")

@router.get("/types")
def list_inventory_types(session: SessionDep):
    stmt = select(TipoInventario)
    types = session.exec(stmt).all()
    return types
```

Quick curl checks (when app is running):

```/dev/null/examples.sh#L1-4
# Health (DB connectivity check)
curl http://localhost:8000/api/v1/health

# Example query endpoint (if implemented)
curl http://localhost:8000/api/v1/inventory/types
```

References:

```school-ps/backend/app/core/db.py#L1-200
# `engine = create_engine(settings.database_url)` and `SessionDep`.
```

---

### 🧰 Makefile — useful commands

Current `Makefile` (reference):

```school-ps/backend/Makefile#L1-40
.PHONY: run lint format install-dev install-prod

run:
	@uv run fastapi dev app/main.py

lint:
	@uv run zuban check
	@uv run ruff check

format:
	@uv run ruff format

install-dev:
	@uv sync --group dev

install-prod:
	@uv sync --group prod
```

Quick descriptions:

- `make run` — start the app in development (`uv run fastapi dev app/main.py`).
- `make lint` — run linters (`zuban` and `ruff`).
- `make format` — format code with `ruff`.
- `make install-dev` — install development dependencies (includes Alembic).
- `make install-prod` — install production dependencies.

---

### ✅ Quick command summary

- Install dev deps: `make install-dev`
- Start app (dev): `make run`
- Create migration: `uv run alembic revision --autogenerate -m "msg"`
- Apply migrations: `uv run alembic upgrade head`
- Lint / format: `make lint`, `make format`

---
