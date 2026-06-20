from httpx import AsyncClient


# helper to avoid repeating project creation in every test
async def create_test_project(async_client: AsyncClient, auth_headers: dict) -> str:
    response = await async_client.post("/projects/", json={
        "name": "Test Project",
        "description": "For task testing"
    }, headers=auth_headers)
    return response.json()["id"]


async def test_create_task(async_client: AsyncClient, auth_headers: dict):
    project_id = await create_test_project(async_client, auth_headers)

    response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Test Task",
        "description": "A test task"
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "todo"
    assert data["project_id"] == project_id


async def test_get_task(async_client: AsyncClient, auth_headers: dict):
    project_id = await create_test_project(async_client, auth_headers)
    create_response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Test Task"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = await async_client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id


async def test_update_task_status(async_client: AsyncClient, auth_headers: dict):
    project_id = await create_test_project(async_client, auth_headers)
    create_response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Test Task"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = await async_client.patch(f"/tasks/{task_id}", json={
        "status": "in_progress"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


async def test_delete_task(async_client: AsyncClient, auth_headers: dict):
    project_id = await create_test_project(async_client, auth_headers)
    create_response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Task to delete"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = await async_client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = await async_client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


async def test_get_tasks_with_filter(async_client: AsyncClient, auth_headers: dict):
    project_id = await create_test_project(async_client, auth_headers)

    # create two tasks
    task1_response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Task 1"
    }, headers=auth_headers)
    await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Task 2"
    }, headers=auth_headers)
    task1_id = task1_response.json()["id"]

    # update task1 to in_progress
    await async_client.patch(f"/tasks/{task1_id}", json={
        "status": "in_progress"
    }, headers=auth_headers)

    # filter by in_progress — should only return task1
    response = await async_client.get(
        f"/projects/{project_id}/tasks?status=in_progress",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"


async def test_get_task_unauthorized(
    async_client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict
):
    project_id = await create_test_project(async_client, auth_headers)
    create_response = await async_client.post(f"/projects/{project_id}/tasks", json={
        "title": "Private Task"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = await async_client.get(f"/tasks/{task_id}", headers=second_auth_headers)
    assert response.status_code == 403