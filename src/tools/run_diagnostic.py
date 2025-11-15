# src/tools/run_diagnostic.py
# Simulated diagnostic runner. Replace with actual checks or APIs.

def run_diagnostic(ticket_id):
    # Simulate a check: for demo, ticket_id odd -> success, even -> fail (deterministic)
    try:
        tid = int(ticket_id)
    except Exception:
        tid = 1
    if tid % 2 == 1:
        return {"ok": True, "fix": f"Restarted service for ticket {ticket_id}"}
    else:
        return {"ok": False, "error": "remote-service-unavailable", "code": 503}
