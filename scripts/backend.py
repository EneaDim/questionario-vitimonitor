import os
import tempfile
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from telegram import Bot
from dotenv import load_dotenv
import anyio
from pathlib import Path

# Carica variabili da .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("ADMIN_CHAT_ID")
PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=TOKEN)

class PDFHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/submit":
            self.send_error(404, "Endpoint non trovato")
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
            print("✅ Dati ricevuti:", data)

            nome = data.get("nome", "utente").strip().replace(" ", "_")
            email = data.get("email", "anonimo@example.com")
            email_prefix = email.split("@")[0].strip().replace(" ", "_")
            file_name = f"{nome}_{email_prefix}.pdf"

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

            # Invia PDF su Telegram
            async def send_pdf():
                async with bot:
                    await bot.send_document(chat_id=CHAT_ID, document=tmp_path.open("rb"), filename=file_name)

            anyio.run(send_pdf)
            tmp_path.unlink()

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode())
        except Exception as e:
            print("❌ Errore:", str(e))
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == "__main__":
    print(f"🚀 Server in ascolto su http://0.0.0.0:{PORT}/submit")
    server = HTTPServer(("0.0.0.0", PORT), PDFHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server interrotto")

