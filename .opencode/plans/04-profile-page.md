# Implementation Plan: Profile Page (Step 4)

## Files modified

| File | Changes |
|------|---------|
| `app.py` | Replace `/profile` stub with real view: auth guard + hardcoded context data |
| `templates/base.html` | Add Lucide CDN script tag + init call |
| `static/css/style.css` | Add profile page styles, category badges, category breakdown bars, responsive rules |

## Files created

| File | Purpose |
|------|---------|
| `templates/profile.html` | Full profile page extending `base.html` — 4 sections |

## Step-by-step

### 1. `templates/base.html` — Lucide setup

- Add `<script src="https://unpkg.com/lucide@latest"></script>` in `<head>` after Google Fonts link
- Add `document.addEventListener("DOMContentLoaded",function(){lucide.createIcons()})` before existing `main.js` script

### 2. `app.py` — rewrite `/profile`

- Auth guard: if `"user_id"` not in session → `redirect(url_for("login"))`
- Hardcoded `user` dict (name, email, member_since, initials)
- Hardcoded `stats` dict (total_spent, transaction_count, top_category)
- Hardcoded `transactions` list (6 rows: date, description, category, amount)
- Hardcoded `categories` list (6 items: name, total, percentage)
- Render `profile.html` with all 4 context variables

### 3. `templates/profile.html` — profile page

Extends `base.html`, 4 sections:

| Section | Content |
|---------|---------|
| **User info card** | Avatar circle with `user.initials`, name, email, member-since date |
| **Summary stats** | 3-column grid: Total Spent (₹12,450), Transactions (42), Top Category (Food). Each with a Lucide icon |
| **Transaction history** | Full table with Date, Description, Category (colored badge via `badge-{category|lower}`), Amount |
| **Category breakdown** | Rows with category name, progress bar (width = percentage), ₹ amount. Bar fill colored via `cat-{name|lower}` class |

All numbers formatted with Jinja `{:,}` filter (Indian thousands separator).

### 4. `static/css/style.css` — new styles

New section "Profile page" added before the Responsive block:

- `.profile-page` — max-width container with padding
- `.profile-card` — flex row with avatar + details
- `.profile-avatar` — 64px circle, accent background, initials text
- `.profile-name` / `.profile-email` / `.profile-meta` — typography
- `.stats-grid` — 3-column grid for stat cards
- `.stat-item` — card with centered content
- `.tx-table-wrap` — card wrapper for table
- `.section-heading` — shared heading style
- `.tx-table` — full-width table with hover
- `.badge` / `.badge-{category}` — pill badges using CSS variables
- `.category-breakdown` / `.category-row` / `.category-bar` — progress bar rows
- `.cat-{category} .category-bar-fill` — per-category bar colors

Responsive additions:
- 900px: stats stack to 1 column, category rows shrink
- 600px: user card stacks vertically, category rows shrink further, table scrollable

## Verification

- [ ] `/profile` without session → redirects to `/login`
- [ ] `/profile` while logged in → HTTP 200, renders template
- [ ] User info card shows avatar initials (DU), name, email, member-since
- [ ] Stats row: Total Spent (₹12,450), Transactions (42), Top Category (Food)
- [ ] Transaction table: 6 hardcoded rows with date, description, colored category badge, ₹ amount
- [ ] Category breakdown: 6 categories with progress bars, colored fills, ₹ totals
- [ ] No hex values in `profile.html` — only CSS variables
- [ ] Category badges use CSS classes (`.badge badge-food` etc.)
- [ ] Lucide icons render (indian-rupee, list, trending-up, arrow-up-right, pie-chart)
- [ ] Navbar shows logged-in state (username + logout) — already works from base.html
- [ ] Responsive: stacks vertically below 900px, avatar centers on 600px
- [ ] `python app.py` starts without errors, server runs on port 5001
