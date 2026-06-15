# Step 1 — Database Setup

## 1. Overview

This step replaces the stub bodies in `database/db.py` with a working SQLite implementation. It is the foundational step of the project: every feature that follows — user authentication (Step 2–3), profile management (Step 4), and all expense CRUD operations (Steps 7–9) — reads from and writes to the database created here. Nothing else can be built until this step is complete.

---

## 2. Depends on

No prerequisites. This is the first implementation step.

---

## 3. Routes

No new routes are introduced in this step. All existing placeholder routes in `app.py` remain unchanged.

---

## 4. Database Schema

### Table A: `users`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `name` | TEXT | NOT NULL |
| `email` | TEXT | NOT NULL, UNIQUE |
| `password_hash` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` |

### Table B: `expenses`

| Column | SQLite Type | Constraints |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → `users(id)` |
| `amount` | REAL | NOT NULL |
| `category` | TEXT | NOT NULL |
| `date` | TEXT | NOT NULL — must be stored as `YYYY-MM-DD` |
| `description` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` |

---

## 5. Functions to Implement (`database/db.py`)

### `get_db()`
- Opens (or creates) `spendly.db` in the project root directory
- Sets `connection.row_factory = sqlite3.Row` so columns are accessible by name
- Executes `PRAGMA foreign_keys = ON` on every new connection
- Returns the open connection

### `init_db()`
- Creates both `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS`
- Safe to call multiple times — must not fail or duplicate tables on repeated calls
- Does not insert any data

### `seed_db()`
- Checks whether the `users` table already contains any rows
- If rows exist: returns immediately (idempotent guard)
- If empty: inserts one demo user:
  - `name`: `Demo User`
  - `email`: `demo@spendly.com`
  - `password_hash`: `demo123` hashed via `werkzeug.security.generate_password_hash`
- Inserts 8 sample expenses linked to the demo user's `id`
- Sample expenses must cover all 7 categories (see Section 9)
- Dates must be spread across the current calendar month in `YYYY-MM-DD` format

---

## 6. Changes to `app.py`

- Import `get_db`, `init_db`, and `seed_db` from `database.db`
- After creating the Flask `app` instance, call `init_db()` and then `seed_db()` inside an `app.app_context()` block so the database is fully initialized before any route is served

---

## 7. Files to Change

- `database/db.py`
- `app.py`

---

## 8. Files to Create

None.

---

## 9. Dependencies

No new pip packages. Use only:
- `sqlite3` — Python standard library
- `werkzeug.security` — already listed in `requirements.txt`

---

## 10. Categories (Fixed List)

The following are the only valid expense category values:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

---

## 11. Rules for Implementation

- No ORM, no SQLAlchemy — use the `sqlite3` standard library only
- All SQL statements must use parameterized queries (`?` placeholders) — never use f-strings or `%` formatting inside SQL
- `PRAGMA foreign_keys = ON` must be executed on every new connection inside `get_db()`
- `amount` must be stored as `REAL`, not `INTEGER`
- Passwords must be hashed with `generate_password_hash` from `werkzeug.security` — never store plain-text passwords
- `seed_db()` must be idempotent — calling it multiple times must produce no duplicate rows
- All date values must be stored and compared as `YYYY-MM-DD` strings

---

## 12. Expected Behavior

| Function | Expected behavior when called correctly |
|---|---|
| `get_db()` | Returns an open `sqlite3.Connection` with `row_factory` set and foreign keys enabled |
| `init_db()` | Creates `users` and `expenses` tables; second call is a no-op |
| `seed_db()` | On first call: inserts 1 user and 8 expenses; on subsequent calls: returns immediately without inserting |

Database-level constraints must enforce:
- `users.email` uniqueness at the DB layer
- `expenses.user_id` referential integrity via the foreign key to `users(id)`
- `NOT NULL` on all required columns

---

## 13. Error Handling Expectations

| Scenario | Expected outcome |
|---|---|
| Insert a duplicate `email` into `users` | SQLite raises `UNIQUE constraint failed: users.email` |
| Insert an `expense` with a non-existent `user_id` | SQLite raises `FOREIGN KEY constraint failed` |
| Malformed or missing required fields | Exception propagates clearly — do not silently swallow errors; let them surface for debugging |

---

## 14. Definition of Done

- [ ] Database file (`spendly.db`) is created automatically on app startup
- [ ] Both `users` and `expenses` tables exist with the correct columns, types, and constraints
- [ ] Demo user (`demo@spendly.com`) exists with a hashed (not plain-text) password
- [ ] Exactly 8 sample expenses exist, covering all 7 categories
- [ ] Running `python app.py` a second time does not duplicate seed data
- [ ] App starts without errors
- [ ] Inserting an expense with an invalid `user_id` is rejected by the foreign key constraint
- [ ] All SQL queries use parameterized `?` placeholders — no string-formatted SQL anywhere
