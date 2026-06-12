from graph.internship_graph import build_internship_graph


internship_graph = build_internship_graph()


TEST_CASES = [
    {
        "name": "Valid Application",
        "attachment_path": "sample_files/sample_application.pdf",
        "expected_recommendation": "APPROVE"
    },
    {
        "name": "Incomplete Application",
        "attachment_path": "sample_files/sample_incomplete_application.pdf",
        "expected_recommendation": "REQUEST_CLARIFICATION"
    },
    {
        "name": "Rule Violation Application",
        "attachment_path": "sample_files/sample_rule_violation_application.pdf",
        "expected_recommendation": "REJECT_OR_CLARIFY"
    },
    {
        "name": "Ambiguous Application",
        "attachment_path": "sample_files/sample_ambiguous_application.pdf",
        "expected_recommendation": "WAIT_FOR_SUPERVISOR_RESPONSE"
    }
]


def run_test_case(test_case: dict):
    initial_state = {
        "email_sender": "student@example.com",
        "email_subject": test_case["name"],
        "email_body": "Dear Coordinator, please find attached.",
        "attachment_paths": [test_case["attachment_path"]],
        "missing_fields": [],
        "rule_violations": [],
        "clarification_needed": False,
        "supervisor_verification_needed": False,
        "audit_log": []
    }

    result = internship_graph.invoke(initial_state)

    actual = result.get("recommendation")
    expected = test_case["expected_recommendation"]

    passed = actual == expected

    print("=" * 80)
    print(f"Test Case: {test_case['name']}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Passed:   {passed}")
    print(f"Missing Fields: {result.get('missing_fields')}")
    print(f"Rule Violations: {result.get('rule_violations')}")
    print(f"Reason: {result.get('recommendation_reason')}")


def run_all_tests():
    passed_count = 0

    for test_case in TEST_CASES:
        initial_state = {
            "email_sender": "student@example.com",
            "email_subject": test_case["name"],
            "email_body": "Dear Coordinator, please find attached.",
            "attachment_paths": [test_case["attachment_path"]],
            "missing_fields": [],
            "rule_violations": [],
            "clarification_needed": False,
            "supervisor_verification_needed": False,
            "audit_log": []
        }

        result = internship_graph.invoke(initial_state)

        actual = result.get("recommendation")
        expected = test_case["expected_recommendation"]

        passed = actual == expected

        if passed:
            passed_count += 1

        print("=" * 80)
        print(f"Test Case: {test_case['name']}")
        print(f"Expected: {expected}")
        print(f"Actual:   {actual}")
        print(f"Passed:   {passed}")
        print(f"Missing Fields: {result.get('missing_fields')}")
        print(f"Rule Violations: {result.get('rule_violations')}")
        print(f"Reason: {result.get('recommendation_reason')}")

    print("=" * 80)
    print(f"TOTAL PASSED: {passed_count}/{len(TEST_CASES)}")


if __name__ == "__main__":
    run_all_tests()
