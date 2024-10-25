async def test_successful_login(ac, session, create_user):
    await create_user("test_successful_login", "test_successful_login")
    response = await ac.post(
        "/api/v1/login",
        data={"username": "test_successful_login", "password": "test_successful_login"},
    )

    assert response.status_code == 200

    json_response = response.json()

    assert json_response["access_token"]
    assert json_response["token_type"] == "bearer"


async def test_failed_login(ac):
    response = await ac.post(
        "/api/v1/login", data={"username": "test", "password": "wrong"}
    )

    assert response.status_code == 401
