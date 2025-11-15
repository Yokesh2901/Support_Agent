# evaluate.py
# Simple evaluator for demo dataset.
from src.agents.triage_agent import TriageAgent
from src.agents.resolver_agent import ResolverAgent

demo_tickets = [
    {"ticket_id": 1, "text": "I forgot my password"},
    {"ticket_id": 2, "text": "Error 504 when connecting"},
    {"ticket_id": 3, "text": "How do I get a refund on my invoice?"},  # billing -> human
    {"ticket_id": 5, "text": "App throws exception on start"}
]

def evaluate():
    triage = TriageAgent()
    resolver = ResolverAgent()

    triage_correct = 0
    resolvable_count = 0
    resolved_count = 0

    # For demo only: ground truth for triage resolvable (password & diagnostics are resolvable)
    for t in demo_tickets:
        session = {"ticket_id": t["ticket_id"], "text": t["text"]}
        triage_res = triage.process(session)
        is_resolvable = triage_res.get("resolvable", False)
        # ground truth:
        truth_resolvable = any(k in t["text"].lower() for k in ["password", "error", "exception", "fail"])
        if is_resolvable == truth_resolvable:
            triage_correct += 1
        if is_resolvable:
            resolvable_count += 1
            res = resolver.process(session, triage_res)
            if res.get("status") == "resolved":
                resolved_count += 1

    print("Triage accuracy:", triage_correct, "/", len(demo_tickets))
    if resolvable_count:
        print("Automated resolution rate:", resolved_count, "/", resolvable_count)
    else:
        print("No resolvable tickets detected in demo set")

if __name__ == "__main__":
    evaluate()
