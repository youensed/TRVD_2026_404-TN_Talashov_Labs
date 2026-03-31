from __future__ import annotations


async def test_register_sets_cookies_and_returns_current_user(client):  # noqa: ANN001
    response = await client.post(
        "/auth/register",
        json={
            "email": "new-patient@example.com",
            "password": "Secret123!",
            "first_name": "Ірина",
            "last_name": "Новак",
            "phone": "+380670000001",
        },
    )

    assert response.status_code == 201
    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies
    assert "csrf_token" in client.cookies

    me_response = await client.get("/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "new-patient@example.com"

