# src/agents/billing_agent.py
from src.tools.kb_search import kb_search

class BillingAgent:
    def process(self, session, triage):
        text = session.get("text", "").lower()

        if "invoice" in text or "receipt" in text:
            res = kb_search("invoice")
            message = res["summary"] or "You can download invoices from Account > Billing > Invoices."
            return {"status":"resolved", "message": f"You can download your invoice like this:\n\n{message}"}

        if "refund" in text:
            # Refunds require human review but give exact template and steps
            template = (
                "I can help start a refund request. Please provide:\n"
                "1) Order ID\n2) Amount to refund\n3) Reason for refund\n\nOnce you provide these, I will create a refund request for the billing team."
            )
            return {"status":"escalated", "message": template}

        if "payment" in text or "card" in text:
            res = kb_search("payment failed")
            message = res["summary"] or "Check card expiry, CVV, and billing address. Try another payment method if possible."
            return {"status":"resolved", "message": f"Payment troubleshooting steps:\n\n{message}"}

        return {"status":"escalated", "message":"Billing issues often require human review. I'll escalate this to the billing team with next steps."}
