from app.crud.attach import CRUDAttach
from app.crud.client import CRUDClient
from app.models import Attach, AttachGroup, Request, RequestService
from app.schemas.client import ClientCreate


async def test_get_attachs_zero(get_token, ac, session):
    token, _ = await get_token(perms=("attach.get", "request.get"))

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
    request_service = RequestService(name="test", display_name="test")
    session.add(request_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=request_service.id)
    session.add(request)
    await session.flush()

    response = await ac.get(
        "/api/v1/attachs",
        params={"request_id": request.id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 0


async def test_get_attachs_one(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    user = user.id

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
    request_service = RequestService(name="test", display_name="test")
    session.add(request_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=request_service.id)
    session.add(request)
    await session.flush()
    request = request.id

    attach = await CRUDAttach(session).create(
        Attach.model_validate(
            {
                "path": "test.txt",
                "original_name": "test.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )

    response = await ac.get(
        "/api/v1/attachs",
        params={"request_id": request},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["id"] == str(attach.id)


async def test_get_attachs_two(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.flush()
    request = request.id

    crud_attach = CRUDAttach(session)
    attach1 = await crud_attach.create(
        Attach.model_validate(
            {
                "path": "test1.txt",
                "original_name": "test1.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )

    attach2 = await crud_attach.create(
        Attach.model_validate(
            {
                "path": "test2.txt",
                "original_name": "test2.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )
    await session.refresh(attach1)

    response = await ac.get(
        "/api/v1/attachs",
        params={"request_id": request},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 2
    assert (
        json_response[0]["id"] == str(attach1.id)
        and json_response[1]["id"] == str(attach2.id)
    ) or (
        json_response[0]["id"] == str(attach2.id)
        and json_response[1]["id"] == str(attach1.id)
    )


async def test_get_attach_by_id(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.flush()
    request = request.id

    crud_attach = CRUDAttach(session)
    attach = await crud_attach.create(
        Attach.model_validate(
            {
                "path": "test.txt",
                "original_name": "test.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )
    response = await ac.get(
        f"/api/v1/attachs/{attach.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == str(attach.id)


async def test_get_attach_by_id_with_incorrect_id(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    response = await ac.get(
        "/api/v1/attachs/100",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


async def test_get_attach_by_id_with_un_existent_id(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    response = await ac.get(
        "/api/v1/attachs/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_update_attach_successfully(ac, get_token, session):
    token, user = await get_token(perms=("attach.update", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.flush()
    request = request.id

    crud_attach = CRUDAttach(session)
    attach = await crud_attach.create(
        Attach.model_validate(
            {
                "path": "test.txt",
                "original_name": "test.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )

    response = await ac.put(
        f"/api/v1/attachs/{attach.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"original_name": "test2.txt"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["original_name"] == "test2.txt"
    assert json_response["id"] == str(attach.id)


async def test_remove_attach_successfully(ac, get_token, session):
    token, user = await get_token(perms=("attach.remove", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.flush()
    request = request.id

    crud_attach = CRUDAttach(session)
    attach = await crud_attach.create(
        Attach.model_validate(
            {
                "path": "test.txt",
                "original_name": "test.txt",
                "content_type": "text/plain",
                "size": 10,
                "creator_id": str(user),
                "request_id": str(request),
            }
        )
    )

    response = await ac.delete(
        f"/api/v1/attachs/{attach.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["original_name"] == "test.txt"
    assert json_response["id"] == str(attach.id)


async def test_remove_attach_with_un_existent_id(ac, get_token):
    token, user = await get_token(perms=("attach.remove", "request.get"))
    response = await ac.delete(
        "/api/v1/attachs/9c6ff043-3f85-4db1-b6d8-c217d4aa8c1c",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_create_attach_successfully(ac, get_token, session):
    token, user = await get_token(perms=("attach.create", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    session.add(req_service)
    session.add(client)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.commit()
    await session.refresh(request)

    with open(  # noqa: ASYNC230
        "D:/Fedor/Documents/PyCharmProjects/avcrm_backend_fastapi/tests/test.txt",
        "rb",
    ) as f:
        response = await ac.post(
            "/api/v1/attachs",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f},
            data={"request_id": str(request.id)},
        )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["original_name"] == "test.txt"
    assert json_response["content_type"] == "text/plain"
    assert json_response["request_id"] == str(request.id)
    assert json_response["creator_id"] == str(user)


async def test_create_attach_with_group_successfully(ac, get_token, session):
    token, user = await get_token(perms=("attach.create", "request.get"))
    user = user.id

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
    req_service = RequestService(name="test", display_name="test")
    attach_group = AttachGroup(title="test")
    session.add(req_service)
    session.add(client)
    session.add(attach_group)
    await session.flush()

    request = Request(client_id=client.id, request_service_id=req_service.id)
    session.add(request)
    await session.commit()
    await session.refresh(request)
    await session.refresh(attach_group)

    with open(  # noqa: ASYNC230
        "D:/Fedor/Documents/PyCharmProjects/avcrm_backend_fastapi/tests/test.txt",
        "rb",
    ) as f:
        response = await ac.post(
            "/api/v1/attachs",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f},
            data={"request_id": str(request.id), "group_id": attach_group.id},
        )
    assert response.status_code == 201

    json_response = response.json()

    assert "id" in json_response
    assert json_response["group"]["id"] == attach_group.id
    assert json_response["original_name"] == "test.txt"
    assert json_response["content_type"] == "text/plain"
    assert json_response["request_id"] == str(request.id)
    assert json_response["creator_id"] == str(user)
