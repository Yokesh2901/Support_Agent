# src/tools/kb_search.py
import json
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[1] / "kb"

def _load_all():
    articles = []
    for fp in KB_DIR.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            for a in data.get("articles", []):
                a["_domain"] = data.get("domain")
                articles.append(a)
        except Exception:
            continue
    return articles

ARTICLES_CACHE = _load_all()

def _score_article(article, q):
    text = (article.get("title","") + " " + article.get("content","") + " " + " ".join(article.get("tags",[]))).lower()
    q = q.lower()
    score = 0
    if q in text:
        score += 10
    for token in q.split():
        if token and token in text:
            score += 2
    return score

def kb_search(query: str, top_n=1):
    """Return top_n matching articles and a conversational summary string."""
    scored = []
    for a in ARTICLES_CACHE:
        score = _score_article(a, query)
        if score > 0:
            scored.append((score, a))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [s[1] for s in scored[:top_n]]
    # generate a short human-friendly summary from the first article
    if results:
        art = results[0]
        # Create a short conversational answer
        first_lines = art.get("content", "").splitlines()
        # use up to first 3 sentences/lines for the summary
        summary = " ".join(first_lines)[:800]
        return {"article": art, "summary": summary}
    return {"article": None, "summary": None}
