from app.crud.client import CRUDClient
from app.crud.request import CRUDRequest
from app.models import RequestService
from app.schemas.client import ClientCreate
from app.schemas.request import RequestCreateWithNewClient


async def test_get_requests_zero(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))

    response = await ac.get(
        "/api/v1/requests",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 0


async def test_get_requests_one(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    request = await CRUDRequest(session).create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service.id,
            }
        )
    )

    response = await ac.get(
        "/api/v1/requests",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["id"] == str(request.id)


async def test_get_requests_two(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)
    req_service = req_service.id

    crud_request = CRUDRequest(session)
    request1 = await crud_request.create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service,
            }
        )
    )

    request2 = await crud_request.create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan2",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service,
            }
        )
    )
    await session.refresh(request1)

    response = await ac.get(
        "/api/v1/requests",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 2
    assert (
        json_response[0]["id"] == str(request1.id)
        and json_response[1]["id"] == str(request2.id)
    ) or (
        json_response[0]["id"] == str(request2.id)
        and json_response[1]["id"] == str(request1.id)
    )


async def test_get_request_by_id(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    request = await CRUDRequest(session).create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service.id,
            }
        )
    )
    response = await ac.get(
        f"/api/v1/requests/{request.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == str(request.id)


async def test_get_request_by_id_with_incorrect_id(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))
    response = await ac.get(
        "/api/v1/requests/100",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_get_request_by_id_with_un_existent_id(get_token, ac, session):
    token, _ = await get_token(perms=("request.get",))
    response = await ac.get(
        "/api/v1/requests/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_update_request_successfully(ac, get_token, session):
    token, user = await get_token(perms=("request.update",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    request = await CRUDRequest(session).create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service.id,
            }
        )
    )
    await session.refresh(request)

    response = await ac.put(
        f"/api/v1/requests/{request.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"number_in_program": "12121212121212"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["client"]["user"]["first_name"] == "Ivan"
    assert json_response["number_in_program"] == "12121212121212"
    assert json_response["id"] == str(request.id)


async def test_remove_request_successfully(ac, get_token, session):
    token, user = await get_token(perms=("request.remove",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    request = await CRUDRequest(session).create(
        RequestCreateWithNewClient.model_validate(
            {
                "first_name": "Ivan",
                "phone": "+79999999999",
                "number_in_program": "123456789",
                "note": "test",
                "request_service_id": req_service.id,
            }
        )
    )

    response = await ac.delete(
        f"/api/v1/requests/{request.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["client"]["user"]["first_name"] == "Ivan"
    assert json_response["id"] == str(request.id)


async def test_remove_request_with_un_existent_id(ac, get_token):
    token, user = await get_token(perms=("request.remove",))
    response = await ac.delete(
        "/api/v1/requests/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_create_request_successfully(ac, get_token, session):
    token, user = await get_token(perms=("request.create",))

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    response = await ac.post(
        "/api/v1/requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Ivan",
            "phone": "+79999999999",
            "number_in_program": "123456789",
            "note": "test",
            "request_service_id": req_service.id,
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["client"]["user"]["first_name"] == "Ivan"
    assert json_response["client"]["user"]["phone"] == "+79999999999"
    assert json_response["client"]["user"]["email"] is None
    assert json_response["note"] == "test"


async def test_create_request_with_existing_client(ac, get_token, session):
    token, user = await get_token(perms=("request.create",))

    await CRUDClient(session).create(
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

    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    await session.commit()
    await session.refresh(req_service)

    response = await ac.post(
        "/api/v1/requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Ivan",
            "phone": "+79999999999",
            "number_in_program": "123456789",
            "note": "test",
            "request_service_id": req_service.id,
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["client"]["user"]["first_name"] == "Ivan"
    assert json_response["client"]["user"]["phone"] == "+79999999999"
    assert json_response["client"]["user"]["email"] is None
    assert json_response["note"] == "test"
