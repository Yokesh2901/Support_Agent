import sys
import os
import uuid
from flask import Flask, request, jsonify, render_template_string

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

init_db()
memory = MemoryBank()
ingest = IngestAgent()
triage = TriageAgent()
resolver = ResolverAgent()
escalation = EscalationAgent()

# ----------------------------------------
# HOME PAGE UI
# ----------------------------------------
@app.route("/", methods=["GET"])
def home():
    from src.storage.sqlite_store import count_tickets  # ensure import

    total = count_tickets()
    next_ticket_id = total + 1

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>SmartSupport Agent</title>
        <script src="https://cdn.tailwindcss.com"></script>

        <style>
            body { background: linear-gradient(135deg, #0f0f0f, #1a1a1a); }
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

            <div class="text-center mb-6 text-yellow-300 font-semibold text-lg">
                Total Tickets Created: <b>{TOTAL}</b><br>
                Your Ticket ID: <span class="text-green-400">{NEXT}</span>
            </div>

            <form id="ticketForm" class="space-y-5">

                <!-- TICKET ID HIDDEN - AUTO GENERATED -->
                <input type="hidden" id="ticket_id" value="{NEXT}">

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

            <div id="result" class="mt-6 hidden"></div>
        </div>

        <script>
        document.getElementById("ticketForm").addEventListener("submit", async function(e){
            e.preventDefault();

            const ticket_id = document.getElementById("ticket_id").value;
            const text = document.getElementById("text").value;

            const res = await fetch("/ticket", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticket_id: ticket_id, text: text })
            });

            const data = await res.json();
            const msg = (data.resolution && data.resolution.message) ? data.resolution.message 
                        : data.message || "No response";

            let color = "text-yellow-300";
            let title = "Ticket Escalated";

            if (data.status === "resolved") {
                color = "text-green-400";
                title = "Issue Resolved Successfully";
            }
            if (data.status === "duplicate") {
                color = "text-red-400";
                title = "Duplicate Ticket ID";
            }

            document.getElementById("result").innerHTML = `
                <div class="glass p-5 rounded">
                    <h2 class="text-xl font-bold ${color}">${title}</h2>
                    <p class="mt-3 text-gray-300">${msg.replace(/\\n/g, "<br>")}</p>
                    <p class="text-sm text-gray-500 mt-3"><b>Reference ID:</b> ${data.request_id}</p>
                </div>
            `;
            document.getElementById("result").classList.remove("hidden");
        });
        </script>

    </body>
    </html>
    """.replace("{TOTAL}", str(total)).replace("{NEXT}", str(next_ticket_id))

    return render_template_string(html)


# ----------------------------------------
# HEALTH
# ----------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ----------------------------------------
# DASHBOARD
# ----------------------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    tickets = list_tickets(200)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Dashboard</title>
    </head>
    <body class='p-10 text-white bg-black'>
        <h1 class='text-3xl font-bold mb-6 text-center'>📊 Ticket Dashboard</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    """

    for t in tickets:
        color = {
            "resolved": "text-green-400",
            "duplicate": "text-red-400",
            "escalated": "text-yellow-400"
        }.get(t["status"], "text-gray-300")

        html += f"""
            <div class='p-5 bg-gray-900 rounded-lg border border-gray-700'>
                <h2 class='text-xl font-bold'>Ticket ID: {t['ticket_id']}</h2>
                <p><strong>Intent:</strong> {t['intent']}</p>
                <p class='{color}'><strong>Status:</strong> {t['status']}</p>
                <details class='mt-3'>
                    <summary class='cursor-pointer text-blue-400'>View Details</summary>
                    <p class='mt-2 text-gray-300'>{t['text']}</p>
                    <p class='mt-2 text-gray-400'>{t['resolution']['message']}</p>
                </details>
            </div>
        """

    html += "</div></body></html>"
    return render_template_string(html)

# ----------------------------------------
# PROCESS TICKET
# ----------------------------------------
@app.route("/ticket", methods=["POST"])
def receive_ticket():
    request_id = str(uuid.uuid4())
    payload = request.json if request.is_json else request.form.to_dict()

    ticket_id = payload.get("ticket_id", request_id)

    # DUPLICATE CHECK
    if ticket_exists(ticket_id):
        return jsonify({
            "request_id": request_id,
            "status": "duplicate",
            "message": f"Ticket ID {ticket_id} is already used."
        })

    ticket = {
        "ticket_id": ticket_id,
        "text": payload.get("text", "")
    }

    log_event("received_ticket", {"ticket": ticket_id})

    session = ingest.process(ticket)
    triage_res = triage.process(session)

    primary_intent = triage_res["intent"]
    secondary = triage_res["secondary_intents"]

    messages = []

    primary_res = resolver.process(session, {"intent": primary_intent})
    if primary_res.get("message"):
        messages.append(primary_res["message"])

    for sec in secondary:
        sec_res = resolver.process(session, {"intent": sec})
        if sec_res.get("message"):
            messages.append(sec_res["message"])

    final_message = "\n\n".join(messages)

    resolution = {
        "status": primary_res.get("status", "resolved"),
        "message": final_message
    }

    save_ticket({
        "ticket_id": ticket_id,
        "text": ticket["text"],
        "intent": primary_intent,
        "status": resolution["status"],
        "resolution": resolution
    })

    if resolution["status"] == "resolved":
        memory.save(ticket)
        return jsonify({
            "request_id": request_id,
            "status": "resolved",
            "resolution": resolution
        })

    esc = escalation.process(session, triage_res, resolution)

    return jsonify({
        "request_id": request_id,
        "status": "escalated",
        "escalation": esc,
        "message": final_message
    })

# ----------------------------------------
# RUN FLASK FOR RENDER
# ----------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    app.run(host="0.0.0.0", port=port)
