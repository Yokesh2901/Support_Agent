from src.agents.triage_agent import TriageAgent

def test_password_triage():
    triage = TriageAgent()
    result = triage.process({"text": "I forgot my password and can't login"})
    assert result["intent"] == "password_reset"
    assert result["secondary_intents"] == ["login_issue"]

def test_billing_triage():
    triage = TriageAgent()
    result = triage.process({"text": "I have a question about my invoice"})
    assert result["intent"] == "invoice_request"
    assert result["secondary_intents"] == []

def test_unknown_triage_escalates():
    triage = TriageAgent()
    result = triage.process({"text": "Something completely unexpected happened"})
    assert result["intent"] == "human_support"

def test_multiple_intents():
    triage = TriageAgent()
    result = triage.process({"text": "I forgot my password and my payment failed"})
    assert result["intent"] == "password_reset"
    assert "payment_failed" in result["secondary_intents"]
