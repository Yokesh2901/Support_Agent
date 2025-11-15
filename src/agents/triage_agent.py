# src/agents/triage_agent.py

class TriageAgent:

    INTENT_KEYWORDS = {

        # ACCOUNT & LOGIN
        "password_reset": [
            "forgot password", "reset password", "can't remember password"
        ],
        "login_issue": [
            "can't log in", "login error", "login not working", "sign in"
        ],
        "account_locked": [
            "account locked", "too many attempts", "disabled account"
        ],
        "update_email": [
            "change email",
            "update email",
            "update my email",
            "change my email",
            "update phone",
            "change phone",
            "update mobile number",
            "update profile",
            "edit profile",
            "change profile details",
            "change account details",
            "update account details",
        ],

        # BILLING
        "billing_refund": ["refund", "money back"],
        "payment_failed": ["payment failed", "card declined", "upi failed"],
        "invoice_request": ["invoice", "receipt"],
        "subscription_change": [
            "upgrade plan", "downgrade", "cancel subscription"
        ],

        # TECHNICAL
        "error_code": ["error 500", "error 504", "error 502"],
        "app_crash": ["app crash", "crashing", "app closed"],
        "network_issue": ["network timeout", "connection failed"],
        "slow_app": ["slow", "lag", "performance"],

        # ORDERS
        "order_status": ["track order", "where is my order", "order status"],
        "cancel_order": ["cancel order"],
        "return_item": ["return order", "return item"],

        # FEATURE HELP
        "feature_howto": ["how to", "how do i", "guide me"],

        # HUMAN ESCALATION
        "human_support": ["talk to manager", "complaint", "escalate", "not helpful"]
    }


    def detect_intents(self, text):
        text = text.lower()
        found = []

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    found.append(intent)
                    break  # avoid duplicate matches

        # If nothing matched → escalate to human
        if not found:
            return ["human_support"]

        return found


    def process(self, session):
        text = session.get("text", "").lower()
        intents = self.detect_intents(text)

        return {
            "intent": intents[0],            # primary intent
            "secondary_intents": intents[1:] # zero or more
        }
