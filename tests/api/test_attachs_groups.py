from app.models import AttachGroup


async def test_get_attachs_groups_zero(get_token, ac, session):
    token, _ = await get_token(perms=("attach.get", "request.get"))

    response = await ac.get(
        "/api/v1/attachs/groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 0


async def test_get_attachs_groups_one(get_token, ac, session):
    token, _ = await get_token(perms=("attach.get", "request.get"))

    attach_group = AttachGroup(title="test")
    session.add(attach_group)
    await session.commit()
    await session.refresh(attach_group)

    response = await ac.get(
        "/api/v1/attachs/groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 1
    assert json_response[0]["id"] == attach_group.id


async def test_get_attachs_groups_two(get_token, ac, session):
    token, _ = await get_token(perms=("attach.get", "request.get"))

    attach_group1 = AttachGroup(title="tEst")
    attach_group2 = AttachGroup(title="Тест")
    session.add(attach_group1)
    session.add(attach_group2)
    await session.commit()
    await session.refresh(attach_group1)
    await session.refresh(attach_group2)

    response = await ac.get(
        "/api/v1/attachs/groups",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert len(json_response) == 2
    assert (
        json_response[0]["id"] == attach_group1.id
        and json_response[1]["id"] == attach_group2.id
    ) or (
        json_response[0]["id"] == attach_group2.id
        and json_response[1]["id"] == attach_group1.id
    )


async def test_get_attachs_group_by_id(get_token, ac, session):
    token, _ = await get_token(perms=("attach.get", "request.get"))

    attach_group = AttachGroup(title="test")
    session.add(attach_group)
    await session.commit()
    await session.refresh(attach_group)

    response = await ac.get(
        f"/api/v1/attachs/groups/{attach_group.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == attach_group.id


async def test_get_attach_group_by_id_with_un_existent_id(get_token, ac, session):
    token, user = await get_token(perms=("attach.get", "request.get"))
    response = await ac.get(
        "/api/v1/attachs/groups/1111",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_update_attach_group_successfully(get_token, ac, session):
    token, user = await get_token(perms=("attach.update",))

    attach_group = AttachGroup(title="test")
    session.add(attach_group)
    await session.commit()
    await session.refresh(attach_group)

    response = await ac.put(
        f"/api/v1/attachs/groups/{attach_group.id}",
        json={"title": "test2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    json_response = response.json()

    assert json_response["id"] == attach_group.id
    assert json_response["title"] == "test2"


async def test_update_attach_group_with_un_existent_id(get_token, ac, session):
    token, user = await get_token(perms=("attach.update",))

    response = await ac.put(
        "/api/v1/attachs/groups/1111",
        json={"title": "test2"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_delete_attach_group_successfully(get_token, ac, session):
    token, user = await get_token(perms=("attach.remove",))

    attach_group = AttachGroup(title="test")
    session.add(attach_group)
    await session.commit()
    await session.refresh(attach_group)

    response = await ac.delete(
        f"/api/v1/attachs/groups/{attach_group.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = await ac.delete(
        f"/api/v1/attachs/groups/{attach_group.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


async def test_create_attach_group_successfully(get_token, ac, session):
    token, user = await get_token(perms=("attach.create",))

    response = await ac.post(
        "/api/v1/attachs/groups",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "test",
        },
    )
    assert response.status_code == 201

    json_response = response.json()

    assert json_response["title"] == "test"
    assert "id" in json_response
