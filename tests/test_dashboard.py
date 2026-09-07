"""Tests for the dashboard summary API."""


def _make_org(client, name="Test Org"):
    r = client.post("/api/v1/organizations/", json={"name": name})
    return r.json()["id"]


def test_dashboard_summary_empty(client):
    org_id = _make_org(client)
    r = client.get(f"/api/v1/organizations/{org_id}/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_spend"] == 0
    assert data["record_count"] == 0
    assert data["anomaly_count"] == 0
    assert data["provider_breakdown"] == []
    assert data["top_services"] == []
    assert data["recent_anomalies"] == []


def test_dashboard_summary_not_found(client):
    r = client.get("/api/v1/organizations/9999/dashboard/summary")
    assert r.status_code == 404


def test_dashboard_summary_fields(client):
    org_id = _make_org(client)
    r = client.get(f"/api/v1/organizations/{org_id}/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    required_keys = [
        "total_spend", "spend_last_30d", "spend_change_pct",
        "record_count", "anomaly_count", "upload_count",
        "provider_breakdown", "daily_spend", "top_services",
        "recent_anomalies",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"
