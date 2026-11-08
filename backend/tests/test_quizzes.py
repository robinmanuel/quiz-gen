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


def test_generate_quiz_custom_question_count(client):
    client.post(
        "/auth/register",
        json={"email": "counter@example.com", "username": "counter", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "counter", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request 5 questions
    r = client.post(
        "/quizzes/generate",
        json={"title": "Custom Count", "topic": "Science", "quiz_type": "general", "num_questions": 5},
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()["questions"]) == 5

    # Request 1 question (minimum)
    r2 = client.post(
        "/quizzes/generate",
        json={"title": "Single Q", "topic": "Science", "quiz_type": "general", "num_questions": 1},
        headers=headers,
    )
    assert r2.status_code == 200
    assert len(r2.json()["questions"]) == 1

    # 21 questions should fail validation
    r3 = client.post(
        "/quizzes/generate",
        json={"title": "Too Many", "topic": "Science", "quiz_type": "general", "num_questions": 21},
        headers=headers,
    )
    assert r3.status_code == 422

    # 0 questions should fail validation
    r4 = client.post(
        "/quizzes/generate",
        json={"title": "Zero", "topic": "Science", "quiz_type": "general", "num_questions": 0},
        headers=headers,
    )
    assert r4.status_code == 422


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


def test_update_quiz(client):
    client.post(
        "/auth/register",
        json={"email": "updater@example.com", "username": "updater", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "updater", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Old Title", "topic": "Old Topic", "quiz_type": "general"},
        headers=headers,
    )
    quiz_id = gen.json()["id"]

    # Partial update: title only
    patch1 = client.patch(
        f"/quizzes/{quiz_id}",
        json={"title": "New Title"},
        headers=headers,
    )
    assert patch1.status_code == 200
    assert patch1.json()["title"] == "New Title"
    assert patch1.json()["topic"] == "Old Topic"

    # Multi-field update: topic and quiz_type
    patch2 = client.patch(
        f"/quizzes/{quiz_id}",
        json={"topic": "New Topic", "quiz_type": "niche"},
        headers=headers,
    )
    assert patch2.status_code == 200
    assert patch2.json()["title"] == "New Title"
    assert patch2.json()["topic"] == "New Topic"
    assert patch2.json()["quiz_type"] == "niche"


def test_update_quiz_unauthorized_and_validation(client):
    client.post(
        "/auth/register",
        json={"email": "user1@example.com", "username": "user1", "password": "password123"},
    )
    login1 = client.post(
        "/auth/token",
        data={"username": "user1", "password": "password123"},
    )
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    gen = client.post(
        "/quizzes/generate",
        json={"title": "User1 Quiz", "topic": "Tech", "quiz_type": "general"},
        headers=headers1,
    )
    quiz_id = gen.json()["id"]

    # Other user cannot update
    client.post(
        "/auth/register",
        json={"email": "user2@example.com", "username": "user2", "password": "password123"},
    )
    login2 = client.post(
        "/auth/token",
        data={"username": "user2", "password": "password123"},
    )
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    res_forbidden = client.patch(
        f"/quizzes/{quiz_id}",
        json={"title": "Hacked Title"},
        headers=headers2,
    )
    assert res_forbidden.status_code == 404

    # Validation failure: empty title
    res_invalid = client.patch(
        f"/quizzes/{quiz_id}",
        json={"title": ""},
        headers=headers1,
    )
    assert res_invalid.status_code == 422


def test_list_and_get_user_attempts(client):
    # Register and login user A
    client.post(
        "/auth/register",
        json={"email": "attempt_tester@example.com", "username": "attempter", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "attempter", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Before submitting any attempts, list should be empty
    empty_attempts = client.get("/quizzes/attempts", headers=headers)
    assert empty_attempts.status_code == 200
    assert empty_attempts.json() == []

    # Generate a quiz
    gen = client.post(
        "/quizzes/generate",
        json={"title": "Geography", "topic": "Capitals", "quiz_type": "general"},
        headers=headers,
    )
    quiz = gen.json()
    quiz_id = quiz["id"]

    # Submit an attempt
    answers = {str(q["id"]): "A" for q in quiz["questions"]}
    submit_res = client.post(
        f"/quizzes/{quiz_id}/submit",
        json={"quiz_id": quiz_id, "answers": answers},
        headers=headers,
    )
    assert submit_res.status_code == 200
    attempt_id = submit_res.json()["id"]

    # List attempts - should now contain 1 item
    list_res = client.get("/quizzes/attempts", headers=headers)
    assert list_res.status_code == 200
    attempts_data = list_res.json()
    assert len(attempts_data) == 1
    assert attempts_data[0]["id"] == attempt_id
    assert attempts_data[0]["quiz_id"] == quiz_id
    assert attempts_data[0]["quiz_title"] == "Geography"
    assert attempts_data[0]["quiz_topic"] == "Capitals"
    assert attempts_data[0]["score"] == 100
    assert attempts_data[0]["correct_answers"] == 8
    assert attempts_data[0]["total_questions"] == 8

    # Get single attempt detail
    detail_res = client.get(f"/quizzes/attempts/{attempt_id}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == attempt_id
    assert detail["quiz_title"] == "Geography"
    assert len(detail["review"]) == 8
    assert detail["review"][0]["correct_option"] == "A"
    assert "explanation" in detail["review"][0]

    # Non-existent attempt returns 404
    missing_res = client.get("/quizzes/attempts/999999", headers=headers)
    assert missing_res.status_code == 404

    # Other user cannot see this attempt
    client.post(
        "/auth/register",
        json={"email": "snooper@example.com", "username": "snooper", "password": "password123"},
    )
    login_snooper = client.post(
        "/auth/token",
        data={"username": "snooper", "password": "password123"},
    )
    token_snooper = login_snooper.json()["access_token"]
    snoop_res = client.get(
        f"/quizzes/attempts/{attempt_id}",
        headers={"Authorization": f"Bearer {token_snooper}"},
    )
    assert snoop_res.status_code == 404


def test_export_quiz_json_and_csv(client):
    client.post(
        "/auth/register",
        json={"email": "exporter@example.com", "username": "exporter", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "exporter", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Export Me", "topic": "Physics", "quiz_type": "general", "num_questions": 2},
        headers=headers,
    )
    quiz_id = gen.json()["id"]

    # Export JSON
    res_json = client.get(f"/quizzes/{quiz_id}/export?format=json", headers=headers)
    assert res_json.status_code == 200
    assert "application/json" in res_json.headers["content-type"]
    exported_data = res_json.json()
    assert exported_data["title"] == "Export Me"
    assert len(exported_data["questions"]) == 2

    # Export CSV
    res_csv = client.get(f"/quizzes/{quiz_id}/export?format=csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "question_text,option_a,option_b,option_c,option_d,correct_option,explanation" in res_csv.text

    # Invalid format returns 400
    res_bad = client.get(f"/quizzes/{quiz_id}/export?format=xml", headers=headers)
    assert res_bad.status_code == 400


def test_admin_delete_quiz_rbac(client):
    from app.main import app
    from app.database import get_db
    from app.models.user import User

    # Regular user creates a quiz
    client.post(
        "/auth/register",
        json={"email": "regular@example.com", "username": "regular", "password": "password123"},
    )
    login_reg = client.post(
        "/auth/token",
        data={"username": "regular", "password": "password123"},
    )
    headers_reg = {"Authorization": f"Bearer {login_reg.json()['access_token']}"}

    gen = client.post(
        "/quizzes/generate",
        json={"title": "Public Spam", "topic": "Spam", "quiz_type": "general"},
        headers=headers_reg,
    )
    quiz_id = gen.json()["id"]

    # Non-admin user cannot call admin delete endpoint
    client.post(
        "/auth/register",
        json={"email": "nonadmin@example.com", "username": "nonadmin", "password": "password123"},
    )
    login_nonadmin = client.post(
        "/auth/token",
        data={"username": "nonadmin", "password": "password123"},
    )
    headers_nonadmin = {"Authorization": f"Bearer {login_nonadmin.json()['access_token']}"}

    forbidden = client.delete(f"/quizzes/admin/{quiz_id}", headers=headers_nonadmin)
    assert forbidden.status_code == 403

    # Promote 'nonadmin' to admin in the test DB and retry
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    admin_user = db.query(User).filter(User.username == "nonadmin").first()
    admin_user.is_admin = True
    db.commit()
    db.close()

    ok = client.delete(f"/quizzes/admin/{quiz_id}", headers=headers_nonadmin)
    assert ok.status_code == 204
    assert client.get(f"/quizzes/{quiz_id}", headers=headers_reg).status_code == 404




