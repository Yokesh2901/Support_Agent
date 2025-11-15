# src/agents/escalation_agent.py
class EscalationAgent:
    def process(self, session: dict, triage_result: dict, resolution_attempt: dict) -> dict:
        # Build a structured escalation payload for human agents
        escalation = {
            "ticket_id": session.get("ticket_id"),
            "summary": session.get("text"),
            "triage_intent": triage_result.get("intent"),
            "triage_priority": triage_result.get("priority"),
            "resolution_attempt": resolution_attempt
        }
        # Could also add similar past cases from memory in a fuller system
        return escalation
