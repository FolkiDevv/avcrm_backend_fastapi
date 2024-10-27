from app.crud.client import CRUDClient
from app.schemas.client import ClientCreate


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
