# src/agents/technical_agent.py
from src.tools.kb_search import kb_search
from src.tools.run_diagnostic import run_diagnostic

class TechnicalAgent:
    def process(self, session, triage):
        text = session.get("text", "")
        # Attempt KB search first
        kb = kb_search(text)
        if kb["article"]:
            return {"status":"resolved", "message": f"I found this troubleshooting guide:\n\n{kb['summary']}"}

        # Run simulated diagnostics
        diag = run_diagnostic(session.get("ticket_id"))
        if diag.get("ok"):
            return {"status":"resolved", "message": f"I ran diagnostics and applied a fix: {diag.get('fix')}. Please confirm if the issue is resolved."}
        
        # If diagnostics failed
        return {"status":"escalated", "message": "Automatic diagnostics couldn't resolve the issue. Please provide logs and the exact steps to reproduce; I'll escalate this to engineering."}
