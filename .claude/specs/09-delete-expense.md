# Step 9 — Delete Expense

## Overview

Step 09 lets a logged-in user permanently delete one of their own expenses directly from the profile transaction table. A `"Delete"` button per row submits a `POST` request to `/expenses/<id>/delete`. The handler verifies ownership, removes the row from the database, and redirects back to `/profile`. There is no separate confirmation page — a browser-side `confirm()` dialog in the button's `onsubmit` handler prevents accidental deletions. The existing `get_expense_by_id` helper from Step 08 is reused for ownership verification — no new query lookup functions are needed. Only one new mutation helper is added: `delete_expense` in `database/queries.py`.

---

## Depends on

- Step 01 — Database setup (`expenses` table exists)
- Step 03 — Login / Logout (`session["user_id"]` is set and enforced on every request)
- Step 05 — Profile page renders the transaction list (the delete button lives there)
- Step 08 — Edit Expense (`get_expense_by_id` is available; the `"Actions"` column already exists in the profile transactions table)

---

## Routes

- **`POST /expenses/<int:id>/delete`**
  - Verifies ownership, deletes the expense row, redirects to `/profile`
  - Logged-in only — redirect to `/login` if `session["user_id"]` is absent

- No `GET` handler — a bare `GET` to this URL must return HTTP 405

---

## Database changes

- No new tables or columns
- The `expenses` table already has all required columns

---

## Templates

- Modify `templates/profile.html`:
  - Inside the existing `"Actions"` cell per transaction row, add a delete form alongside the existing `"Edit"` link:
    - `<form>` with `method="POST"` and `action="{{ url_for('delete_expense', id=tx.id) }}"`
    - `style="display:inline"` on the `<form>` tag is the one permitted exception to the no-inline-styles rule — it is a layout-utility value only, not a design value
    - `onsubmit="return confirm('Delete this expense?')"` on the `<form>` tag to provide browser-side confirmation before submission
    - A `<button>` with `class="btn-delete"` and label `"Delete"`
  - The `"Edit"` link from Step 08 remains alongside the new `"Delete"` button

---

## Files to change

- `database/queries.py`
  - Add `delete_expense(expense_id, user_id)`:
    - Issues a parameterized `DELETE FROM expenses WHERE id = ? AND user_id = ?`
    - The dual-column `WHERE` clause is the ownership guard — if `user_id` does not match, 0 rows are deleted and no exception is raised
    - Commits and closes the connection before returning

- `app.py`
  - Import `delete_expense` from `database.queries`
  - Replace the `GET`-only placeholder at `/expenses/<int:id>/delete` with a `POST`-only handler using `@app.route("/expenses/<int:id>/delete", methods=["POST"])`
  - Handler steps in order:
    - If `session["user_id"]` is absent: `redirect(url_for("login"))`
    - Call `get_expense_by_id(id, session["user_id"])`; if `None` returned: `abort(404)`
    - Call `delete_expense(id, session["user_id"])`
    - `redirect(url_for("profile"))`

- `templates/profile.html`
  - Add the delete form inside the existing `"Actions"` cell per transaction row

- `static/css/style.css`
  - Add a `.btn-delete` style using CSS variables for a danger colour (e.g. a red-toned CSS variable) — never hardcode hex values

---

## Files to create

None.

---

## New dependencies

None.

---

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting to inject values into SQL
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()` — do not bypass it)
- `delete_expense` must scope its `DELETE` to `id = ? AND user_id = ?` — this is the ownership guard that prevents one user deleting another user's expense
- The route must only accept `POST` — a bare `GET` to the URL must return HTTP 405
- Unauthenticated access must redirect to `url_for("login")` (HTTP 302)
- If the expense does not exist or belongs to another user, `abort(404)`
- After successful deletion, redirect to `url_for("profile")` — do not render a template
- The only permitted inline style is `style="display:inline"` on the `<form>` tag — no hex colours or design values may be inlined anywhere
- Use CSS variables — never hardcode hex colour values
- All templates must extend `base.html`
- Currency must always display as ₹ — never £ or $
- Use `url_for()` for every internal link — never hardcode paths

---

## Tests to write

File: `tests/test_delete_expense.py`

### Unit tests

| Function | Input | Expected output |
|---|---|---|
| `delete_expense` | valid `expense_id`, correct `user_id` | Row removed from the DB; querying for it returns `None` |
| `delete_expense` | valid `expense_id`, wrong `user_id` | Row remains in the DB; 0 rows deleted; no exception raised |
| `delete_expense` | non-existent `expense_id` | No exception raised; DB unchanged |

### Route tests

- `POST /expenses/<id>/delete` unauthenticated → redirects to `/login` (HTTP 302)
- `POST /expenses/<id>/delete` authenticated, own expense → redirects to `/profile` (HTTP 302); row no longer exists in the database
- `POST /expenses/<id>/delete` authenticated, another user's expense → returns HTTP 404; row still exists in the database
- `POST /expenses/<id>/delete` authenticated, non-existent `id` → returns HTTP 404
- `GET /expenses/<id>/delete` any user → returns HTTP 405 (Method Not Allowed)

---

## Definition of done

- [ ] `POST /expenses/<id>/delete` while logged out redirects to `/login`
- [ ] `POST /expenses/<id>/delete` for a non-existent or another user's expense returns HTTP 404
- [ ] `GET /expenses/<id>/delete` returns HTTP 405
- [ ] Clicking `"Delete"` on a transaction row and confirming in the browser dialog removes that expense from the database
- [ ] After deletion, the user is redirected to `/profile` and the deleted expense no longer appears in the transaction list
- [ ] Cancelling the browser `confirm()` dialog does not submit the form and leaves the expense intact
- [ ] Each transaction row in the profile table now shows both `"Edit"` and `"Delete"` actions
