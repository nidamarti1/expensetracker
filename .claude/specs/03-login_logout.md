# Step 3 — Login and Logout

## Overview

This step converts the `/login` stub into a functional POST handler that verifies submitted credentials against the `users` table, stores the authenticated user's `id` in `session["user_id"]`, and redirects to the landing page (until a dashboard route exists). It also implements `/logout`, which clears the session and redirects to `/`. After this step the app can distinguish logged-in users from guests — the presence of `session["user_id"]` becomes the single source of truth for auth state throughout the app. This is a prerequisite for all expense features.

---

## Depends on

- Step 01 — Database Setup (`users` table must exist with `email` and `password_hash` columns)
- Step 02 — Registration (`create_user()` and password hashing must be in place; at minimum the seeded demo user must exist to log in against)

---

## Routes

- **`GET /login`**
  - Renders the login form
  - Public — no login required
  - Already exists as a stub; this step upgrades it in place

- **`POST /login`**
  - Reads `email` and `password` from the submitted form
  - Looks up the user by email via `get_user_by_email()`
  - Verifies the password with `werkzeug.security.check_password_hash`
  - On failure: flashes a generic error and re-renders the form — no redirect
  - On success: stores the user's `id` in `session["user_id"]` and redirects to `url_for("landing")`
  - Public — no login required

- **`GET /logout`**
  - Calls `session.clear()`
  - Redirects to `url_for("landing")`
  - Public — no login required to log out

---

## Database changes

- No schema changes — the `users` table from Step 01 already stores `email` and `password_hash`
- One new helper to add to `database/db.py`:
  - **`get_user_by_email(email)`**
    - Queries the `users` table for a row where `email` matches the argument
    - Returns the matching `sqlite3.Row` if found, or `None` if no match
    - Must live in `database/db.py` — must not be written inline inside the route function

---

## Templates

- Modify `templates/login.html`:
  - Add a `<form>` with `action="{{ url_for('login') }}"` and `method="post"`
  - Include an `email` input (`name="email"`, `type="email"`) and a `password` input (`name="password"`, `type="password"`)
  - Add a section that iterates over `get_flashed_messages()` and displays each message
  - Add a link to `/register` for users who do not yet have an account
  - Keep all existing visual design, layout, and CSS classes completely unchanged

---

## Files to change

- `app.py`
  - Add imports: `session` from `flask`; `get_user_by_email` from `database.db`; `check_password_hash` from `werkzeug.security`
  - Upgrade `login()` to handle both `GET` and `POST` with full credential verification logic
  - Upgrade `logout()` to call `session.clear()` and redirect — remove the raw stub string return

- `database/db.py`
  - Add `get_user_by_email(email)` helper

- `templates/login.html`
  - Wire up form `action`, `method`, and field `name` attributes
  - Add flash message display block
  - Add link to registration page

---

## Files to create

None.

---

## New dependencies

None. This step uses only:
- `werkzeug.security.check_password_hash` — already installed
- `flask.session`, `flask.flash`, `flask.redirect`, `flask.url_for`, `flask.request` — Flask built-ins
- `sqlite3` — Python standard library (via `get_db()`)

---

## Rules for implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting inside SQL
- Verify passwords with `werkzeug.security.check_password_hash` — never compare plaintext
- The session key for the logged-in user must be `session["user_id"]` and its value must be the integer `id` from the `users` table
- Use `flask.session` — do not implement a custom session or cookie mechanism
- On failed login — whether the email is not found or the password is wrong — show exactly one generic flash message: `"Invalid email or password."` — never reveal which field caused the failure
- After successful login redirect to `url_for("landing")` until a dashboard route exists
- `logout()` must call `session.clear()` (not `session.pop`) then redirect to `url_for("landing")`
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex colour values
- Use `url_for()` for every internal link — never hardcode paths

---

## Definition of done

- [ ] `GET /login` renders the login form with `email` and `password` fields
- [ ] Submitting with valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`
- [ ] Submitting with a wrong password flashes `"Invalid email or password."` and stays on the login page
- [ ] Submitting with an unregistered email flashes the same generic error — no distinction from wrong password
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer present in the session
- [ ] The `/logout` route no longer returns the raw stub string
