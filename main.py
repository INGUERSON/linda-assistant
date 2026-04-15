from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import os
from bot import create_bot_application
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Assistant background tasks...")
    global telegram_app
    
    telegram_app = create_bot_application()
    
    if telegram_app:
        print("Initializing and starting Telegram Polling cleanly...")
        await telegram_app.initialize()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        await telegram_app.start()

    yield
    print("Shutting down Assistant...")
    
    if telegram_app:
        print("Stopping Telegram Application...")
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()


app = FastAPI(title="Linda - Secretária Pessoal", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Linda está online e pronta para ajudar, chefe! 💼"}

@app.get("/status")
def status():
    return {"status": "active", "brain": "GPT-4o-mini", "modules": ["telegram", "tasks", "projects", "schedule"]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
