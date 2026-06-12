from agents.email_intake_agent import email_intake_agent

test_state = {
    "email_sender": "student@example.com",
    "email_subject": "Internship Application",
    "email_body": "Dear Coordinator, please find my internship application attached.",
    "attachment_paths": ["sample_application.pdf"]
}

result = email_intake_agent(test_state) # type: ignore

print(result)
