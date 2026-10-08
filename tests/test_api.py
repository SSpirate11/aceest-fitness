def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"ACEest Fitness" in res.data


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_list_programs(client):
    data = client.get("/api/programs").get_json()
    assert data == {"FL": "Fat Loss", "MG": "Muscle Gain", "BG": "Beginner"}


def test_program_detail_and_404(client):
    assert client.get("/api/programs/mg").get_json()["calorie_factor"] == 35
    assert client.get("/api/programs/XX").status_code == 404


def test_calories_endpoint(client):
    res = client.post("/api/calories", json={"weight": 70, "program": "FL"})
    assert res.get_json() == {"program": "FL", "calories": 1540}


def test_calories_endpoint_validation(client):
    res = client.post("/api/calories", json={"weight": -1, "program": "FL"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_bmi_endpoint(client):
    res = client.post("/api/bmi", json={"weight": 70, "height": 175})
    assert res.get_json() == {"bmi": 22.9, "category": "Normal"}


def test_generate_program_endpoint(client):
    res = client.post("/api/generate-program",
                      json={"program": "MG", "level": "beginner", "seed": 7})
    body = res.get_json()
    assert res.status_code == 200
    assert body["focus"] == "Hypertrophy" and body["days"] == 3


def test_login(client):
    ok = client.post("/api/login", json={"username": "admin", "password": "admin"})
    assert ok.status_code == 200 and ok.get_json()["role"] == "Admin"
    bad = client.post("/api/login", json={"username": "admin", "password": "x"})
    assert bad.status_code == 401


def _create(client, **overrides):
    payload = {"name": "Arjun", "age": 28, "height": 175, "weight": 70,
               "program": "FL", "membership_end": "2099-12-31"}
    payload.update(overrides)
    return client.post("/api/clients", json=payload)


def test_create_and_get_client(client):
    res = _create(client)
    assert res.status_code == 201
    assert res.get_json()["calories"] == 1540
    detail = client.get("/api/clients/Arjun").get_json()
    assert detail["bmi"] == {"value": 22.9, "category": "Normal"}
    assert detail["membership_status"] == "Active"
    assert [c["name"] for c in client.get("/api/clients").get_json()] == ["Arjun"]


def test_create_client_validation(client):
    assert _create(client, name="").status_code == 400
    assert _create(client, program="BAD").status_code == 400
    assert _create(client).status_code == 201
    assert _create(client).status_code == 409


def test_unknown_client_returns_404(client):
    assert client.get("/api/clients/Ghost").status_code == 404
    assert client.get("/api/clients/Ghost/membership").status_code == 404
    assert client.post("/api/clients/Ghost/progress",
                       json={"week": "W1", "adherence": 50}).status_code == 404


def test_progress_tracking(client):
    _create(client)
    assert client.post("/api/clients/Arjun/progress",
                       json={"week": "W1", "adherence": 80}).status_code == 201
    assert client.post("/api/clients/Arjun/progress",
                       json={"week": "W2", "adherence": 150}).status_code == 400
    assert client.get("/api/clients/Arjun/progress").get_json() == [
        {"week": "W1", "adherence": 80}]


def test_workout_logging(client):
    _create(client)
    ok = client.post("/api/clients/Arjun/workouts", json={
        "date": "2026-01-10", "workout_type": "Strength", "duration_min": 60})
    assert ok.status_code == 201
    bad = client.post("/api/clients/Arjun/workouts", json={
        "date": "2026-01-10", "workout_type": "Dancing", "duration_min": 60})
    assert bad.status_code == 400
    history = client.get("/api/clients/Arjun/workouts").get_json()
    assert history[0]["workout_type"] == "Strength"


def test_membership_expired(client):
    _create(client, membership_end="2000-01-01")
    body = client.get("/api/clients/Arjun/membership").get_json()
    assert body["status"] == "Expired"

