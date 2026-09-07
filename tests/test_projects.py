"""API + service tests for the Project resource."""


def _create_org(client, name="Test Org"):
    r = client.post("/api/v1/organizations/", json={"name": name})
    return r.json()["id"]


def test_create_project(client):
    org_id = _create_org(client)
    response = client.post(
        f"/api/v1/organizations/{org_id}/projects/",
        json={"name": "Project Alpha", "description": "First project"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Project Alpha"
    assert data["organization_id"] == org_id


def test_create_project_org_not_found(client):
    response = client.post(
        "/api/v1/organizations/9999/projects/",
        json={"name": "Orphan Project"},
    )
    assert response.status_code == 404


def test_get_projects(client):
    org_id = _create_org(client)
    client.post(f"/api/v1/organizations/{org_id}/projects/", json={"name": "Project One"})
    client.post(f"/api/v1/organizations/{org_id}/projects/", json={"name": "Project Two"})
    response = client.get(f"/api/v1/organizations/{org_id}/projects/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project_by_id(client):
    org_id = _create_org(client)
    create = client.post(
        f"/api/v1/organizations/{org_id}/projects/", json={"name": "Project One"}
    )
    project_id = create.json()["id"]
    response = client.get(f"/api/v1/organizations/{org_id}/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Project One"


def test_update_project(client):
    org_id = _create_org(client)
    create = client.post(
        f"/api/v1/organizations/{org_id}/projects/", json={"name": "Old Name"}
    )
    project_id = create.json()["id"]
    response = client.put(
        f"/api/v1/organizations/{org_id}/projects/{project_id}",
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_project(client):
    org_id = _create_org(client)
    create = client.post(
        f"/api/v1/organizations/{org_id}/projects/", json={"name": "Temp Project"}
    )
    project_id = create.json()["id"]
    response = client.delete(f"/api/v1/organizations/{org_id}/projects/{project_id}")
    assert response.status_code == 204


def test_projects_isolated_between_orgs(client):
    org1 = _create_org(client, "Org One")
    org2 = _create_org(client, "Org Two")
    client.post(f"/api/v1/organizations/{org1}/projects/", json={"name": "P1"})
    response = client.get(f"/api/v1/organizations/{org2}/projects/")
    assert response.status_code == 200
    assert response.json() == []
