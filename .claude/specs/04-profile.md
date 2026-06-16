# Step 4 — Profile Page (Hardcoded UI)

## Overview

This step replaces the `/profile` stub with a fully designed profile page that displays static, hardcoded data. The goal is to establish the complete UI layout before any real database queries are wired up in Step 05. Four sections are built: a user info card, a summary stats row, a transaction history table, and a category breakdown. Building UI first lets the team validate the design in isolation and ensures the templates are fully ready for the backend-connection step — no placeholder text, no skeleton layouts.

---

## Depends on

- Step 01 — Database setup (schema must exist for the tables that Step 05 will query)
- Step 02 — Registration (user accounts must be creatable so there is something to log in as)
- Step 03 — Login + Logout (session must be set; `/profile` is a protected route that requires `session["user_id"]`)

---

## Routes

- **`GET /profile`**
  - Renders the profile page
  - Logged-in only — if `session["user_id"]` is absent, redirect to `url_for("login")`
  - Already exists as a stub; this step replaces it in place

---

## Database changes

- No database changes
- The existing `users` and `expenses` tables are sufficient for when real queries are added in Step 05
- No DB queries are made in this step — all data passed to the template is hardcoded in `app.py`

---

## Templates

- Create `templates/profile.html` — a full profile page extending `base.html`
- Must contain four sections in this order:

  1. **User info card** — avatar built from initials (e.g. `DU` for Demo User), hardcoded name (`Demo User`), hardcoded email (`demo@spendly.com`), hardcoded member-since date
  2. **Summary stats row** — at least three stat tiles with hardcoded values: total spent (e.g. `₹18,240`), number of transactions (e.g. `34`), top category (e.g. `Food`)
  3. **Transaction history table** — tabular list of recent expenses with columns for date, description, category badge, and amount; at least 3 hardcoded rows covering different categories
  4. **Category breakdown** — per-category totals displayed as a simple list or progress-bar rows; at least 3 hardcoded categories with amounts

---

## Files to change

- `app.py`
  - Replace the `/profile` stub with a real view function
  - Add authentication guard: if `session.get("user_id")` is absent, `redirect(url_for("login"))`
  - Pass hardcoded context variables to `profile.html`:
    - A `user` dict (e.g. `name`, `email`, `member_since`)
    - A `stats` dict (e.g. `total_spent`, `transaction_count`, `top_category`)
    - An `expenses` list of dicts (e.g. `date`, `description`, `category`, `amount`)
    - A `categories` list of dicts (e.g. `name`, `total`, `percentage`)

---

## Files to create

- `templates/profile.html`

---

## New dependencies

None.

---

## Rules for implementation

- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()` if any DB call is ever needed
- Parameterized queries only — never use f-strings or `%` formatting inside SQL
- Authentication guard must use `session.get("user_id")`; if absent, call `redirect(url_for("login"))` — do not use `abort()`
- All data passed to the template must be hardcoded Python dicts and lists in `app.py` — no DB queries in this step
- Use CSS variables — never hardcode hex colour values anywhere in `profile.html`
- No inline `style` attributes anywhere in `profile.html`
- All templates must extend `base.html`
- Category badges in the transaction table must be styled via a CSS class (e.g. `badge-food`, `badge-transport`) — not via inline colour styles
- Use `url_for()` for every internal link — never hardcode paths
- Avatar initials must be rendered from the hardcoded name via a CSS-styled element, not an image

---

## Definition of done

- [ ] Visiting `/profile` without being logged in redirects to `/login`
- [ ] Visiting `/profile` while logged in returns HTTP 200
- [ ] The page displays a user info card with a hardcoded name and email
- [ ] The page displays at least three summary stat values (total spent, transaction count, top category)
- [ ] The page displays a transaction history table with at least three hardcoded rows
- [ ] The page displays a category breakdown section with at least three categories
- [ ] The navbar reflects the logged-in state (username and logout link visible)
- [ ] No hex colour values appear anywhere in `profile.html` — only CSS variables
