# src/agents/ingest_agent.py
class IngestAgent:
    def process(self, ticket: dict) -> dict:
        # Minimal normalization and metadata extraction
        text = ticket.get("text", "") or ""
        normalized = " ".join(text.strip().split())
        return {
            "ticket_id": ticket.get("ticket_id"),
            "text": normalized,
            "raw": ticket
        }
