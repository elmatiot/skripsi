def test_register_and_login(client):
    payload = {"email": "test@example.com", "nama": "Tester", "password": "rahasia123"}
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    assert token

    r2 = client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    assert r2.json()["user"]["email"] == payload["email"]


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
