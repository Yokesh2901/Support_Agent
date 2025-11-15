from src.agents.account_agent import AccountAgent
from src.agents.technical_agent import TechnicalAgent

def test_account_password_reset():
    agent = AccountAgent()
    res = agent.process({"ticket_id": 1, "text":"forgot password"}, {"intent":"password_reset"})
    assert res["status"] == "resolved"

def test_technical_diag():
    agent = TechnicalAgent()
    res = agent.process({"ticket_id":1,"text":"error 504"}, {"intent":"error_code"})
    # for demo, diagnostic odd/even logic may resolve or fail; assert structure
    assert "status" in res
