# src/agents/account_agent.py
from src.tools.kb_search import kb_search

class AccountAgent:
    def process(self, session, triage):
        intent = triage.get("intent")
        text = session.get("text", "")

        # -----------------------------------
        # PASSWORD RESET
        # -----------------------------------
        if intent == "password_reset":
            res = kb_search("password reset")
            message = res.get("summary") or (
                "You can reset your password using the 'Forgot Password' option on the login page."
            )

            return {
                "status": "resolved",
                "message": f"Sure — here’s how to reset your password:\n\n{message}"
            }

        # -----------------------------------
        # LOGIN ISSUES
        # -----------------------------------
        if intent == "login_issue":
            res = kb_search("login")
            message = res.get("summary") or (
                "Please verify your email, clear browser cache or try logging in from incognito mode."
            )

            return {
                "status": "resolved",
                "message": f"I’m sorry you're unable to log in. Try the following steps:\n\n{message}"
            }

        # -----------------------------------
        # ACCOUNT LOCKED
        # -----------------------------------
        if intent == "account_locked":
            return {
                "status": "escalated",
                "message": (
                    "Your account appears to be locked due to security reasons.\n\n"
                    "Please share the following so we can escalate it safely:\n"
                    "• Your registered email\n"
                    "• Approximate last login attempt time\n\n"
                    "A human support specialist will unlock it for you."
                )
            }

        # -----------------------------------
        # UPDATE EMAIL / PROFILE DETAILS
        # -----------------------------------
        if intent == "update_email":
            return {
                "status": "resolved",
                "message": (
                    "You can update your account details by going to:\n\n"
                    "Settings → Account → Profile → Edit\n\n"
                    "For email updates, you will receive a verification link on the new email address.\n"
                    "Clicking the verification link completes the update process."
                )
            }

        # -----------------------------------
        # FALLBACK (no match in account agent)
        # -----------------------------------
        return {
            "status": "escalated",
            "message": (
                "I couldn't handle this account request automatically — "
                "I'm escalating this to a human specialist."
            )
        }
