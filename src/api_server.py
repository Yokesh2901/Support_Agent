# src/api_server.py
import sys
import os
import uuid
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for

# ----------------------------------------
# FIX PYTHON PATH (so imports like src.xxx work)
# ----------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ----------------------------------------
# IMPORT AGENTS + UTILITIES (your project modules)
# ----------------------------------------
from src.agents.ingest_agent import IngestAgent
from src.agents.triage_agent import TriageAgent
from src.agents.escalation_agent import EscalationAgent
from src.agents.resolver_agent import ResolverAgent

# storage utilities - adjust if your sqlite_store has a different API
from src.storage.sqlite_store import (
    init_db,
    save_ticket,
    list_tickets,
    ticket_exists,
    count_tickets,
)
from src.observability.observability import log_event
from src.memory.memory_bank import MemoryBank

# ----------------------------------------
# INIT SYSTEM
# ----------------------------------------
app = Flask(__name__)
# change this secret key in production
app.secret_key = "CHANGE_ME_TO_A_RANDOM_SECRET"

# initialize DB + components
init_db()
memory = MemoryBank()
ingest = IngestAgent()
triage = TriageAgent()
resolver = ResolverAgent()
escalation = EscalationAgent()


# ----------------------
# HOME (ticket submit)
# ----------------------
HOME_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SmartSupport Agent</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: linear-gradient(135deg, #0f0f0f, #1a1a1a); }
    .glass { backdrop-filter: blur(10px); background: rgba(255,255,255,0.04);
             border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 26px; }
    .result { white-space: pre-wrap; }
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-6 text-white">
  <div class="glass max-w-2xl w-full">
    <h1 class="text-3xl font-bold mb-4 text-center">SmartSupport Agent</h1>

    <div class="mb-4 text-center text-yellow-300 font-semibold">
      Total Tickets Created: {{ total }} &nbsp; — &nbsp; Your Ticket ID: <span class="text-green-400 font-bold">{{ next_ticket }}</span>
    </div>

    <div class="text-center mb-6">
      <a href="{{ url_for('admin_login') }}" class="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600">Admin Login</a>
      <a href="{{ url_for('dashboard') }}" class="px-4 py-2 bg-purple-600 rounded hover:bg-purple-500 ml-2">Dashboard</a>
    </div>

    <form id="ticketForm" class="space-y-4">
      <!-- user does not set ticket_id manually anymore -->
      <div>
        <label class="block mb-1 text-gray-300">Issue Description</label>
        <textarea id="text" rows="5" class="w-full p-3 rounded bg-gray-800 text-white outline-none" placeholder="Describe your issue..." required></textarea>
      </div>

      <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold">Submit Ticket</button>
    </form>

    <div id="result" class="mt-6 hidden"></div>
  </div>

<script>
document.getElementById('ticketForm').addEventListener('submit', async function(e){
  e.preventDefault();
  const text = document.getElementById('text').value.trim();
  if(!text){ alert('Please describe your issue'); return; }

  // POST to /ticket - server will auto-assign ticket_id
  const resp = await fetch('/ticket', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ text })
  });

  const data = await resp.json();
  const resultDiv = document.getElementById('result');
  let html = '';

  if(data.status === 'resolved'){
    html += '<div class="p-4 rounded bg-green-900/50 border border-green-500">';
    html += '<h3 class="text-lg font-semibold text-green-300">Issue Resolved</h3>';
    html += '<div class="result text-gray-200 mt-2">' + (data?.resolution?.message || '') + '</div>';
    html += '</div>';
  } else if(data.status === 'duplicate'){
    html += '<div class="p-4 rounded bg-red-900/50 border border-red-500">';
    html += '<h3 class="text-lg font-semibold text-red-300">Duplicate Ticket</h3>';
    html += '<div class="text-gray-200 mt-2">' + (data.message || '') + '</div>';
    html += '</div>';
  } else if(data.status === 'escalated'){
    html += '<div class="p-4 rounded bg-yellow-900/50 border border-yellow-500">';
    html += '<h3 class="text-lg font-semibold text-yellow-300">Escalated to Human Team</h3>';
    html += '<div class="result text-gray-200 mt-2">' + (data.message || '') + '</div>';
    if(data.escalation){
      html += '<div class="mt-3 text-sm text-gray-400">Escalation summary: ' + JSON.stringify(data.escalation) + '</div>';
    }
    html += '</div>';
  } else {
    html += '<div class="p-4 rounded bg-gray-800 border border-gray-700"><div class="result text-gray-200">Unexpected response: ' + JSON.stringify(data) + '</div></div>';
  }

  resultDiv.innerHTML = html;
  resultDiv.classList.remove('hidden');
});
</script>

