# tests/test_triage.py
from src.agents.triage_agent import TriageAgent

def test_password_triage():
    triage = TriageAgent()
    session = {"text": "I forgot my password and can't login"}
    result = triage.process(session)
    assert result["resolvable"] is True
    assert result["intent"] == "password_reset"

def test_billing_triage():
    triage = TriageAgent()
    session = {"text": "I have a question about my invoice"}
    result = triage.process(session)
    assert result["resolvable"] is False
    assert result["intent"] == "billing"
