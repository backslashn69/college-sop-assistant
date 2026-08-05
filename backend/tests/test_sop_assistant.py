import pytest
from fastapi.testclient import TestClient

from document_service import (
    build_sop_chunks,
    load_all_sops,
)
from main import app
from retrieval_service import (
    build_precise_answer,
    find_best_sop_chunks,
)


@pytest.fixture(scope="module")
def sop_chunks() -> list[dict[str, str | int]]:
    """
    Load and section the real SOP documents once
    for all tests in this file.
    """
    sop_pages = load_all_sops()
    chunks = build_sop_chunks(sop_pages)

    assert chunks, (
        "No SOP chunks were created. "
        "Check backend/data/sops."
    )

    return chunks


def retrieve_answer(
    question: str,
    sop_chunks: list[dict[str, str | int]],
) -> tuple[
    list[dict[str, str | int]],
    str,
]:
    """
    Retrieve the strongest SOP sections and create
    the deterministic answer used by the backend.
    """
    matching_chunks = find_best_sop_chunks(
        question,
        sop_chunks,
    )

    assert matching_chunks, (
        f"No SOP section was retrieved for: "
        f"{question}"
    )

    answer = build_precise_answer(
        question,
        matching_chunks,
    )

    assert answer, (
        f"No answer was generated for: "
        f"{question}"
    )

    return matching_chunks, answer


def test_access_workday(
    sop_chunks: list[dict[str, str | int]],
) -> None:
    matching_chunks, answer = retrieve_answer(
        "How do I access Workday?",
        sop_chunks,
    )

    assert matching_chunks[0]["title"] == (
        "Step 1: Access Workday"
    )

    assert "Open Workday" in answer
    assert "Bookmark the page." in answer
    assert "Log in using NJIT credentials." in answer


def test_salaried_employee_time_off(
    sop_chunks: list[dict[str, str | int]],
) -> None:
    matching_chunks, answer = retrieve_answer(
        (
            "How do salaried employees "
            "request time off?"
        ),
        sop_chunks,
    )

    assert matching_chunks[0]["title"] == (
        "Step 5: Request Time Off"
    )

    assert "Salaried Employees:" in answer

    assert (
        "Submit all leave requests "
        "directly in Workday."
        in answer
    )

    assert (
        "View leave balances in Workday."
        in answer
    )

    assert (
        "Bi-weekly Banner leave reports "
        "for salaried employees are no longer used."
        in answer
    )


def test_delegation_procedure(
    sop_chunks: list[dict[str, str | int]],
) -> None:
    matching_chunks, answer = retrieve_answer(
        "How do I set up delegation?",
        sop_chunks,
    )

    primary_chunk = matching_chunks[0]

    assert primary_chunk["title"] == (
        "Step 9: Set Up Delegation"
    )

    assert primary_chunk["page_start"] == 5
    assert primary_chunk["page_end"] == 6

    expected_steps = [
        "1. Open Delegation in Workday.",
        "2. Select delegation dates.",
        "3. Choose the delegate.",
        (
            "4. Select either specific tasks "
            "or the entire inbox."
        ),
        "5. Submit.",
        "6. Supervisor approves delegation.",
    ]

    for expected_step in expected_steps:
        assert expected_step in answer

    assert (
        "Delegating the entire inbox provides "
        "access to all incoming items"
        in answer
    )

    assert "Choose delegates carefully." in answer


def test_support_order(
    sop_chunks: list[dict[str, str | int]],
) -> None:
    matching_chunks, answer = retrieve_answer(
        "What is the support order?",
        sop_chunks,
    )

    assert matching_chunks[0]["title"] == (
        "Step 10: Seek Support"
    )

    expected_items = [
        "Search Workday.",
        "Search Nexus Knowledge Base.",
        "Use Hypercare Zoom Room.",
        "Visit IST Service Desk.",
        "Contact Help Desk.",
        "Subject Matter Experts (SMEs).",
    ]

    positions: list[int] = []

    for expected_item in expected_items:
        assert expected_item in answer
        positions.append(
            answer.index(expected_item)
        )

    assert positions == sorted(positions), (
        "The support levels are not in the "
        "correct SOP order."
    )


def test_incorrect_physical_work_location(
    sop_chunks: list[dict[str, str | int]],
) -> None:
    _, answer = retrieve_answer(
        (
            "What should I do if my physical "
            "work location is incorrect?"
        ),
        sop_chunks,
    )

    assert answer == (
        "Notify your manager if your "
        "physical work location is incorrect."
    )


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_delegation_chat_endpoint() -> None:
    """
    This procedure uses deterministic generation,
    so the test does not make an external Groq call.
    """
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "question": (
                "How do I set up delegation?"
            ),
        },
    )

    assert response.status_code == 200

    response_body = response.json()

    assert (
        "Select either specific tasks "
        "or the entire inbox."
        in response_body["answer"]
    )

    assert (
        "Step 9: Set Up Delegation"
        in response_body["source"]
    )

    assert (
        "Pages 5-6"
        in response_body["source"]
    )