from httpx import AsyncClient


async def test_register_success(async_client: AsyncClient):
    response = await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "john@example.com"
    assert data["full_name"] == "John Doe"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    response = await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


async def test_login_success(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    response = await async_client.post("/auth/login", data={
        "username": "john@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    response = await async_client.post("/auth/login", data={
        "username": "john@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


async def test_login_nonexistent_user(async_client: AsyncClient):
    response = await async_client.post("/auth/login", data={
        "username": "nobody@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


async def test_refresh_token(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    })
    login_response = await async_client.post("/auth/login", data={
        "username": "john@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = await async_client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_refresh_invalid_token(async_client: AsyncClient):
    response = await async_client.post("/auth/refresh", json={
        "refresh_token": "invalid.token.here"
    })
    assert response.status_code == 401