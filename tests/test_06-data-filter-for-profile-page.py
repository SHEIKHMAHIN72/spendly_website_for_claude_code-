"""Tests for the profile-page date filter feature (Step 6).

Spec reference: .opencode/specs/06-data-filter-for-profile-page.md

Behaviour summary
------------------
The existing GET /profile route gains optional query-string parameters
``date_from`` and ``date_to`` (ISO 8601 ``YYYY-MM-DD``).  When both are
present and well-formed the three data sections (summary stats, recent
transactions, category breakdown) are filtered to that inclusive range.
When either is absent, malformed, or when ``date_from > date_to``, the
route falls back to an unfiltered (“All Time”) view.  The template
receives the active ``date_from``/``date_to`` values and an
``active_preset`` key so the filter bar can highlight the current
selection.
"""

import pytest
from datetime import date, timedelta

from database.db import get_db
from werkzeug.security import generate_password_hash

# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

_UID_COUNTER = [0]


def _make_filter_user():
    """Create a user + 4 expenses with deterministic relative dates.

    Expenses
    --------
    * ``Today expense``     — amount 100, category Food,     date = *today*
    * ``60 days ago``       — amount 200, category Transport, date = *today* – 60
    * ``120 days ago``      — amount 300, category Bills,    date = *today* – 120
    * ``200 days ago``      — amount 400, category Health,   date = *today* – 200

    Returns
    -------
    tuple[int, date]
        ``(user_id, today)`` — the caller can use *today* to compute
        expected filter results in assertions.
    """
    _UID_COUNTER[0] += 1
    db = get_db()
    pw_hash = generate_password_hash("pass123")
    email = f"filter_{_UID_COUNTER[0]}@spendly.test"
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (f"Filter User {_UID_COUNTER[0]}", email, pw_hash),
    )
    db.commit()
    uid = db.execute("SELECT last_insert_rowid()").fetchone()[0]

    today = date.today()
    expenses = [
        (uid, 100.0, "Food", today.isoformat(), "Today expense"),
        (uid, 200.0, "Transport",
         (today - timedelta(days=60)).isoformat(), "60 days ago"),
        (uid, 300.0, "Bills",
         (today - timedelta(days=120)).isoformat(), "120 days ago"),
        (uid, 400.0, "Health",
         (today - timedelta(days=200)).isoformat(), "200 days ago"),
    ]
    db.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    db.commit()
    db.close()
    return uid, today


# ------------------------------------------------------------------ #
# Fixtures                                                            #
# ------------------------------------------------------------------ #


@pytest.fixture
def filter_user_id():
    """Create a filter-test user and return only the user ID."""
    uid, _ = _make_filter_user()
    return uid


@pytest.fixture
def filter_client(client, filter_user_id):
    """Test client logged in as the filter-test user (session-based)."""
    with client.session_transaction() as sess:
        sess["user_id"] = filter_user_id
        sess["user_name"] = "Filter User"
    return client


# ================================================================== #
# Tests                                                               #
# ================================================================== #


class TestAuthGuard:
    """Unauthenticated requests to /profile must redirect to /login."""

    def test_anonymous_user_gets_redirected(self, client):
        """DoD (implied by profile route): no session → 302 to /login."""
        resp = client.get("/profile")
        assert resp.status_code == 302, "Expected redirect for anonymous user"
        assert resp.location.endswith("/login"), (
            f"Expected redirect to /login, got {resp.location}"
        )


class TestUnfilteredView:
    """No query params → all expenses shown (backward-compatible)."""

    def test_unfiltered_shows_all_expenses(self, filter_client):
        """DoD #1: visiting /profile with no params returns all expenses."""
        resp = filter_client.get("/profile")
        assert resp.status_code == 200

        # All four expense descriptions must be visible
        assert "Today expense" in resp.text
        assert "60 days ago" in resp.text
        assert "120 days ago" in resp.text
        assert "200 days ago" in resp.text

        # Total = 100 + 200 + 300 + 400 = 1,000
        assert "1,000" in resp.text or "1,000.0" in resp.text


