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
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Generate quiz
    r = client.post(
        "/quizzes/generate",
        json={"title": "JS Basics", "topic": "JavaScript", "quiz_type": "niche"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "JS Basics"
    assert data["topic"] == "JavaScript"
    assert data["quiz_type"] == "niche"
    assert data["owner_id"] > 0
    assert len(data["questions"]) == 8


def test_create_manual_quiz(client):
    client.post(
        "/auth/register",
        json={"email": "author@example.com", "username": "author", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "author", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}
    payload = {
        "title": "My Python Quiz",
        "topic": "Python",
        "quiz_type": "niche",
        "questions": [
            {
                "question_text": "Which type is immutable?",
                "option_a": "list",
                "option_b": "dict",
                "option_c": "tuple",
                "option_d": "set",
                "correct_option": "C",
                "explanation": "A tuple cannot be modified after creation.",
            }
        ],
    }

    response = client.post("/quizzes/", json=payload, headers=headers)

    assert response.status_code == 200
    quiz = response.json()
    assert quiz["title"] == "My Python Quiz"
    assert quiz["quiz_type"] == "niche"
    assert quiz["is_public"] is False
    assert len(quiz["questions"]) == 1
    assert quiz["questions"][0]["correct_option"] == "C"


def test_generate_quiz_from_source_material(client):
    client.post(
        "/auth/register",
        json={"email": "source@example.com", "username": "source", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "source", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}

    response = client.post(
        "/quizzes/generate",
        json={
            "title": "Study Notes Quiz",
            "topic": "Plant biology",
            "quiz_type": "general",
            "source_text": "Chlorophyll is a green pigment in plants.",
        },
        headers=headers,
    )

    assert response.status_code == 200
    quiz = response.json()
    assert quiz["questions"][0]["question_text"] == "What detail appears in the source?"
    assert quiz["is_public"] is False


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
        json={"title": "Quiz 1", "topic": "Topic 1", "quiz_type": "general"},
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
        json={"title": "Quiz 1", "topic": "Topic 1", "quiz_type": "general"},
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
        json={"title": "Quiz 1", "topic": "Topic 1", "quiz_type": "general"},
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
    assert data["correct_answers"] == 8
    assert data["total_questions"] == 8
    assert data["id"] > 0


def test_delete_quiz(client):
    # Register and login owner
    client.post(
        "/auth/register",
        json={"email": "owner@example.com", "username": "owner", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "owner", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a quiz
    gen = client.post(
        "/quizzes/generate",
        json={"title": "To Delete", "topic": "Testing", "quiz_type": "general"},
        headers=headers,
    )
    quiz_id = gen.json()["id"]

    # Submit an attempt so attempts exist for this quiz
    client.post(
        f"/quizzes/{quiz_id}/submit",
        json={"quiz_id": quiz_id, "answers": {}},
        headers=headers,
    )

    # Delete the quiz
    delete_res = client.delete(f"/quizzes/{quiz_id}", headers=headers)
    assert delete_res.status_code == 204

    # Quiz should no longer exist
    get_res = client.get(f"/quizzes/{quiz_id}", headers=headers)
    assert get_res.status_code == 404

    # Quiz should no longer be listed in user's quizzes
    list_res = client.get("/quizzes/", headers=headers)
    assert not any(q["id"] == quiz_id for q in list_res.json())


def test_delete_quiz_forbidden_or_not_found_for_other_user(client):
    # Register owner and create quiz
    client.post(
        "/auth/register",
        json={"email": "alice@example.com", "username": "alice", "password": "password123"},
    )
    login_alice = client.post(
        "/auth/token",
        data={"username": "alice", "password": "password123"},
    )
    token_alice = login_alice.json()["access_token"]

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Alice Quiz", "topic": "Math", "quiz_type": "general"},
        headers={"Authorization": f"Bearer {token_alice}"},
    )
    quiz_id = gen.json()["id"]

    # Register eve and attempt to delete alice's quiz
    client.post(
        "/auth/register",
        json={"email": "eve@example.com", "username": "eve", "password": "password123"},
    )
    login_eve = client.post(
        "/auth/token",
        data={"username": "eve", "password": "password123"},
    )
    token_eve = login_eve.json()["access_token"]

    delete_res = client.delete(
        f"/quizzes/{quiz_id}",
        headers={"Authorization": f"Bearer {token_eve}"},
    )
    assert delete_res.status_code == 404

