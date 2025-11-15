import sys
import os
import uuid
from flask import Flask, request, jsonify, render_template_string, session, redirect

# ----------------------------------------
# FIX PYTHON PATH
# ----------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ----------------------------------------
# IMPORT AGENTS + UTILITIES
# ----------------------------------------
from src.agents.ingest_agent import IngestAgent
from src.agents.triage_agent import TriageAgent
from src.agents.escalation_agent import EscalationAgent
from src.agents.resolver_agent import ResolverAgent

from src.storage.sqlite_store import init_db, save_ticket, list_tickets, ticket_exists
from src.observability.observability import log_event
from src.memory.memory_bank import MemoryBank

# ----------------------------------------
# INIT SYSTEM
# ----------------------------------------
app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_CHANGE_ME"

init_db()
memory = MemoryBank()
ingest = IngestAgent()
triage = TriageAgent()
resolver = ResolverAgent()
escalation = EscalationAgent()


# ======================================================================
#                             HOME PAGE UI
# ======================================================================
@app.route("/", methods=["GET"])
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>SmartSupport Agent</title>
        <script src="https://cdn.tailwindcss.com"></script>

        <style>
            body {
                background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
            }
            .glass {
                backdrop-filter: blur(14px);
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.4);
            }
        </style>
    </head>

    <body class="min-h-screen flex items-center justify-center p-8 text-white">
        <div class="glass max-w-2xl w-full">

            <h1 class="text-3xl font-bold mb-6 text-center">SmartSupport Agent</h1>

            <!-- DASHBOARD BUTTON -->
            <div class="text-center mb-6">
                <a href="/dashboard" 
                   class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-semibold transition">
                   📊 View Ticket Dashboard
                </a>
            </div>

            <!-- TICKET FORM -->
            <form id="ticketForm" class="space-y-5">
                <div>
                    <label class="block mb-1 text-gray-300">Ticket ID</label>
                    <input type="text" id="ticket_id"
                        class="w-full p-3 rounded bg-gray-800 text-white outline-none" 
                        value="1" required>
                </div>

                <div>
                    <label class="block mb-1 text-gray-300">Issue Description</label>
                    <textarea id="text"
                        class="w-full p-3 rounded bg-gray-800 text-white outline-none"
                        rows="4" placeholder="Describe your issue..." required></textarea>
                </div>

                <button type="submit"
                    class="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold transition">
                    Submit Ticket
                </button>
            </form>

            <!-- RESULT BOX -->
            <div id="result" class="mt-6 hidden"></div>
        </div>

        <!-- SCRIPT -->
        <script>
        document.getElementById("ticketForm").addEventListener("submit", async function(event){
            event.preventDefault();

            const ticket_id = document.getElementById("ticket_id").value;
            const text = document.getElementById("text").value;

            const response = await fetch("/ticket", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticket_id, text })
            });

            const data = await response.json();
            const msg = data?.resolution?.message || data?.message || "No response.";

            document.getElementById("result").innerHTML = `
                <div class="glass mt-6 p-5">

                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-3 h-3 ${
                            data.status === "resolved" ? "bg-green-500" :
                            data.status === "duplicate" ? "bg-red-500" :
                            "bg-yellow-500"
                        } rounded-full"></div>

                        <h2 class="text-xl font-semibold ${
                            data.status === "resolved" ? "text-green-400" :
                            data.status === "duplicate" ? "text-red-400" :
                            "text-yellow-300"
                        }">
                            ${
                                data.status === "resolved"
                                ? "Issue Resolved Successfully"
                                : data.status === "duplicate"
                                ? "Duplicate Ticket ID"
                                : "Ticket Escalated to Human Support"
                            }
                        </h2>
                    </div>

                    <p class="text-gray-300 leading-relaxed text-lg">
                        ${msg.replace(/\\n/g, "<br>")}
                    </p>

                    <div class="mt-4 text-sm text-gray-500">
                        <strong>Reference ID:</strong> ${data.request_id}
                    </div>
                </div>
            `;

            document.getElementById("result").classList.remove("hidden");
        });
        </script>

    </body>
    </html>
    """
    return render_template_string(html)



# ======================================================================
#                             ADMIN LOGIN PAGE
# ======================================================================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-gray-900 flex items-center justify-center min-h-screen text-white">

        <form method="POST" class="glass p-8 rounded-lg max-w-md w-full">
            <h2 class="text-3xl font-bold text-center mb-6">Admin Login</h2>

            <label class="block mb-2">Login ID</label>
            <input name="username" class="w-full p-3 rounded bg-gray-800 mb-4" required>

            <label class="block mb-2">Password</label>
            <input type="password" name="password" class="w-full p-3 rounded bg-gray-800 mb-4" required>

            <button class="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded text-white font-semibold">
                Login
            </button>

            <p class="text-red-400 text-center mt-3">%s</p>
        </form>

    </body>
    </html>
    """

    error = ""

    if request.method == "POST":
        if request.form.get("username") == "Yokesh29" and request.form.get("password") == "Yovan@29":
            session["admin"] = True
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    return html % error