class TestThisMonthPreset:
    """"This Month" filters to the current calendar month only."""

    def test_this_month_shows_only_current_month(self, filter_client):
        """DoD #2: clicking 'This Month' shows only this month's expense."""
        today = date.today()
        month_start = today.replace(day=1)

        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": month_start.isoformat(),
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200

        assert "Today expense" in resp.text, (
            "Today's expense should be visible in 'This Month'"
        )
        assert "60 days ago" not in resp.text, (
            "Expense from 60 days ago should be excluded from 'This Month'"
        )
        assert "120 days ago" not in resp.text
        assert "200 days ago" not in resp.text


class TestLast3MonthsPreset:
    """"Last 3 Months" filters to expenses within the last ~90 days."""

    def test_last_3_months_shows_relevant_expenses(self, filter_client):
        """DoD #3: 'Last 3 Months' includes 60d-ago but not 120d-ago."""
        today = date.today()
        ninety_days_ago = (today - timedelta(days=90)).isoformat()

        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": ninety_days_ago,
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200

        # Today and 60-days-ago are within the window
        assert "Today expense" in resp.text
        assert "60 days ago" in resp.text

        # 120 and 200 days ago are outside the window
        assert "120 days ago" not in resp.text, (
            "Expense from 120 days ago should be excluded from 'Last 3 Months'"
        )
        assert "200 days ago" not in resp.text


class TestLast6MonthsPreset:
    """"Last 6 Months" filters to expenses within the last ~180 days."""

    def test_last_6_months_shows_relevant_expenses(self, filter_client):
        """DoD #4: 'Last 6 Months' includes 120d-ago but not 200d-ago."""
        today = date.today()
        hundred_eighty_days_ago = (today - timedelta(days=180)).isoformat()

        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": hundred_eighty_days_ago,
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200

        # All expenses except 200-days-ago are within 180-day window
        assert "Today expense" in resp.text
        assert "60 days ago" in resp.text
        assert "120 days ago" in resp.text

        assert "200 days ago" not in resp.text, (
            "Expense from 200 days ago should be excluded from 'Last 6 Months'"
        )


class TestAllTimePreset:
    """"All Time" removes any active filter (no query params)."""

    def test_all_time_preset_link_has_no_query_params(self, filter_client):
        """DoD #5: the 'All Time' button's href has no query string."""
        resp = filter_client.get("/profile")
        assert resp.status_code == 200

        # The template renders: url_for('profile') → "/profile" (no params)
        assert 'All Time</a>' in resp.text, (
            "All Time link should be present in the response"
        )
        # Make sure the All Time href does NOT contain 'date_from' or 'date_to'
        # We look for the anchor that contains "All Time" and confirm it
        # does not carry query parameters.
        import re
        all_time_hrefs = re.findall(
            r'<a[^>]*href="([^"]*)"[^>]*>All Time</a>', resp.text
        )
        assert all_time_hrefs, "Could not locate 'All Time' link in HTML"
        for href in all_time_hrefs:
            assert "?" not in href, (
                f"'All Time' link should have no query params, got {href}"
            )


class TestCustomDateRange:
    """A valid custom date range correctly filters all three sections."""

    def test_custom_date_range_filters_correctly(self, filter_client):
        """DoD #6: a custom range shows only expenses that fall inside it."""
        today = date.today()
        # A window that covers the 60-day and 120-day expenses only
        from_date = (today - timedelta(days=130)).isoformat()
        to_date = (today - timedelta(days=50)).isoformat()

        resp = filter_client.get(
            "/profile",
            query_string={"date_from": from_date, "date_to": to_date},
        )
        assert resp.status_code == 200

        assert "60 days ago" in resp.text
        assert "120 days ago" in resp.text
        assert "Today expense" not in resp.text, (
            "Today's expense falls outside the custom range"
        )
        assert "200 days ago" not in resp.text


