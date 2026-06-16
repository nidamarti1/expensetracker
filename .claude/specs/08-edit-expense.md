# Step 8 — Edit Expense

## Overview

Step 08 lets a logged-in user edit any of their own expenses via a pre-populated form at `/expenses/<id>/edit`. The `GET` handler loads the existing expense from the database and renders the form with its current values pre-filled. The `POST` handler validates the submission and updates the row in place. Ownership is enforced at both the query and route level: a user can only edit expenses that belong to them — any attempt to access another user's expense returns a `404`. Two new query helpers are added to `database/queries.py`: `get_expense_by_id` and `update_expense`. The transactions table in `profile.html` gains an `"Edit"` action link per row, which requires `get_recent_transactions` to also return the expense `id`.

---

## Depends on

- Step 01 — Database setup (`expenses` table exists with all required columns)
- Step 03 — Login / Logout (`session["user_id"]` is set and enforced on every request)
- Step 05 — Profile page renders the transaction list (the `"Edit"` link lives there)
- Step 07 — Add Expense (establishes the form structure, validation rules, and template pattern this step follows)

---

## Routes

- **`GET /expenses/<int:id>/edit`**
  - Renders the edit form pre-populated with the existing expense values
  - Logged-in only — redirect to `/login` if `session["user_id"]` is absent

- **`POST /expenses/<int:id>/edit`**
  - Validates the submitted form fields and saves the updated expense
  - Logged-in only — redirect to `/login` if `session["user_id"]` is absent

---

## Database changes

- No new tables or columns
- All required columns already exist in `expenses`: `id`, `user_id`, `amount`, `category`, `date`, `description`

---

## Templates

- Create `templates/edit_expense.html`:
  - Extends `base.html`
  - `<form>` with `method="POST"` and `action="{{ url_for('edit_expense', id=expense.id) }}"`
  - Fields (identical structure to `add_expense.html`, all pre-filled with current values):
    - `amount` — `<input type="number">`, `step="0.01"`, `min="0.01"`, required, pre-filled with current `amount`
    - `category` — `<select>` with exactly 7 fixed options (`Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`), with the current `category` pre-selected
    - `date` — `<input type="date">`, required, pre-filled with current `date`
    - `description` — `<input type="text">`, optional, `maxlength="200"`, pre-filled with current `description`
  - Submit button labelled `"Save Changes"`
  - Cancel link back to `/profile` using `url_for("profile")`
  - Error message block that re-populates the submitted (not original) values on validation failure

- Modify `templates/profile.html`:
  - Add an `"Actions"` column header to the transactions table
  - Add an `"Edit"` link cell per row pointing to `url_for("edit_expense", id=tx.id)`

---

## Files to change

- `database/queries.py`
  - Add `get_expense_by_id(expense_id, user_id)`:
    - Fetches a single expense row scoped to `id = ? AND user_id = ?`
    - Returns the row as a `sqlite3.Row` (dict-like) if found
    - Returns `None` if not found or if `user_id` does not match — never raises an exception for the not-found case
  - Add `update_expense(expense_id, user_id, amount, category, date, description)`:
    - Issues a parameterized `UPDATE` statement scoped to `id = ? AND user_id = ?`
    - If the `user_id` does not match, 0 rows are affected and no exception is raised
  - Modify `get_recent_transactions`:
    - Add `id` to the `SELECT` column list so each returned dict includes the expense `id` for building edit links

- `app.py`
  - Import `get_expense_by_id` and `update_expense` from `database.queries`
  - Replace the `GET`-only placeholder at `/expenses/<int:id>/edit` with a full `GET + POST` handler using `@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])`
  - `GET`: call `get_expense_by_id(id, session["user_id"])`; call `abort(404)` if `None` is returned; render `edit_expense.html` passing the expense row and the fixed categories list
  - `POST`: read form fields; run validation (same rules as Step 07); call `update_expense()` on success and `redirect(url_for("profile"))`; re-render `edit_expense.html` with errors and submitted values on failure

- `templates/profile.html`
  - Add `"Actions"` column header to the transactions table
  - Add an `"Edit"` link cell per transaction row using `url_for("edit_expense", id=tx.id)`

