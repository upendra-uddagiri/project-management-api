from httpx import AsyncClient


async def test_create_project(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post("/projects/", json={
        "name": "Test Project",
        "description": "A test project"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert "id" in data
    assert "owner_id" in data


async def test_get_projects(async_client: AsyncClient, auth_headers: dict):
    await async_client.post("/projects/", json={
        "name": "Project 1"
    }, headers=auth_headers)
    await async_client.post("/projects/", json={
        "name": "Project 2"
    }, headers=auth_headers)

    response = await async_client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_get_project_by_id(async_client: AsyncClient, auth_headers: dict):
    create_response = await async_client.post("/projects/", json={
        "name": "Test Project"
    }, headers=auth_headers)
    project_id = create_response.json()["id"]

    response = await async_client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == project_id


async def test_update_project(async_client: AsyncClient, auth_headers: dict):
    create_response = await async_client.post("/projects/", json={
        "name": "Old Name",
        "description": "Old description"
    }, headers=auth_headers)
    project_id = create_response.json()["id"]

    response = await async_client.patch(f"/projects/{project_id}", json={
        "name": "New Name"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["description"] == "Old description"


async def test_delete_project(async_client: AsyncClient, auth_headers: dict):
    create_response = await async_client.post("/projects/", json={
        "name": "To Delete"
    }, headers=auth_headers)
    project_id = create_response.json()["id"]

    response = await async_client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = await async_client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_get_project_unauthorized(
    async_client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict
):
    create_response = await async_client.post("/projects/", json={
        "name": "Private Project"
    }, headers=auth_headers)
    project_id = create_response.json()["id"]

    response = await async_client.get(f"/projects/{project_id}", headers=second_auth_headers)
    assert response.status_code == 403


async def test_create_project_unauthenticated(async_client: AsyncClient):
    response = await async_client.post("/projects/", json={
        "name": "Test Project"
    })
    assert response.status_code == 401