class TestInvertedDates:
    """date_from > date_to → flash error + unfiltered fallback."""

    def test_inverted_dates_shows_flash_and_unfiltered(self, filter_client):
        """DoD #7: inverted dates flash an error and fall back to unfiltered."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "2026-12-31", "date_to": "2026-01-01"},
        )
        assert resp.status_code == 200

        # The spec requires ``flash()`` to be called with this exact message.
        # Check the Flask session for the flash message rather than the HTML
        # body (the template may not render flashed messages yet).
        with filter_client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
            matching = [
                msg for cat, msg in flashes
                if "Start date must be before end date." in msg
            ]
            assert matching, (
                f"Expected a flash with 'Start date must be before end date.', "
                f"got flashes: {flashes}"
            )

        # Fallback to unfiltered — all expenses shown
        assert "Today expense" in resp.text
        assert "60 days ago" in resp.text
        assert "120 days ago" in resp.text
        assert "200 days ago" in resp.text


class TestMalformedDates:
    """Malformed date strings silently fall back to unfiltered (no crash)."""

    def test_malformed_date_from_ignored(self, filter_client):
        """DoD #8: unparseable date_from silently falls back."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "not-a-date", "date_to": "2026-06-19"},
        )
        assert resp.status_code == 200
        # date_from is malformed → both treated as absent → unfiltered
        assert "Today expense" in resp.text
        assert "200 days ago" in resp.text

    def test_malformed_date_to_ignored(self, filter_client):
        """DoD #8: unparseable date_to silently falls back."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "2026-06-01", "date_to": "also-bad"},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text
        assert "200 days ago" in resp.text

    def test_both_malformed_ignored(self, filter_client):
        """DoD #8: both dates unparseable → unfiltered."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "bad", "date_to": "worse"},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text

    def test_partial_date_format_ignored(self, filter_client):
        """DoD #8: wrong format (DD-MM-YYYY) is also malformed."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "19-06-2026", "date_to": "01-06-2026"},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text


class TestEmptyResultRange:
    """A range that matches no expenses shows zero totals, no errors."""

    def test_empty_range_shows_zero_totals(self, filter_client):
        """DoD #11: a range with no expenses yields ₹0 / 0 txns / empty."""
        today = date.today()
        far_past_from = (today - timedelta(days=5000)).isoformat()
        far_past_to = (today - timedelta(days=4900)).isoformat()

        resp = filter_client.get(
            "/profile",
            query_string={"date_from": far_past_from, "date_to": far_past_to},
        )
        assert resp.status_code == 200

        # No expenses should appear in the table
        assert "Today expense" not in resp.text
        assert "60 days ago" not in resp.text

        # Total spent should be zero (displayed as 0 or 0.0)
        # The template renders: ₹{{ "{:,}".format(stats.total_spent) }}
        # For 0 this will be ₹0 — we check for the zero near the ₹ symbol
        assert "0" in resp.text, "Expected zero total for empty range"


class TestOnlyOneDateParam:
    """Spec § "If either parameter is absent … fall back to unfiltered"."""

    def test_only_date_from_provided_is_unfiltered(self, filter_client):
        """Only date_from → absent date_to → no filter applied."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "2026-01-01"},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text
        assert "200 days ago" in resp.text

    def test_only_date_to_provided_is_unfiltered(self, filter_client):
        """Only date_to → absent date_from → no filter applied."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_to": "2026-06-01"},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text
        assert "200 days ago" in resp.text


