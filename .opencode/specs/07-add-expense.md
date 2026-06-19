Spec: Add Expense
Overview
Replace the placeholder "Add expense — coming in Step 7" stub with a full add-expense page. Logged-in users can submit a new expense (amount, category, date, optional description) which gets inserted into the expenses table. This feature unlocks the core transactional capability of Spendly, bridging the static profile dashboard with live data entry.

Depends on
Steps 1–6 (registration, login/logout, profile with data filtering, database queries)

Routes
GET /expenses/add — render the add-expense form — logged-in
POST /expenses/add — validate and insert a new expense, then redirect — logged-in

Database changes
No new tables or columns. The existing expenses table already has: id, user_id, amount, category, date, description, created_at.

Templates
Create: templates/add_expense.html
Modify: none

Files to change
app.py — replace GET stub with real form rendering; add POST handler

Files to create
templates/add_expense.html

New dependencies
No new dependencies

Rules for implementation
No SQLAlchemy or ORMs
Parameterised queries only
Passwords hashed with werkzeug
Use CSS variables — never hardcode hex values
All templates extend base.html

Definition of done
GET /expenses/add shows a form with fields: amount, category (dropdown from CATEGORIES list), date (date picker), description (optional textarea)
POST /expenses/add with valid data inserts a row into expenses and redirects to the profile page
POST /expenses/add with missing/invalid data re-renders the form with an error message
Submitting the form as a logged-out user redirects to the login page
The new expense appears in the profile page's recent transactions table
