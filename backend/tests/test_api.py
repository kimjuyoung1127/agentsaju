from __future__ import annotations


def test_compile_chart_endpoint(client) -> None:
    response = client.post(
        "/charts/compile",
        json={
            "birth_input": {
                "calendar": "solar",
                "birth_datetime": "1990-10-10T14:30:00+09:00",
                "timezone": "Asia/Seoul",
            }
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["chart_core"]["day_master"] == "Gap"
    assert body["validation_meta"]["normalized_birth_datetime"] == "1990-10-10T14:30:00+09:00"


def test_compile_chart_validation_error(client) -> None:
    response = client.post(
        "/charts/compile",
        json={
            "birth_input": {
                "calendar": "solar",
                "birth_datetime": "1990-10-10T14:30:00+09:00",
                "timezone": "Asia/Seoul",
                "apply_local_mean_time": True,
            }
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_simulation_endpoints(client) -> None:
    create = client.post(
        "/simulations",
        json={
            "birth_input": {
                "calendar": "solar",
                "birth_datetime": "1990-10-10T14:30:00+09:00",
                "timezone": "Asia/Seoul",
            },
            "goal": {"category": "career", "question": "Should I move this year?"},
            "constraints": {"must_avoid": ["debt", "conflict"]},
            "seed": 1024,
            "horizon_year": 2026,
        },
    )
    assert create.status_code == 200
    run_id = create.json()["run_id"]

    run = client.get(f"/simulations/{run_id}")
    assert run.status_code == 200
    run_body = run.json()
    assert run_body["status"] == "completed"
    assert run_body["timeline_mode"] == "monthly"

    events = client.get(f"/simulations/{run_id}/events")
    assert events.status_code == 200
    event_body = events.json()
    assert isinstance(event_body, list)
    assert event_body
    assert all("evidence_refs" in item for item in event_body)
