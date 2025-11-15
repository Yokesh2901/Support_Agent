# src/resolver_dispatcher.py
from src.agents.account_agent import AccountAgent
from src.agents.billing_agent import BillingAgent
from src.agents.technical_agent import TechnicalAgent
from src.agents.order_agent import OrderAgent
from src.agents.product_agent import ProductAgent

# ----------------------------------------------------
# INTENT → AGENT MAPPING (FULL + UPDATED)
# ----------------------------------------------------
DISPATCH = {

    # ACCOUNT
    "password_reset": AccountAgent(),
    "login_issue": AccountAgent(),
    "account_locked": AccountAgent(),
    "update_email": AccountAgent(),            # <-- FIXED

    # BILLING
    "billing_refund": BillingAgent(),
    "payment_failed": BillingAgent(),
    "invoice_request": BillingAgent(),
    "subscription_change": BillingAgent(),

    # TECHNICAL
    "error_code": TechnicalAgent(),
    "app_crash": TechnicalAgent(),
    "network_issue": TechnicalAgent(),         # <-- add if exists
    "slow_app": TechnicalAgent(),              # <-- add if exists

    # ORDERS
    "order_status": OrderAgent(),
    "cancel_order": OrderAgent(),
    "return_item": OrderAgent(),

    # PRODUCT HELP
    "feature_howto": ProductAgent(),
}


# ----------------------------------------------------
# DISPATCH FUNCTION
# ----------------------------------------------------
def dispatch(session, triage_result):
    intent = triage_result.get("intent")
    agent = DISPATCH.get(intent)

    if agent:
        return agent.process(session, triage_result)

    return {
        "status": "escalated",
        "message": "I couldn't find an automated handler for that request — escalating now."
    }
