from app.crud.client import CRUDClient
from app.crud.user import CRUDUser
from app.schemas.client import ClientCreate
from app.schemas.user import UserCreate


async def test_get_clients_zero(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))

    response = await ac.get(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 0


async def test_get_clients_one(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))

    crud_client = CRUDClient(session)
    client = await crud_client.create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan",
                "last_name": "Tea",
                "phone": "+79999999999",
                "email": "test@test.com",
                "note": "test",
            }
        )
    )

    response = await ac.get(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
    )
    json_response = response.json()
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["id"] == str(client.id)


async def test_get_clients_two(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))

    crud_client = CRUDClient(session)
    client1 = await crud_client.create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan",
                "last_name": "Tea",
                "phone": "+79999999999",
                "note": "test",
            }
        )
    )

    client2 = await crud_client.create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan2",
                "last_name": "Tea2",
                "phone": "+79999999999",
                "email": "test2@test.com",
            }
        )
    )
    await session.refresh(client1)

    response = await ac.get(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 2
    assert (
        json_response[0]["id"] == str(client1.id)
        and json_response[1]["id"] == str(client2.id)
    ) or (
        json_response[0]["id"] == str(client2.id)
        and json_response[1]["id"] == str(client1.id)
    )


async def test_get_client_by_id(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))
    crud_client = CRUDClient(session)
    client = await crud_client.create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan",
                "last_name": "Tea",
                "phone": "+79999999999",
                "email": "test@test.com",
                "note": "test",
            }
        )
    )
    response = await ac.get(
        f"/api/v1/clients/{client.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == str(client.id)


async def test_get_client_by_id_with_incorrect_id(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))
    response = await ac.get(
        "/api/v1/clients/100",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_get_client_by_id_with_un_existent_id(get_token, ac, session):
    token, _ = await get_token(perms=("client.get",))
    response = await ac.get(
        "/api/v1/clients/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_update_client_successfully(ac, get_token, session):
    token, user = await get_token(perms=("client.update",))

    client = await CRUDClient(session).create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan",
                "last_name": "Tea",
                "phone": "+79999999999",
                "email": "test@test.com",
                "note": "test",
            }
        )
    )

    response = await ac.put(
        f"/api/v1/clients/{client.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Ivan2"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["user"]["first_name"] == "Ivan2"
    assert json_response["id"] == str(client.id)


async def test_remove_client_successfully(ac, get_token, session):
    token, user = await get_token(perms=("client.remove",))

    client = await CRUDClient(session).create(
        ClientCreate.model_validate(
            {
                "first_name": "Ivan",
                "last_name": "Tea",
                "phone": "+79999999999",
                "email": "test@test.com",
                "note": "test",
            }
        )
    )
    await session.refresh(client)

    response = await ac.delete(
        f"/api/v1/clients/{client.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["user"]["first_name"] == "Ivan"
    assert json_response["id"] == str(client.id)


async def test_remove_client_with_un_existent_id(ac, get_token):
    token, user = await get_token(perms=("client.remove",))
    response = await ac.delete(
        "/api/v1/clients/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_create_client_successfully(ac, get_token, session):
    token, user = await get_token(perms=("client.create",))

    response = await ac.post(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Ivan",
            "last_name": "Tea",
            "phone": "+79999999999",
            "email": "test@test.com",
            "note": "test",
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["user"]["first_name"] == "Ivan"
    assert json_response["user"]["last_name"] == "Tea"
    assert json_response["user"]["phone"] == "+79999999999"
    assert json_response["user"]["email"] == "test@test.com"
    assert json_response["note"] == "test"


async def test_create_client_with_existing_user(ac, get_token, session):
    token, user = await get_token(perms=("client.create",))

    await CRUDUser(session).create(
        UserCreate.model_validate(
            {
                "username": "tests",
                "first_name": "Ivan",
                "last_name": "Tea",
                "password": "test",
            }
        )
    )

    response = await ac.post(
        "/api/v1/clients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Ivan",
            "last_name": "Tea",
            "phone": "+79999999999",
            "email": "test@test.com",
            "note": "test",
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["user"]["username"] != "tests"
    assert json_response["user"]["first_name"] == "Ivan"
    assert json_response["user"]["last_name"] == "Tea"
    assert json_response["user"]["phone"] == "+79999999999"
    assert json_response["user"]["email"] == "test@test.com"
    assert json_response["note"] == "test"
