from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
)


class TestGetUserById:
    def test_valid_user(self, seed_user_id):
        user = get_user_by_id(seed_user_id)
        assert user is not None
        assert user["name"] == "Demo User"
        assert user["email"] == "demo@spendly.com"
        assert user["member_since"]  # e.g. "June 2026"

    def test_nonexistent_user(self):
        assert get_user_by_id(99999) is None


class TestGetSummaryStats:
    def test_with_expenses(self, seed_user_id):
        stats = get_summary_stats(seed_user_id)
        assert stats["total_spent"] == 346.24
        assert stats["transaction_count"] == 8
        assert stats["top_category"] == "Bills"

    def test_no_expenses(self, empty_user_id):
        stats = get_summary_stats(empty_user_id)
        assert stats["total_spent"] == 0
        assert stats["transaction_count"] == 0
        assert stats["top_category"] == "\u2014"


class TestGetRecentTransactions:
    def test_with_expenses(self, seed_user_id):
        txs = get_recent_transactions(seed_user_id)
        assert len(txs) == 8
        for tx in txs:
            assert "date" in tx
            assert "description" in tx
            assert "category" in tx
            assert "amount" in tx
        dates = [tx["date"] for tx in txs]
        assert dates == sorted(dates, reverse=True)

    def test_no_expenses(self, empty_user_id):
        assert get_recent_transactions(empty_user_id) == []


class TestGetCategoryBreakdown:
    def test_with_expenses(self, seed_user_id):
        cats = get_category_breakdown(seed_user_id)
        assert len(cats) == 7
        amounts = [cat["amount"] for cat in cats]
        assert amounts == sorted(amounts, reverse=True)
        pct_sum = sum(cat["pct"] for cat in cats)
        assert pct_sum == 100

    def test_no_expenses(self, empty_user_id):
        assert get_category_breakdown(empty_user_id) == []


class TestProfileRoute:
    def test_unauthenticated_redirect(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 302
        assert resp.location.endswith("/login")

    def test_authenticated_profile(self, auth_client):
        resp = auth_client.get("/profile")
        assert resp.status_code == 200
        assert "Demo User" in resp.text
        assert "demo@spendly.com" in resp.text
        assert "\u20b9" in resp.text
        assert "346.24" in resp.text
        assert "Bills" in resp.text
