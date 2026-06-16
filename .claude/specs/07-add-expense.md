# Step 7 — Add Expense

## Overview

Step 07 lets a logged-in user submit a new expense through a dedicated form page at `/expenses/add`. The route already exists as a `GET` placeholder; this step upgrades it to a full `GET + POST` handler. Validated data is inserted into the `expenses` table and the user is redirected back to the profile page on success. A reusable `insert_expense()` query helper is added to `database/queries.py`. An `"Add Expense"` button is added to `profile.html` and a nav link is added to `base.html` so users can navigate to the form from anywhere in the app.

---

## Depends on

- Step 01 — Database setup (`expenses` table exists with all required columns)
- Step 03 — Login / Logout (`session["user_id"]` is set on login and must be checked on both `GET` and `POST`)
- Step 04 / 05 — Profile page exists and is the natural redirect target after saving a new expense

---

## Routes

- **`GET /expenses/add`**
  - Renders the add-expense form
  - Logged-in only — redirect to `/login` if `session["user_id"]` is absent

- **`POST /expenses/add`**
  - Reads form fields, runs server-side validation, calls `insert_expense()`, redirects to `/profile` on success
  - Logged-in only — redirect to `/login` if `session["user_id"]` is absent

---

## Database changes

- No database changes
- The `expenses` table already has all required columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, `created_at`

---

## Templates

- Create `templates/add_expense.html`:
  - Extends `base.html`
  - `<form>` with `method="POST"` and `action="{{ url_for('add_expense') }}"`
  - Fields:
    - `amount` — `<input type="number">`, `step="0.01"`, `min="0.01"`, required
    - `category` — `<select>` with exactly 7 fixed options: `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`
    - `date` — `<input type="date">`, required, defaults to today's date
    - `description` — `<input type="text">`, optional, `maxlength="200"`
  - Submit button labelled `"Save Expense"`
  - Cancel link back to `/profile` using `url_for("profile")`
  - Flash/error message block that displays validation errors
  - Previously submitted field values must be pre-filled when the form is re-rendered after a validation failure

- Modify `templates/profile.html`:
  - Add an `"Add Expense"` button or link pointing to `url_for("add_expense")`, positioned near the transaction table heading

- Modify `templates/base.html`:
  - Add an `"Add Expense"` link in the navbar, visible only when `session.user_id` is set (i.e. inside a Jinja `{% if session.user_id %}` block)

---

## Files to change

- `app.py`
  - Replace the `GET`-only placeholder at `/expenses/add` with a `GET + POST` handler
  - `GET`: render `add_expense.html`; redirect to `url_for("login")` if not authenticated
  - `POST`: read form fields, run validation, call `insert_expense()`, redirect to `url_for("profile")` on success; re-render form with errors on failure
  - Import `insert_expense` from `database.queries`

- `database/queries.py`
  - Add `insert_expense(user_id, amount, category, date, description)`

- `templates/profile.html`
  - Add `"Add Expense"` button linking to `url_for("add_expense")`

- `templates/base.html`
  - Add `"Add Expense"` navbar link for authenticated users

---

## Files to create

- `templates/add_expense.html`

---

## New dependencies

None.

---

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting to inject values into SQL
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()` — do not bypass it)
- Unauthenticated access to both `GET` and `POST /expenses/add` must redirect to `url_for("login")`
- Server-side validation for `POST` must run in this order:
  1. `amount` — required; must parse as a positive `float` greater than `0`; use `float()` and catch `ValueError`
  2. `category` — required; must be one of the 7 fixed categories; reject any value not in the list
  3. `date` — required; must be a valid `YYYY-MM-DD` string; validate with `datetime.strptime(value, "%Y-%m-%d")`
  4. `description` — optional; strip whitespace; store `None` if blank
- On any validation error: re-render `add_expense.html` with the error message and all previously submitted values pre-filled — do not redirect
- After a successful insert: redirect to `url_for("profile")` — do not re-render the form
- Currency must always display as ₹ — never £ or $
- Use CSS variables — never hardcode hex colour values
- No inline `style` attributes in any template
- All templates must extend `base.html`
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to write

File: `tests/test_add_expense.py`

### Unit tests

| Function | Input | Expected output |
|---|---|---|
| `insert_expense` | valid `user_id`, `amount=50.0`, `category="Food"`, `date="2026-03-20"`, `description="Lunch"` | Row inserted; querying the DB returns the new row with matching values |
| `insert_expense` | valid `user_id`, all fields valid, `description=None` | Row inserted; `description` stored as `NULL` in the DB |

### Route tests

- `GET /expenses/add` unauthenticated → redirects to `/login` (HTTP 302)
- `GET /expenses/add` authenticated → returns HTTP 200; response contains a `<select>` with all 7 category options; response contains a `<form>` with `method="post"`
- `POST /expenses/add` unauthenticated → redirects to `/login` (HTTP 302)
- `POST /expenses/add` authenticated, valid data (`amount=50.0`, `category=Food`, `date=2026-03-20`, `description=Lunch`) → redirects to `/profile` (HTTP 302); new expense row exists in the DB for the test user
- `POST /expenses/add` authenticated, `amount` field missing → returns HTTP 200; response contains an error message
- `POST /expenses/add` authenticated, `amount=0` → returns HTTP 200; response contains an error message
- `POST /expenses/add` authenticated, non-numeric `amount` (e.g. `"abc"`) → returns HTTP 200; response contains an error message
- `POST /expenses/add` authenticated, `category` not in the fixed list (e.g. `"Snacks"`) → returns HTTP 200; response contains an error message
- `POST /expenses/add` authenticated, invalid `date` string (e.g. `"not-a-date"`) → returns HTTP 200; response contains an error message
- `POST /expenses/add` authenticated, `description` field empty → redirects to `/profile` (HTTP 302); row inserted with `description = NULL`

---

## Definition of done

- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in renders a form with `amount`, `category`, `date`, and `description` fields
- [ ] The category dropdown contains exactly: `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`
- [ ] Submitting a valid expense redirects to `/profile` and the new expense appears in the transaction list
- [ ] Submitting with a missing or zero `amount` re-renders the form with an error and all previously entered values retained
- [ ] Submitting with an `amount` that is not a valid positive number re-renders the form with an error
- [ ] Submitting with an invalid `category` re-renders the form with an error
- [ ] Submitting with an invalid `date` re-renders the form with an error
- [ ] Submitting without a `description` saves the expense successfully with no error
- [ ] The `"Add Expense"` button on the profile page navigates to `/expenses/add`
- [ ] The navbar shows an `"Add Expense"` link when the user is logged in