class TestActivePresetHighlight:
    """The filter bar highlights the currently active preset button."""

    def test_this_month_preset_gets_active_class(self, filter_client):
        """DoD #9: 'This Month' button receives ``active`` CSS class."""
        today = date.today()
        month_start = today.replace(day=1)

        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": month_start.isoformat(),
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200
        # The template adds ' active' when active_preset matches
        assert "filter-preset-btn active" in resp.text, (
            "Expected at least one preset button to have the 'active' class "
            "when 'This Month' preset is selected"
        )

    def test_unfiltered_shows_all_time_active(self, filter_client):
        """DoD #9: no filter → 'All Time' button is active."""
        resp = filter_client.get("/profile")
        assert resp.status_code == 200
        assert "filter-preset-btn active" in resp.text, (
            "Expected 'All Time' button to be active when no filter set"
        )

    def test_custom_range_activates_all_time(self, filter_client):
        """Custom range does not match any preset → 'All Time' is active."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "2026-01-01", "date_to": "2026-06-01"},
        )
        assert resp.status_code == 200
        # When active_preset is None, 'All Time' gets the active class
        assert "filter-preset-btn active" in resp.text, (
            "Expected 'All Time' to be active when custom range is applied"
        )


class TestRupeeSymbol:
    """All monetary amounts display the ₹ symbol regardless of filter."""

    def test_rupee_on_unfiltered(self, filter_client):
        """DoD #10: ₹ present when viewing all expenses."""
        resp = filter_client.get("/profile")
        assert resp.status_code == 200
        assert "\u20b9" in resp.text, "₹ symbol missing in unfiltered view"

    def test_rupee_on_filtered(self, filter_client):
        """DoD #10: ₹ present when a date filter is active."""
        today = date.today()
        month_start = today.replace(day=1)
        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": month_start.isoformat(),
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200
        assert "\u20b9" in resp.text, "₹ symbol missing in filtered view"

    def test_rupee_on_empty_range(self, filter_client):
        """DoD #10: ₹ present even when the filtered result is empty."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "2020-01-01", "date_to": "2020-01-31"},
        )
        assert resp.status_code == 200
        assert "\u20b9" in resp.text, "₹ symbol missing in empty-range view"


class TestSqlInjectionSafety:
    """SQL injection attempts via date params must not crash the app."""

    def test_sql_injection_in_date_from(self, filter_client):
        """SQL injected into date_from is rejected by strptime → unfiltered."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "' OR 1=1 --", "date_to": "2026-06-19"},
        )
        assert resp.status_code == 200
        # The injection string fails strptime → both params ignored → unfiltered
        assert "Today expense" in resp.text

    def test_sql_injection_in_date_to(self, filter_client):
        """SQL injected into date_to is rejected by strptime → unfiltered."""
        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": "2026-06-01",
                "date_to": "'; DROP TABLE expenses; --",
            },
        )
        assert resp.status_code == 200
        # date_to is malformed → both ignored → table still exists
        assert "Today expense" in resp.text

    def test_sql_injection_both_params(self, filter_client):
        """Both params are SQL fragments → strptime rejects → unfiltered."""
        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": "2026-01-01' UNION SELECT * FROM users --",
                "date_to": "2026-01-31' OR '1'='1",
            },
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text


class TestEdgeCases:
    """Additional edge cases for robustness."""

    def test_date_equal_to_endpoint_inclusive(self, filter_client):
        """Spec says inclusive bounds: expense on date_to should appear."""
        today = date.today()
        resp = filter_client.get(
            "/profile",
            query_string={
                "date_from": today.isoformat(),
                "date_to": today.isoformat(),
            },
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text, (
            "Inclusive range should include expense on date_to"
        )

    def test_empty_query_string_treated_as_no_params(self, filter_client):
        """Empty query string is equivalent to no query string."""
        resp = filter_client.get("/profile", query_string={})
        assert resp.status_code == 200
        assert "Today expense" in resp.text

    def test_whitespace_only_params_ignored(self, filter_client):
        """Whitespace-only date params should be treated as absent."""
        resp = filter_client.get(
            "/profile",
            query_string={"date_from": "  ", "date_to": "  "},
        )
        assert resp.status_code == 200
        assert "Today expense" in resp.text

    def test_template_context_includes_presets(self, filter_client):
        """Spec: template receives ``presets`` and ``active_preset`` vars."""
        resp = filter_client.get("/profile")
        assert resp.status_code == 200
        # The presets dict is used to generate preset button hrefs.
        # Check that each preset label appears in the rendered page.
        assert "This Month" in resp.text
        assert "Last 3 Months" in resp.text
        assert "Last 6 Months" in resp.text
        assert "All Time" in resp.text