</body>
</html>
"""

# ----------------------
# DASHBOARD HTML (Jinja)
# ----------------------
DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Ticket Dashboard</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #0f0f0f; color: white; }
    .glass { backdrop-filter: blur(10px); background: rgba(255,255,255,0.03); padding: 18px; border-radius: 12px; border:1px solid rgba(255,255,255,0.04); }
  </style>
</head>
<body class="p-8">
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">📊 Ticket Dashboard</h1>
      <div>
        <a href="{{ url_for('home') }}" class="px-3 py-2 bg-blue-600 rounded hover:bg-blue-700">Home</a>
        <a href="{{ url_for('logout') }}" class="px-3 py-2 bg-red-600 rounded hover:bg-red-700 ml-2">Logout</a>
      </div>
    </div>

    <div class="mb-4 text-gray-300">Showing {{ tickets|length }} tickets (most recent first)</div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {% for t in tickets %}
      <div class="glass">
        <div class="flex items-start justify-between">
          <div>
            <div class="text-sm text-gray-400">Ticket ID</div>
            <div class="text-xl font-semibold">{{ t.ticket_id }}</div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-400">Status</div>
            <div class="{% if t.status == 'resolved' %}text-green-400{% elif t.status == 'escalated' %}text-yellow-400{% else %}text-red-400{% endif %} font-semibold">
              {{ t.status | upper }}
            </div>
          </div>
        </div>

        <div class="mt-3 text-gray-200">
          <div class="text-sm text-gray-400">Intent</div>
          <div class="font-medium">{{ t.intent }}</div>
          <details class="mt-3 text-sm">
            <summary class="cursor-pointer text-blue-300">View Details</summary>
            <div class="mt-2 text-gray-300">
              <p><strong>Issue:</strong><br/>{{ t.text }}</p>
              <p class="mt-2"><strong>Resolution:</strong><br/>{{ t.resolution.message }}</p>
            </div>
          </details>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""

# ----------------------
# ROUTES
# ----------------------
@app.route("/", methods=["GET"])
def home():
    total = count_tickets()
    next_ticket = total + 1
    return render_template_string(HOME_HTML, total=total, next_ticket=next_ticket)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/tickets", methods=["GET"])
def tickets_list():
    # return raw tickets (JSON)
    return jsonify(list_tickets(500))


# ----------------------
# ADMIN LOGIN / PROTECTION
# ----------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    # simple admin form + session
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "Yokesh29" and password == "Yovan@29":
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Login ID or Password"
    # render very small HTML form (keeps separation simple)
    form = """
    <!doctype html>
    <html>
    <head><meta charset="utf-8"/><title>Admin Login</title><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="min-h-screen flex items-center justify-center bg-gray-900 text-white p-6">
      <form method="post" class="glass w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Admin Login</h2>
        <label class="block mb-2">Login ID</label>
        <input name="username" class="w-full p-3 mb-3 rounded bg-gray-800" required>
        <label class="block mb-2">Password</label>
        <input type="password" name="password" class="w-full p-3 mb-3 rounded bg-gray-800" required>
        <button class="w-full py-3 bg-blue-600 rounded">Login</button>
        <div class="mt-3 text-red-400">%s</div>
        <div class="mt-4 text-sm"><a href="/" class="text-blue-300">Back to Home</a></div>
      </form>
    </body>
    </html>
    """ % error
    return form


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/dashboard", methods=["GET"])
def dashboard():
    # require admin
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    tickets = list_tickets(500)
    # list_tickets should return list of dict-like objects with keys: ticket_id, text, intent, status, resolution
    # If your list_tickets returns tuples, adapt accordingly.
    return render_template_string(DASHBOARD_HTML, tickets=tickets)


# ----------------------
# PROCESS TICKET
# ----------------------
@app.route("/ticket", methods=["POST"])
def receive_ticket():
    # server assigns ticket id automatically
    request_id = str(uuid.uuid4())
    payload = request.json if request.is_json else request.form.to_dict()
    text = payload.get("text", "").strip()
    if not text:
        return jsonify({"request_id": request_id, "status": "error", "message": "Empty ticket text"}), 400

    # propose a ticket id (use count_tickets+1 to avoid user choices)
    ticket_id = str(count_tickets() + 1)

    # Duplicate safety (if your ticket_exists checks strings vs ints ensure consistent types)
    if ticket_exists(ticket_id):
        return jsonify({"request_id": request_id, "status": "duplicate", "message": f"Ticket ID {ticket_id} is already used."})

    ticket = {"ticket_id": ticket_id, "text": text}

    # log
    log_event("received_ticket", {"ticket": ticket_id})

    # pipeline
    session_data = ingest.process(ticket)
    triage_res = triage.process(session_data)

    primary_intent = triage_res.get("intent")
    secondary_intents = triage_res.get("secondary_intents", [])

    messages = []

    primary_output = resolver.process(session_data, {"intent": primary_intent})
    if primary_output.get("message"):
        messages.append(primary_output["message"])

    for sec in secondary_intents:
        sec_output = resolver.process(session_data, {"intent": sec})
        if sec_output.get("message"):
            messages.append(sec_output["message"])

    final_message = "\n\n".join(messages) if messages else ""

    resolution = {
        "status": primary_output.get("status", "escalated"),
        "message": final_message
    }

    # persist ticket
    save_ticket({
        "ticket_id": ticket_id,
        "text": ticket["text"],
        "intent": primary_intent,
        "status": resolution["status"],
        "resolution": resolution
    })

    # memory store for successful automated resolutions
    if resolution["status"] == "resolved":
        memory.save({
            "ticket_id": ticket_id,
            "text": ticket["text"],
            "intent": primary_intent,
            "resolution": resolution
        })
        return jsonify({"request_id": request_id, "status": "resolved", "resolution": resolution})

    # escalate
    escalated = escalation.process(session_data, triage_res, resolution)
    return jsonify({"request_id": request_id, "status": "escalated", "message": final_message, "escalation": escalated})


# ----------------------
# START
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    # bind to 0.0.0.0 so Render/Heroku can route traffic
    app.run(host="0.0.0.0", port=port, debug=True)
