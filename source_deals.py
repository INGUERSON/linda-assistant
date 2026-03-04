import feedparser
import os
import time
import json
from datetime import datetime
from ai_brain import draft_proposal
from bot import get_linda_response

# File to store already seen job IDs so Linda doesn't send duplicate alerts
SEEN_JOBS_FILE = "seen_jobs.json"

def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_jobs(seen_jobs):
    with open(SEEN_JOBS_FILE, 'w') as f:
        json.dump(list(seen_jobs), f)

def evaluate_job_with_ai(title, description):
    """Asks Linda's AI if this job is a good fit and how to reply."""
    prompt = f"""
    Chefe, avalie essa vaga de Freela:
    Título: {title}
    Descrição: {description[:500]}...
    
    Responda EXATAMENTE nesse formato curto:
    [AVALIAÇÃO]: (Nota de 1 a 10 para o nosso perfil de Desenvolvedor)
    [MENSAGEM]: (Uma frase curta de alerta para me enviar no Telegram)
    """
    response = get_linda_response(prompt)
    if not response or "[AVALIAÇÃO]" not in response:
        return 0, "Erro ao avaliar."
    
    try:
        # Pega o número que vem depois de [AVALIAÇÃO]:
        score_part = response.split("[AVALIAÇÃO]:")[1].split('\n')[0].strip()
        score = int(''.join(c for c in score_part if c.isdigit()))
        msg_part = response.split("[MENSAGEM]:")[1].strip()
        return score, msg_part
    except:
        return 5, "Vaga encontrada, mas falhei ao pontuar."

def fetch_upwork_jobs():
    """
    Fetches Jobs from an Upwork RSS Feed.
    Note: Upwork RSS usually requires a specific search URL.
    This is a generic example query for 'python AND automation'.
    """
    search_query = "python AND automation"
    # Example generic feed format (Replace with user's actual RSS link later)
    rss_url = f"https://www.upwork.com/ab/feed/jobs/rss?q={search_query.replace(' ', '+')}&sort=recency"
    
    print(f"[{datetime.now()}] Hunting for jobs on Upwork: {search_query}...")
    
    feed = feedparser.parse(rss_url)
    seen_jobs = load_seen_jobs()
    new_opportunities = []

    for entry in feed.entries[:5]: # Check the latest 5
        job_id = entry.id if hasattr(entry, 'id') else entry.link
        
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            score, alert_msg = evaluate_job_with_ai(entry.title, entry.description)
            
            # If Linda thinks it's a good match (Score 7 or higher)
            if score >= 7:
                # Draft a proposal automatically
                proposal = draft_proposal(entry.title, entry.description)
                
                new_opportunities.append({
                    "title": entry.title,
                    "link": entry.link,
                    "alert": alert_msg,
                    "score": score,
                    "proposal": proposal
                })
                
    save_seen_jobs(seen_jobs)
    return new_opportunities

if __name__ == "__main__":
    # Test script locally
    jobs = fetch_upwork_jobs()
    for job in jobs:
        print(f"🎯 Match Encontrado (Nota {job['score']}): {job['title']}")
        print(f"🗣️ Mensagem da Linda: {job['alert']}")
        print(f"🔗 Link: {job['link']}\n")
