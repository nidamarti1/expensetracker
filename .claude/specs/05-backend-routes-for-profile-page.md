# Step 5 — Backend Routes for Profile Page

## Overview

Step 05 replaces all hardcoded data in the `/profile` route with live queries against the SQLite database. The profile page currently renders a static demo user, fixed summary stats, a hand-typed transaction list, and a hardcoded category breakdown. This step wires those four sections to real data so every logged-in user sees their own expenses — registering a new account and visiting `/profile` must show zeroed stats, not Demo User's data. Three parallel subagents handle the three independent data concerns — transaction history, summary stats, and category breakdown — before being integrated into the single `/profile` route.

---

## Depends on

- Step 01 — Database setup (`users` and `expenses` tables exist; `get_db()` is implemented)
- Step 02 — Registration (users are stored in the database with hashed passwords)
- Step 03 — Login / Logout (`session["user_id"]` is set on successful login)
- Step 04 — Profile page static UI (template already renders all four sections; no structural changes needed here)

---

## Routes

- No new routes
- The existing `GET /profile` route is modified in place — hardcoded dicts and lists are replaced with calls to query helpers from `database/queries.py`

---

## Database changes

- No database changes
- The `users` and `expenses` tables already have all required columns: `user_id`, `amount`, `category`, `date`, `description`, `created_at`

---

## Templates

- Modify `templates/profile.html`:
  - Amounts must be rendered with the ₹ symbol (Indian Rupee) — never £ or $
  - All four dynamic sections are already present in the template — no structural changes needed; only the Jinja variables they consume are now sourced from real query results

---

## Files to change

- `app.py`
  - Remove all hardcoded `user`, `stats`, `expenses`, and `categories` dicts/lists from the `profile()` view
  - Import and call the four helpers from `database/queries.py`: `get_user_by_id`, `get_summary_stats`, `get_recent_transactions`, `get_category_breakdown`
  - Pass the returned values as template context — variable names must match what `profile.html` already expects

- `templates/profile.html`
  - Confirm the ₹ symbol is used for all currency display — replace any £ or $ occurrences

---

## Files to create

- `database/queries.py` — pure query helpers with no Flask imports; one function per data concern:
  - **`get_user_by_id(user_id)`**
    - Queries `users` by `id`
    - Returns a dict with keys `name`, `email`, `member_since`
    - `member_since` is derived from `users.created_at` and formatted as `"Month YYYY"` (e.g. `"January 2026"`)
    - Returns `None` if no matching user is found
  - **`get_summary_stats(user_id)`**
    - Returns a dict with keys `total_spent`, `transaction_count`, `top_category`
    - `total_spent` is the sum of all `expenses.amount` for the user (float, rounded to 2 decimal places)
    - `transaction_count` is the count of expense rows for the user
    - `top_category` is the category with the highest combined spend for the user
    - If the user has no expenses: returns `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` — never raises an exception
  - **`get_recent_transactions(user_id, limit=10)`**
    - Returns a list of dicts, each with keys `date`, `description`, `category`, `amount`
    - Ordered newest-first by `date`
    - Returns an empty list if the user has no expenses — never raises an exception
  - **`get_category_breakdown(user_id)`**
    - Returns a list of dicts, each with keys `name`, `amount`, `pct`
    - `pct` is the percentage of total spend rounded to the nearest integer
    - `pct` values across all categories must sum to exactly 100; the largest category absorbs any rounding remainder
    - Ordered by `amount` descending
    - Returns an empty list if the user has no expenses — never raises an exception
  - All four helpers must call `get_db()` internally and close the connection before returning

---

## New dependencies

None.

---

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterized queries only — never use f-strings or `%` formatting to inject values into SQL
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled inside `get_db()` — do not bypass it)
- Currency must always display as ₹ — never £ or $
- `member_since` must be derived from `users.created_at` and formatted as `"Month YYYY"` (e.g. `"January 2026"`)
- `pct` values in the category breakdown must sum to 100; use integer rounding and adjust the largest category to absorb any rounding remainder
- If a user has no expenses, all helpers must return zeros and empty lists — never raise exceptions for the empty-data case
- All helpers in `database/queries.py` must call `get_db()` internally and close the connection before returning — no connection should be left open
- `database/queries.py` must have no Flask imports — it is a pure data layer
- Use CSS variables — never hardcode hex colour values
- No inline `style` attributes in any template
- All templates must extend `base.html`

---

## Tests to write

File: `tests/test_backend_connection.py`

### Unit tests

| Function | Input | Expected output |
|---|---|---|
| `get_user_by_id` | valid `user_id` (seed user) | Dict with correct `name`, `email`, and `member_since` in `"Month YYYY"` format |
| `get_user_by_id` | non-existent `id` | `None` |
| `get_summary_stats` | `user_id` with expenses | Dict with correct `total_spent`, `transaction_count`, and `top_category` |
| `get_summary_stats` | `user_id` with no expenses | `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` |
| `get_recent_transactions` | `user_id` with expenses | Non-empty list ordered newest-first; each item has `date`, `description`, `category`, `amount` |
| `get_recent_transactions` | `user_id` with no expenses | Empty list `[]` |
| `get_category_breakdown` | `user_id` with expenses | Non-empty list ordered by `amount` descending; `pct` values are integers summing to `100` |
| `get_category_breakdown` | `user_id` with no expenses | Empty list `[]` |

### Route tests

- `GET /profile` unauthenticated → redirects to `/login` (HTTP 302)
- `GET /profile` authenticated as the seed user:
  - Returns HTTP 200
  - Response body contains `"Demo User"`
  - Response body contains `"demo@spendly.com"`
  - Response body contains the ₹ symbol
  - `total_spent` displayed equals `₹346.24` (sum of all 8 seed expenses)
  - `transaction_count` displayed is `8`
  - `top_category` displayed is `"Bills"` (highest single-category total among seed data)
  - Transaction list rows appear in newest-first order by date
  - Category breakdown contains all 7 categories

---

## Definition of done

- [ ] Logging in as `demo@spendly.com` / `demo123` shows `"Demo User"` and `"demo@spendly.com"` on the profile page — not any hardcoded strings
- [ ] Total spent displayed on the profile page equals `₹346.24`
- [ ] Transaction count displayed is `8`
- [ ] Top category displayed is `"Bills"`
- [ ] Transaction list shows 8 rows ordered newest date first
- [ ] Category breakdown shows 7 categories with percentage values that add up to `100%`
- [ ] All amounts on the page display the ₹ symbol — no £ or $ anywhere
- [ ] Registering a brand-new user and visiting `/profile` shows `₹0.00` total spent, `0` transactions, and an empty category breakdown — no errors or exceptions
