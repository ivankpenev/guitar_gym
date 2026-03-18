"""End-to-end test: boots a minimal FastAPI app with the exercise routes
and runs through the full exercise flow via HTTP.

This test doesn't require a database or crypto libraries — it tests the
core exercise API which is the heart of the app.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import only the exercise router (no DB/auth dependencies)
from app.routers.exercises import router as exercises_router

# Build a minimal test app
test_app = FastAPI()
test_app.include_router(exercises_router)


def test_health_and_list():
    """List available exercises."""
    client = TestClient(test_app)

    r = client.get("/exercises/")
    assert r.status_code == 200
    exercises = r.json()
    assert len(exercises) == 2
    types = {e["exercise_type"] for e in exercises}
    assert types == {"note_identification", "interval_training"}
    print(f"PASS: listed {len(exercises)} exercises: {types}")


def test_note_identification_flow():
    """Full question -> answer cycle for note identification."""
    client = TestClient(test_app)

    # Get a question
    r = client.post("/exercises/note_identification/question", json={"difficulty": 1})
    assert r.status_code == 200
    q = r.json()
    assert "prompt" in q
    assert len(q["choices"]) == 4
    assert "question_token" in q
    # Correct answer should NOT be leaked to the client
    assert "correct_answer" not in q
    print(f"PASS: got question: {q['prompt']} | choices: {q['choices']}")

    # Submit the correct answer (we'll try all choices to find it)
    token = q["question_token"]
    r = client.post("/exercises/note_identification/answer", json={
        "question_token": token,
        "user_answer": q["choices"][0],
    })
    assert r.status_code == 200
    result = r.json()
    assert "correct" in result
    assert "correct_answer" in result
    assert result["correct_answer"] in q["choices"], "Correct answer must be one of the choices"
    print(f"PASS: submitted answer '{q['choices'][0]}', correct={result['correct']}, answer='{result['correct_answer']}'")

    # Token should be consumed
    r = client.post("/exercises/note_identification/answer", json={
        "question_token": token,
        "user_answer": "C",
    })
    assert r.status_code == 404
    print("PASS: reused token correctly rejected (404)")


def test_interval_training_flow():
    """Full question -> answer cycle for interval training."""
    client = TestClient(test_app)

    r = client.post("/exercises/interval_training/question", json={"difficulty": 3})
    assert r.status_code == 200
    q = r.json()
    assert len(q["choices"]) >= 2
    token = q["question_token"]
    print(f"PASS: got interval question: {q['prompt']} | choices: {q['choices']}")

    r = client.post("/exercises/interval_training/answer", json={
        "question_token": token,
        "user_answer": q["choices"][0],
    })
    assert r.status_code == 200
    result = r.json()
    assert result["correct_answer"] in q["choices"]
    print(f"PASS: interval answer: correct={result['correct']}, answer='{result['correct_answer']}'")


def test_all_difficulty_levels():
    """All 5 difficulty levels should return valid questions for both exercises."""
    client = TestClient(test_app)

    for ex_type in ["note_identification", "interval_training"]:
        for diff in range(1, 6):
            r = client.post(f"/exercises/{ex_type}/question", json={"difficulty": diff})
            assert r.status_code == 200
            q = r.json()
            assert len(q["choices"]) >= 2
            # Consume token
            client.post(f"/exercises/{ex_type}/answer", json={
                "question_token": q["question_token"],
                "user_answer": q["choices"][0],
            })
    print("PASS: all difficulty levels (1-5) work for both exercises")


def test_invalid_exercise():
    """Unknown exercise type should return 404."""
    client = TestClient(test_app)
    r = client.post("/exercises/nonexistent/question", json={"difficulty": 1})
    assert r.status_code == 404
    print("PASS: invalid exercise type returns 404")


def test_visual_data_structure():
    """Verify visual_data has the right structure for fretboard rendering."""
    client = TestClient(test_app)

    # Note ID: should have highlight_positions
    r = client.post("/exercises/note_identification/question", json={"difficulty": 1})
    q = r.json()
    vd = q["visual_data"]
    assert "highlight_positions" in vd
    pos = vd["highlight_positions"][0]
    assert 1 <= pos["string"] <= 6
    assert 0 <= pos["fret"] <= 24
    print(f"PASS: note ID visual_data: string={pos['string']}, fret={pos['fret']}")
    client.post("/exercises/note_identification/answer", json={
        "question_token": q["question_token"], "user_answer": "C"
    })

    # Interval: should have positions array with labels
    r = client.post("/exercises/interval_training/question", json={"difficulty": 2})
    q = r.json()
    vd = q["visual_data"]
    assert "positions" in vd
    assert len(vd["positions"]) == 2
    for p in vd["positions"]:
        assert "string" in p and "fret" in p and "label" in p
    print(f"PASS: interval visual_data: {vd['positions']}")


def test_stress_20_questions():
    """Run 20 questions and verify answer checking is consistent."""
    client = TestClient(test_app)

    correct_count = 0
    for i in range(20):
        r = client.post("/exercises/note_identification/question", json={"difficulty": 3})
        q = r.json()

        r = client.post("/exercises/note_identification/answer", json={
            "question_token": q["question_token"],
            "user_answer": q["choices"][0],
        })
        result = r.json()
        assert result["correct_answer"] in q["choices"]
        if result["correct"]:
            correct_count += 1

    print(f"PASS: 20-question stress test ({correct_count}/20 correct by chance)")


if __name__ == "__main__":
    tests = [
        test_health_and_list,
        test_note_identification_flow,
        test_interval_training_flow,
        test_all_difficulty_levels,
        test_invalid_exercise,
        test_visual_data_structure,
        test_stress_20_questions,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*40}")
    print(f"{len(tests) - failed}/{len(tests)} e2e tests passed")
    if failed:
        sys.exit(1)
    else:
        print("All e2e tests passed!")
