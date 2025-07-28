from http import HTTPStatus
import os
import tempfile
import anyio
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from telegram import Bot
from telegram.constants import ParseMode
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carica .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("ADMIN_CHAT_ID")
RAILWAY = os.getenv("RAILWAY") == "1"
PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=TELEGRAM_BOT_TOKEN)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 puoi specificare ["http://localhost:5500"] se vuoi essere più restrittivo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def submit_form(request: Request):
    try:
        data = await request.json()
        print("✅ Dati ricevuti:", data)

        # Costruisci il nome del file dal nome e dall'email
        nome = data.get("nome", "utente").strip().replace(" ", "_")
        email = data.get("email", "anonimo@example.com")
        email_prefix = email.split("@")[0].strip().replace(" ", "_")
        file_name = f"{nome}_{email_prefix}.pdf"

        # Crea PDF temporaneo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = Path(tmp.name)
            c = canvas.Canvas(str(tmp_path), pagesize=A4)
            width, height = A4
            y = height - 40

            c.setFont("Helvetica", 12)
            c.drawString(50, y, "📋 Questionario Vitimonitor")
            y -= 30

            for key, value in data.items():
                text = f"{key.replace('_', ' ').capitalize()}: {value}"
                c.drawString(50, y, text)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 40

            c.save()

        # Invia PDF via Telegram
        async with bot:
            await bot.send_document(chat_id=CHAT_ID, document=tmp_path.open("rb"), filename=file_name)

        tmp_path.unlink()  # elimina file
        return JSONResponse(status_code=HTTPStatus.OK, content={"status": "OK"})

    except Exception as e:
        print("❌ Errore:", str(e))
        return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.backend:app", host="0.0.0.0", port=PORT, reload=not RAILWAY)

