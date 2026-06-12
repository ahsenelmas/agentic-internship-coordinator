from langgraph.graph import StateGraph, END

from models.case_state import InternshipCaseState

from agents.email_intake_agent import email_intake_agent
from agents.document_extraction_agent import document_extraction_agent
from agents.completeness_validation_agent import completeness_validation_agent
from agents.university_rules_agent import university_rules_agent
from agents.supervisor_verification_agent import supervisor_verification_agent
from agents.decision_recommendation_agent import decision_recommendation_agent


def route_after_completeness(state: InternshipCaseState) -> str:
    if state.get("clarification_needed"):
        return "decision"
    return "rules"


def route_after_rules(state: InternshipCaseState) -> str:
    if state.get("rule_violations"):
        return "decision"
    return "supervisor"


def build_internship_graph():
    workflow = StateGraph(InternshipCaseState)

    workflow.add_node("email_intake", email_intake_agent)
    workflow.add_node("document_extraction", document_extraction_agent)
    workflow.add_node("completeness_validation", completeness_validation_agent)
    workflow.add_node("university_rules", university_rules_agent)
    workflow.add_node("supervisor_verification", supervisor_verification_agent)
    workflow.add_node("decision_recommendation", decision_recommendation_agent)

    workflow.set_entry_point("email_intake")

    workflow.add_edge("email_intake", "document_extraction")
    workflow.add_edge("document_extraction", "completeness_validation")

    workflow.add_conditional_edges(
        "completeness_validation",
        route_after_completeness,
        {
            "decision": "decision_recommendation",
            "rules": "university_rules"
        }
    )

    workflow.add_conditional_edges(
        "university_rules",
        route_after_rules,
        {
            "decision": "decision_recommendation",
            "supervisor": "supervisor_verification"
        }
    )

    workflow.add_edge("supervisor_verification", "decision_recommendation")
    workflow.add_edge("decision_recommendation", END)

    return workflow.compile()
