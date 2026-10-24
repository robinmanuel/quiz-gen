def register_and_login(client, username):
    client.post(
        "/auth/register",
        json={
            "email": f"{username}@example.com",
            "username": username,
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/token",
        data={"username": username, "password": "password123"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_public_quizzes_and_leaderboard(client):
    owner_headers = register_and_login(client, "quiz_owner")
    player_headers = register_and_login(client, "quiz_player")

    generated = client.post(
        "/quizzes/generate",
        json={
            "title": "Python Lists",
            "topic": "Python lists",
            "quiz_type": "niche",
        },
        headers=owner_headers,
    )
    assert generated.status_code == 200
    quiz = generated.json()
    assert quiz["is_public"] is False

    public_quizzes = client.get("/quizzes/public")
    assert public_quizzes.status_code == 200
    assert public_quizzes.json() == []

    shared = client.patch(
        f"/quizzes/{quiz['id']}/share",
        json={"is_public": True},
        headers=owner_headers,
    )
    assert shared.status_code == 200
    assert shared.json()["is_public"] is True

    public_quizzes = client.get("/quizzes/public")
    assert public_quizzes.status_code == 200
    assert public_quizzes.json()[0]["owner_username"] == "quiz_owner"
    assert public_quizzes.json()[0]["question_count"] == 8

    public_quiz = client.get(f"/quizzes/{quiz['id']}", headers=player_headers)
    assert public_quiz.status_code == 404
    shared_quiz = client.get(f"/quizzes/shared/{quiz['id']}")
    assert shared_quiz.status_code == 200
    assert "correct_option" not in shared_quiz.json()["questions"][0]
    assert "explanation" not in shared_quiz.json()["questions"][0]
    assert len(shared_quiz.json()["questions"]) == 8
    public_quiz = client.get(f"/quizzes/{quiz['id']}", headers=owner_headers)
    assert public_quiz.status_code == 200
    answers = {str(question["id"]): "A" for question in public_quiz.json()["questions"]}
    submitted = client.post(
        f"/quizzes/{quiz['id']}/submit",
        json={"quiz_id": quiz["id"], "answers": answers},
        headers=player_headers,
    )
    assert submitted.status_code == 200
    assert len(submitted.json()["review"]) == 8

    lower_score = client.post(
        f"/quizzes/{quiz['id']}/submit",
        json={
            "quiz_id": quiz["id"],
            "answers": {str(question["id"]): "B" for question in public_quiz.json()["questions"]},
        },
        headers=player_headers,
    )
    assert lower_score.status_code == 200

    leaderboard = client.get("/quizzes/leaderboard")
    assert leaderboard.status_code == 200
    assert leaderboard.json()[0]["username"] == "quiz_player"
    assert leaderboard.json()[0]["best_score"] == 100
    assert leaderboard.json()[0]["quiz_title"] == "Python Lists"

    unshared = client.patch(
        f"/quizzes/{quiz['id']}/share",
        json={"is_public": False},
        headers=owner_headers,
    )
    assert unshared.status_code == 200
    assert client.get("/quizzes/public").json() == []
    assert client.get(f"/quizzes/shared/{quiz['id']}").status_code == 404
    assert client.get(f"/quizzes/{quiz['id']}", headers=player_headers).status_code == 404
    assert client.get("/quizzes/leaderboard").json() == []


def test_only_quiz_owner_can_change_sharing(client):
    owner_headers = register_and_login(client, "owner")
    other_headers = register_and_login(client, "other")
    generated = client.post(
        "/quizzes/generate",
        json={
            "title": "Private",
            "topic": "Private topic",
            "quiz_type": "general",
        },
        headers=owner_headers,
    )

    response = client.patch(
        f"/quizzes/{generated.json()['id']}/share",
        json={"is_public": True},
        headers=other_headers,
    )
    assert response.status_code == 404
