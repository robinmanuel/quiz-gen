from app.models.quiz import Quiz
from app.models.question import Question


def test_generate_quiz(client):
    # Register and login
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    # Generate quiz
    r = client.post(
        "/quizzes/generate",
        json={"title": "JS Basics", "topic": "JavaScript"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "JS Basics"
    assert data["topic"] == "JavaScript"
    assert data["owner_id"] > 0
    assert len(data["questions"]) == 5


def test_list_quizzes(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    # Create a quiz
    client.post(
        "/quizzes/generate",
        json={"title": "Quiz 1", "topic": "Topic 1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    r = client.get("/quizzes", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_quiz_by_id(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Quiz 1", "topic": "Topic 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    quiz_id = gen.json()["id"]

    r = client.get(f"/quizzes/{quiz_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["id"] == quiz_id


def test_get_quiz_not_found(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    r = client.get("/quizzes/99999", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404


def test_submit_quiz(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Quiz 1", "topic": "Topic 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    quiz_id = gen.json()["id"]

    # All answers are "A" which is the mocked correct_option
    answers = {str(q["id"]): "A" for q in gen.json()["questions"]}
    r = client.post(
        f"/quizzes/{quiz_id}/submit",
        json={"quiz_id": quiz_id, "answers": answers},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 100
    assert data["correct_answers"] == 5
    assert data["total_questions"] == 5
    assert data["id"] > 0