---

## Files to create

- `templates/edit_expense.html`

---

## New dependencies

None.

---

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting to inject values into SQL
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()` — do not bypass it)
- `get_expense_by_id` must scope its query to `id = ? AND user_id = ?` — return `None` if not found or if the ownership check fails
- `update_expense` must include `user_id = ?` in its `WHERE` clause as a second ownership guard — if the `user_id` does not match, 0 rows are affected silently
- Unauthenticated access to both `GET` and `POST` must redirect to `url_for("login")`
- If `get_expense_by_id` returns `None` (expense not found or belongs to another user), the route must call `abort(404)`
- Validation rules for `POST` (identical to Step 07):
  1. `amount` — required; must parse as a positive `float` greater than `0`; use `float()` and catch `ValueError`
  2. `category` — required; must be one of the 7 fixed categories; reject any value not in the list
  3. `date` — required; must be a valid `YYYY-MM-DD` string; validate with `datetime.strptime(value, "%Y-%m-%d")`
  4. `description` — optional; strip whitespace; store `None` if blank
- On any validation error: re-render `edit_expense.html` with the error message and the submitted (not original) values pre-filled
- After a successful update: redirect to `url_for("profile")` — do not re-render the form
- Currency must always display as ₹ — never £ or $
- Use CSS variables — never hardcode hex colour values
- No inline `style` attributes in any template
- All templates must extend `base.html`
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to write

File: `tests/test_edit_expense.py`

### Unit tests

| Function | Input | Expected output |
|---|---|---|
| `get_expense_by_id` | valid `expense_id`, correct `user_id` | Returns matching row as a dict-like object with correct field values |
| `get_expense_by_id` | valid `expense_id`, wrong `user_id` | Returns `None` |
| `get_expense_by_id` | non-existent `expense_id` | Returns `None` |
| `update_expense` | valid `expense_id`, correct `user_id`, `amount=99.0` | Row in DB reflects updated `amount`; other fields unchanged |
| `update_expense` | valid `expense_id`, wrong `user_id` | Row in DB unchanged; no exception raised; 0 rows affected |

### Route tests

- `GET /expenses/<id>/edit` unauthenticated → redirects to `/login` (HTTP 302)
- `GET /expenses/<id>/edit` authenticated, own expense → returns HTTP 200; response contains a form pre-filled with current expense values; current category is pre-selected in the dropdown
- `GET /expenses/<id>/edit` authenticated, another user's expense → returns HTTP 404
- `GET /expenses/<id>/edit` authenticated, non-existent `id` → returns HTTP 404
- `POST /expenses/<id>/edit` unauthenticated → redirects to `/login` (HTTP 302)
- `POST /expenses/<id>/edit` authenticated, valid data → redirects to `/profile` (HTTP 302); updated values are reflected in the database
- `POST /expenses/<id>/edit` authenticated, another user's expense → returns HTTP 404
- `POST /expenses/<id>/edit` authenticated, `amount` field missing → returns HTTP 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, `amount=0` → returns HTTP 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, non-numeric `amount` (e.g. `"abc"`) → returns HTTP 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, `category` not in fixed list → returns HTTP 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, invalid `date` string → returns HTTP 200; response contains an error message
- `POST /expenses/<id>/edit` authenticated, `description` field empty → redirects to `/profile` (HTTP 302); row updated with `description = NULL`

---

## Definition of done

- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`
- [ ] Visiting `/expenses/<id>/edit` for a non-existent or another user's expense returns HTTP 404
- [ ] Visiting `/expenses/<id>/edit` while logged in shows a form pre-filled with the expense's current values
- [ ] The category dropdown has the correct category pre-selected
- [ ] Submitting valid changes redirects to `/profile` and the updated values appear in the transaction list
- [ ] Submitting with a missing or zero `amount` re-renders the form with an error and the submitted values retained
- [ ] Submitting with an invalid `category` re-renders the form with an error
- [ ] Submitting with an invalid `date` re-renders the form with an error
- [ ] Submitting without a `description` saves the expense successfully with no error
- [ ] Each row in the profile transaction table has an `"Edit"` link pointing to the correct `/expenses/<id>/edit` URL
