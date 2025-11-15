# src/agents/product_agent.py
from src.tools.kb_search import kb_search

class ProductAgent:
    def process(self, session, triage):
        text = session.get("text", "")
        res = kb_search(text)
        if res["article"]:
            return {"status":"resolved", "message": f"Here's a short guide:\n\n{res['summary']}"}
        return {"status":"escalated", "message":"I don't have a quick guide for that exact workflow. Tell me which feature you mean and I will escalate to product support with examples."}
