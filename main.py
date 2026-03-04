from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import os
from bot import create_bot_application
from source_deals import fetch_upwork_jobs
from apscheduler.schedulers.background import BackgroundScheduler
import requests

telegram_app = None

def run_job_hunter():
    print("Linda is hunting for deals...")
    opportunities = fetch_upwork_jobs()
    
    # Send a telegram message using the raw API if we found anything good
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = "667589872" # Configured by user
    
    for opp in opportunities:
        if token and chat_id and chat_id != "SEU_CHAT_ID_AQUI":
            msg = f"🚨 *NOVA VAGA ENCONTRADA (Nota {opp['score']})*\n\n"
            msg += f"*{opp['title']}*\n"
            msg += f"👱‍♀️ Linda: _{opp['alert']}_\n\n"
            msg += f"*📝 Minha Sugestão de Proposta:*\n"
            msg += f"```text\n{opp.get('proposal', 'Falha ao gerar proposta.')}\n```\n\n"
            msg += f"[Ver Projeto no Upwork]({opp['link']})"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Linda Assistant background tasks...")
    global telegram_app
    
    telegram_app = create_bot_application()
    
    if telegram_app:
        print("Initializing and starting Telegram Polling cleanly...")
        await telegram_app.initialize()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        await telegram_app.start()

    # Start APScheduler for background job hunting
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job_hunter, 'interval', minutes=60)
    scheduler.start()
    
    yield
    print("Shutting down Linda Assistant...")
    scheduler.shutdown()
    
    if telegram_app:
        print("Stopping Telegram Application...")
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()


app = FastAPI(title="Linda Freelance Assistant API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Linda is online and hunting for clients."}

@app.get("/status")
def status():
    return {"status": "active", "brain": "GPT-4o", "modules": ["telegram", "fastapi"]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
