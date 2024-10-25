from sqlalchemy import delete

from app.models import User


async def test_get_users_me_without_auth(ac):
    response = await ac.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_get_users_me(ac, create_user, generate_token):
    user = await create_user("test_get_users_me", "test_get_users_me")
    token = generate_token(user.id)
    response = await ac.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["username"] == "test_get_users_me"


async def test_get_users_me_with_expired_token(ac, create_user, generate_token):
    user = await create_user("test_get_users_me_with_expired_token", "test")
    token = generate_token(user.id, True)
    response = await ac.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_users_without_permission(ac, create_user, generate_token):
    user = await create_user("test_get_users_without_permission", "test")
    token = generate_token(user.id)
    response = await ac.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_users_successfully(ac, create_user, generate_token, session):
    # Clear all users
    await session.exec(delete(User))

    user = await create_user("test_get_users_successfully", "test", perms=["user.get"])
    token = generate_token(user.id)
    response = await ac.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["username"] == "test_get_users_successfully"


async def test_get_user_without_permission(ac, create_user, generate_token):
    user = await create_user("test_get_user_without_permission", "test")
    token = generate_token(user.id)
    response = await ac.get(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_get_user_successfully(ac, create_user, generate_token):
    user = await create_user("test_get_user_successfully", "test", perms=["user.get"])
    token = generate_token(user.id)
    response = await ac.get(
        f"/api/v1/users/{user.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["username"] == "test_get_user_successfully"


async def test_update_user_without_permission(ac, create_user, generate_token):
    user = await create_user("test_update_user_without_permission", "test")
    token = generate_token(user.id)
    response = await ac.put(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2"},
    )
    assert response.status_code == 401


async def test_update_user_successfully(ac, create_user, generate_token):
    user = await create_user(
        "test_update_user_successfully", "test", perms=["user.update"]
    )
    token = generate_token(user.id)
    response = await ac.put(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["first_name"] == "Ivan2"


async def test_create_user_without_permission(ac, create_user, generate_token):
    user = await create_user("test_create_user_without_permission", "test")
    token = generate_token(user.id)
    response = await ac.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2", "last_name": "Tea2"},
    )
    assert response.status_code == 401


async def test_create_user_successfully(ac, create_user, generate_token):
    user = await create_user(
        "test_create_user_successfully", "test", perms=["user.create"]
    )
    token = generate_token(user.id)
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


async def test_remove_user_without_permission(ac, create_user, generate_token):
    user = await create_user("test_remove_user_without_permission", "test")
    token = generate_token(user.id)
    response = await ac.delete(
        "/api/v1/users/1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_remove_user_successfully(ac, create_user, generate_token, session):
    remove_me = User(username="remove_me", password="test", first_name="Lol")
    session.add(remove_me)
    await session.commit()

    user = await create_user(
        "test_remove_user_successfully", "test", perms=["user.remove"]
    )

    await session.refresh(remove_me)
    token = generate_token(user.id)
    response = await ac.delete(
        f"/api/v1/users/{remove_me.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["username"] == "remove_me"


async def test_remove_user_with_incorrect_id(ac, create_user, generate_token):
    user = await create_user(
        "test_remove_user_with_incorrect_id", "test", perms=["user.remove"]
    )
    token = generate_token(user.id)
    response = await ac.delete(
        "/api/v1/users/100", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


async def test_remove_user_with_un_existent_id(ac, create_user, generate_token):
    user = await create_user(
        "test_remove_user_with_un_existent_id", "test", perms=["user.remove"]
    )
    token = generate_token(user.id)
    response = await ac.delete(
        "/api/v1/users/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
