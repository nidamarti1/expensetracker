# Step 2 — User Registration

## Overview

This step upgrades the existing stub `GET /register` route into a fully functional registration flow that handles both `GET` and `POST`. The form accepts four fields: `name`, `email`, `password`, and `confirm_password`. On successful registration the user receives a flashed success message and is redirected to `/login`. This is the entry point for all authenticated features — no user can log in, manage a profile, or track expenses until they have registered.

---

## Depends on

- Step 01 — Database setup (`users` table, `get_db()`)

---

## Routes

- **`GET /register`**
  - Renders the registration form
  - Public — no login required
  - Already exists as a stub; this step upgrades it in place

- **`POST /register`**
  - Reads `name`, `email`, `password`, `confirm_password` from the submitted form
  - Runs server-side validation (see Rules for Implementation)
  - On failure: re-renders the form with a flashed error message — no redirect
  - On success: creates the user, flashes a success message, redirects to `/login`
  - Public — no login required

---

## Database changes

- No new tables or columns — the existing `users` table covers all requirements
- One new helper to add to `database/db.py`:
  - **`create_user(name, email, password)`**
    - Hashes `password` with `werkzeug.security.generate_password_hash`
    - Inserts a new row into the `users` table
    - Returns the `lastrowid` of the newly created user
    - Raises `sqlite3.IntegrityError` if the email is already taken (propagated from the `UNIQUE` constraint — do not catch it here)

---

## Templates

- Modify `templates/register.html`:
  - Set `action="{{ url_for('register') }}"` and `method="post"` on the `<form>` element
  - Add `name` attributes to all inputs: `name`, `email`, `password`, `confirm_password`
  - Add a section that iterates over `get_flashed_messages()` and displays each message to the user (e.g. "Email already registered", "Passwords do not match", "All fields are required")
  - Keep all existing visual design, layout, and CSS classes completely unchanged

---

## Files to change

- `app.py`
  - Set `app.secret_key` to a hardcoded dev string (required for `flash()`)
  - Upgrade `register()` to handle both `GET` and `POST`
  - Add import for `flash`, `redirect`, `request` from `flask`
  - Add import for `create_user` from `database.db`
  - Add import for `sqlite3` (to catch `IntegrityError`)
  - Implement validation logic and success/failure branching

- `database/db.py`
  - Add `create_user(name, email, password)` helper

- `templates/register.html`
  - Wire up form `action` and `method`
  - Add flash message display block

---

## Files to create

None.

---

## New dependencies

None. This step uses only:
- `werkzeug.security` — already installed
- `flask.flash`, `flask.redirect`, `flask.url_for`, `flask.request` — Flask built-ins
- `sqlite3` — Python standard library

---

## Rules for implementation

- No SQLAlchemy or ORMs — use `sqlite3` directly via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting inside SQL
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext
- `app.secret_key` must be set in `app.py` for `flash()` to work — use a hardcoded dev string for now
- Server-side validation must run in this exact order:
  1. All four fields are non-empty — if any field is blank, flash an error and re-render
  2. `password == confirm_password` — if they differ, flash an error and re-render
  3. Email uniqueness — call `create_user()` and catch `sqlite3.IntegrityError`; if raised, flash "Email already registered" and re-render
- On any validation failure: re-render the form with `render_template('register.html')` — do not redirect
- On success: flash a success message and `redirect(url_for('login'))`
- Use `abort(405)` if an unsupported HTTP method reaches the route
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex colour values
- Use `url_for()` for every internal link — never hardcode URLs

---

## Definition of done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting with all valid fields creates a new row in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error message and makes no DB insert
- [ ] Submitting with an already-registered email re-renders the form with "Email already registered"
- [ ] Submitting with any empty field re-renders the form with a validation error
- [ ] Passwords are stored as hashes — never plaintext — verifiable by inspecting `spendly.db`
- [ ] Repeated valid submissions with the same email do not create duplicate users
