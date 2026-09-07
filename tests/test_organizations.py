"""API + service tests for the Organization resource."""


def test_create_organization(client):
    response = client.post(
        "/api/v1/organizations/",
        json={"name": "Acme Corp", "description": "Test org"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["description"] == "Test org"
    assert "id" in data


def test_create_organization_duplicate(client):
    client.post("/api/v1/organizations/", json={"name": "Acme Corp"})
    response = client.post("/api/v1/organizations/", json={"name": "Acme Corp"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_organization_name_too_short(client):
    response = client.post("/api/v1/organizations/", json={"name": "AB"})
    assert response.status_code == 422


def test_get_organizations_empty(client):
    response = client.get("/api/v1/organizations/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_organizations(client):
    client.post("/api/v1/organizations/", json={"name": "Org One"})
    client.post("/api/v1/organizations/", json={"name": "Org Two"})
    response = client.get("/api/v1/organizations/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_organization_by_id(client):
    create = client.post("/api/v1/organizations/", json={"name": "Org One"})
    org_id = create.json()["id"]
    response = client.get(f"/api/v1/organizations/{org_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Org One"


def test_get_organization_not_found(client):
    response = client.get("/api/v1/organizations/9999")
    assert response.status_code == 400


def test_update_organization(client):
    create = client.post("/api/v1/organizations/", json={"name": "Old Name"})
    org_id = create.json()["id"]
    response = client.put(
        f"/api/v1/organizations/{org_id}",
        json={"name": "New Name", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_update_organization_not_found(client):
    response = client.put(
        "/api/v1/organizations/9999",
        json={"name": "Does Not Exist"},
    )
    assert response.status_code == 400


def test_update_organization_duplicate_name(client):
    client.post("/api/v1/organizations/", json={"name": "Org Alpha"})
    create = client.post("/api/v1/organizations/", json={"name": "Org Beta"})
    org_id = create.json()["id"]
    response = client.put(
        f"/api/v1/organizations/{org_id}",
        json={"name": "Org Alpha"},
    )
    assert response.status_code == 400


def test_delete_organization(client):
    create = client.post("/api/v1/organizations/", json={"name": "To Delete"})
    org_id = create.json()["id"]
    response = client.delete(f"/api/v1/organizations/{org_id}")
    assert response.status_code == 204
    get = client.get(f"/api/v1/organizations/{org_id}")
    assert get.status_code == 400


def test_delete_organization_not_found(client):
    response = client.delete("/api/v1/organizations/9999")
    assert response.status_code == 400