# ======================================================================
#                                LOGOUT
# ======================================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin-login")



# ======================================================================
#                             TICKET DASHBOARD
# ======================================================================
@app.route("/dashboard", methods=["GET"])
def dashboard():

    # ADMIN PROTECTION
    if not session.get("admin"):
        return redirect("/admin-login")

    tickets = list_tickets(200)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"/>
        <title>Ticket Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background: #0f0f0f; color: white; }
            .glass { 
                backdrop-filter: blur(12px);
                background: rgba(255,255,255,0.05);
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.1);
            }
        </style>
    </head>

    <body class="p-10">

        <h1 class="text-3xl font-bold mb-6 text-center">📊 Ticket Dashboard</h1>

        <div class="text-center mb-6">
            <a href="/" class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">Back to Home</a>
            <a href="/logout" class="px-4 py-2 bg-red-600 rounded hover:bg-red-700 ml-2">Logout</a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    """

    # Render Tickets
    for t in tickets:
        status_color = {
            "resolved": "text-green-400",
            "escalated": "text-yellow-400",
            "duplicate": "text-red-400"
        }.get(t["status"], "text-gray-300")

        html += f"""
        <div class="glass p-5 shadow-lg">
            <h2 class="text-xl font-bold mb-2">Ticket ID: {t['ticket_id']}</h2>
            <p class="text-gray-300 mb-2"><strong>Intent:</strong> {t['intent']}</p>
            <p class="{status_color} mb-2"><strong>Status:</strong> {t['status'].upper()}</p>

            <details class="mt-3">
                <summary class="cursor-pointer text-blue-400">View Details</summary>
                <div class="mt-2 text-gray-300 text-sm">
                    <p><strong>Issue:</strong><br>{t['text']}</p>
                    <p class="mt-2"><strong>Resolution:</strong><br>{t['resolution']['message']}</p>
                </div>
            </details>
        </div>
        """

    html += """
        </div>
    </body>
    </html>
    """

    return render_template_string(html)



# ======================================================================
#                          PROCESS TICKET
# ======================================================================
@app.route("/ticket", methods=["POST"])
def receive_ticket():
    request_id = str(uuid.uuid4())

    payload = request.json if request.is_json else request.form.to_dict()

    ticket = {
        "ticket_id": payload.get("ticket_id", request_id),
        "text": payload.get("text", "")
    }

    # DUPLICATE CHECK
    if ticket_exists(ticket["ticket_id"]):
        return jsonify({
            "request_id": request_id,
            "status": "duplicate",
            "message": f"Ticket ID {ticket['ticket_id']} is already used. Please use a new ticket ID."
        })

    log_event("received_ticket", {"ticket": ticket["ticket_id"]})

    session_data = ingest.process(ticket)
    triage_res = triage.process(session_data)

    primary_intent = triage_res.get("intent")
    secondary_intents = triage_res.get("secondary_intents", [])

    messages = []

    # Primary intent response
    primary_output = resolver.process(session_data, {"intent": primary_intent})
    if "message" in primary_output:
        messages.append(primary_output["message"])

    # Secondary intents
    for sec in secondary_intents:
        sec_output = resolver.process(session_data, {"intent": sec})
        if "message" in sec_output:
            messages.append(sec_output["message"])

    final_message = "\n\n".join(messages)

    resolution = {
        "status": primary_output.get("status", "resolved"),
        "message": final_message
    }

    # SAVE IN DB
    save_ticket({
        "ticket_id": ticket["ticket_id"],
        "text": ticket["text"],
        "intent": primary_intent,
        "status": resolution["status"],
        "resolution": resolution
    })

    # Save memory if resolved
    if resolution["status"] == "resolved":
        memory.save({
            "ticket_id": ticket["ticket_id"],
            "text": ticket["text"],
            "intent": primary_intent,
            "resolution": resolution
        })
        return jsonify({"request_id": request_id, "status": "resolved", "resolution": resolution})

    # Escalation
    escalated = escalation.process(session_data, triage_res, resolution)

    return jsonify({
        "request_id": request_id,
        "status": "escalated",
        "message": final_message,
        "escalation": escalated
    })


# ======================================================================
#                          START SERVER
# ======================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    print(f"🚀 SmartSupport server running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)


