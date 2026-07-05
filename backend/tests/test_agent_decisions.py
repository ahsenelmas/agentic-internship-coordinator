from graph.internship_graph import build_internship_graph

graph = build_internship_graph()


def test_valid_application_returns_decision():
    case_data = {
        "email_sender": "student@example.com",
        "email_subject": "Internship Application",
        "email_body": """
        Student Name: Ayse Yilmaz
        Student ID: 123456
        Company Name: ABC Tech
        Supervisor Name: John Smith
        Supervisor Email: john@abctech.com
        Internship Start Date: 2026-07-01
        Internship End Date: 2026-08-15
        """,
        "attachment_paths": []
    }

    result = graph.invoke(case_data)#type: ignore

    assert "recommendation" in result
    assert result["recommendation"] in [
        "APPROVE",
        "REQUEST_CLARIFICATION",
        "REJECT_OR_CLARIFY"
    ]


def test_incomplete_application_requests_clarification():
    case_data = {
        "email_sender": "student@example.com",
        "email_subject": "Internship Application",
        "email_body": """
        Student Name: Ayse Yilmaz
        Student ID: 123456
        Company Name: ABC Tech
        Internship Start Date: 2026-07-01
        Internship End Date: 2026-08-15
        """,
        "attachment_paths": []
    }

    result = graph.invoke(case_data)#type: ignore

    assert "recommendation" in result
    assert result["recommendation"] in [
        "REQUEST_CLARIFICATION",
        "REJECT_OR_CLARIFY"
    ]


def test_empty_application_does_not_crash():
    case_data = {
        "email_sender": "",
        "email_subject": "",
        "email_body": "",
        "attachment_paths": []
    }

    result = graph.invoke(case_data)#type: ignore

    assert isinstance(result, dict)
    assert "recommendation" in result