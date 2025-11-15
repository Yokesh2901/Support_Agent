# src/agents/order_agent.py
from src.tools.kb_search import kb_search

class OrderAgent:
    def process(self, session, triage):
        text = session.get("text", "").lower()

        if "track" in text or "where is my" in text or "order status" in text:
            res = kb_search("track order")
            message = res["summary"] or "Open Orders > select your order and click Track. If tracking hasn't updated, contact support with your tracking number."
            return {"status":"resolved", "message": f"Order tracking instructions:\n\n{message}"}

        if "cancel" in text:
            return {"status":"escalated", "message": "I can attempt to cancel your order if it hasn't shipped. Please share the order ID and I'll check immediately."}

        if "return" in text:
            return {"status":"escalated", "message": "To start a return, I need your order ID and the reason for return. I will create a return request for the team."}

        return {"status":"escalated", "message": "I couldn't find a direct order action — please provide your order ID and I will escalate."}
