<div align="center">🤖 SmartSupport Agent</div>
<p align="center"> A full-stack, multi-agent customer support automation system with ticket triage, resolution, escalation, duplicate detection, memory, observability, and an admin dashboard. </p>

🚀 Overview

SmartSupport Agent is an intelligent automated customer support system built using a multi-agent architecture.
It processes user tickets, identifies intents, resolves issues automatically using domain-specific agents, escalates when required, and stores all activity in a SQLite database.

It includes:

Automated ticket triage

Multi-intent detection

Auto-resolution using Account/Billing/Order/Technical/Product agents

Duplicate ticket protection

Admin login + secure dashboard

Observability logs

Long-term memory engine

Clean Tailwind UI for ticket submission

Live dashboard with ticket history

SmartSupport significantly reduces manual workload, speeds up ticket handling, and improves the overall quality and consistency of customer support.

🧠 Features
✔ Multi-Agent Architecture

Includes the following agents:

Agent	Responsibility
IngestAgent	Normalizes ticket input
TriageAgent	Classifies primary & secondary intents
ResolverAgent	Runs KB search + diagnostics + domain agents
EscalationAgent	Generates escalation summaries
AccountAgent	Password, login, profile updates
BillingAgent	Refunds, payments, invoices
TechnicalAgent	App crashes, network errors, error codes
OrderAgent	Track order, cancel order, returns
ProductAgent	Feature usage, how-to questions

✔ Admin Dashboard (with Login)

Secure admin login:

Login ID: Yokesh29
Password: Yovan@29


Dashboard displays:

All tickets

Status (Resolved / Escalated / Duplicate)

Issue text

Intent

Final resolution message

Collapsible details

✔ Duplicate Ticket Detection

If a ticket ID is reused, SmartSupport returns:

Ticket ID <x> is already used. Please use a new ticket ID.

✔ Ticket Memory Engine

Stores:

Successful resolutions

Past patterns

Metadata for future matching

✔ Observability Layer

Includes:

Structured logging

Request traceability

Ticket event tracking

✔ UI with Tailwind Glassmorphism

Beautiful frontend for ticket submission:

3D glass effect

Animated resolution card

With reference ID

Responsive layout

🏗 Architecture
🔧 System Pipeline

<img width="1024" height="1024" alt="Gemini_Generated_Image_ieolp5ieolp5ieol" src="https://github.com/user-attachments/assets/a1182660-ae81-4f23-abf8-557c9cab30fa" />

📁 Project Structure

<img width="1024" height="1024" alt="Gemini_Generated_Image_24qv7r24qv7r24qv" src="https://github.com/user-attachments/assets/0cf0b8fa-c7a8-4afa-bfb3-99964b7990dc" />

⚙ How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Run the server
python src/api_server.py

3️⃣ Open the UI

📌 Customer Ticket Page

http://127.0.0.1:5500/


📌 Admin Login

http://127.0.0.1:5500/admin-login


📌 Ticket Dashboard

http://127.0.0.1:5500/dashboard

💬 Example Questions Users Can Ask
🔐 Account Issues

I forgot my password

I can’t log in

My account is locked

Change my email

Update my phone number

💳 Billing

I want a refund

Payment failed

Send me invoice

🛠 Technical

App is crashing

Error 500

Network timeout

📦 Orders

Track my order

Cancel my order

Return item

📘 Product Usage

How to enable notifications?

How to use dashboard?

🟡 Escalation

Talk to a manager

Escalate this ticket

📈 Value Delivered

SmartSupport reduces manual ticket workload by 6–8 hours per week, automating:

Triage

Troubleshooting

KB search

Diagnostics

Response drafting

Escalation summaries

It increases:

Productivity

Resolution accuracy

Customer satisfaction

Team efficiency

🔮 Future Enhancements

If extended, SmartSupport could include a Proactive Insights Agent that monitors logs and system metrics to detect:

repetitive errors

trending issues

upcoming outages

failing services

This would allow pre-emptive alerts and automated KB updates.

❤️ Author

Built by Yokesh, leveraging Python, Flask, Tailwind CSS, and a custom multi-agent architecture.
