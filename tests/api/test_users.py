from app.models import User


async def test_get_users_me_without_auth(ac):
    response = await ac.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_get_users_me(ac, get_token):
    token, user = await get_token()
    response = await ac.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == str(user.id)
    assert json_response["username"] == user.username


async def test_get_users_me_with_expired_token(ac, get_token):
    token, user = await get_token(expired=True)
    response = await ac.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_users_without_permission(ac, get_token):
    token, user = await get_token()
    response = await ac.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_users_successfully(ac, get_token, session):
    token, user = await get_token(perms=("user.get",))
    response = await ac.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["id"] == str(user.id)
    assert json_response[0]["username"] == user.username


async def test_get_user_without_permission(ac, get_token):
    token, user = await get_token()
    response = await ac.get(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_user_successfully(ac, get_token):
    token, user = await get_token(perms=("user.get",))
    response = await ac.get(
        f"/api/v1/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == str(user.id)
    assert json_response["username"] == user.username


async def test_update_user_without_permission(ac, get_token):
    token, user = await get_token()
    response = await ac.put(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2"},
    )
    assert response.status_code == 401


async def test_update_user_successfully(ac, get_token):
    token, user = await get_token(perms=("user.update",))
    response = await ac.put(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["first_name"] == "Ivan2"


async def test_create_user_without_permission(ac, get_token):
    token, user = await get_token()
    response = await ac.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2", "last_name": "Tea2"},
    )
    assert response.status_code == 401


async def test_create_user_successfully(ac, get_token):
    token, user = await get_token(perms=("user.create",))
    response = await ac.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "created_user",
            "first_name": "Ivan2",
            "password": "created_user",
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert json_response["username"] == "created_user"
    assert json_response["first_name"] == "Ivan2"
    assert "password" not in json_response


async def test_remove_user_without_permission(ac, get_token):
    token, user = await get_token()
    response = await ac.delete(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_remove_user_successfully(ac, get_token, session):
    token, _ = await get_token(perms=("user.remove",))

    remove_me = User(username="remove_me", password="test", first_name="Lol")
    session.add(remove_me)
    await session.commit()

    await session.refresh(remove_me)
    response = await ac.delete(
        f"/api/v1/users/{remove_me.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["username"] == "remove_me"


async def test_remove_user_with_incorrect_id(ac, get_token):
    token, user = await get_token(perms=("user.remove",))
    response = await ac.delete(
        "/api/v1/users/100", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


async def test_remove_user_with_un_existent_id(ac, get_token):
    token, user = await get_token(perms=("user.remove",))
    response = await ac.delete(
        "/api/v1/users/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
