import os
import tempfile
import json
import anyio
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from telegram import Bot
from dotenv import load_dotenv
from pathlib import Path
import markdown2
import pdfkit

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
            file_stem = f"{nome}_{email_prefix}"

            # 1. 📝 Crea contenuto Markdown
            markdown_content = f"# 📋 Questionario Vitimonitor\n\n"
            for key, value in data.items():
                label = key.replace("_", " ").capitalize()
                markdown_content += f"- **{label}**: {value}\n"
            html = markdown2.markdown(markdown_content)

            # 2. 🧾 Salva Markdown in file temporaneo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                pdf_path = Path(pdf_file.name)
                pdfkit.from_string(html, str(pdf_path))

            # 3. 🖨️ Converti Markdown in HTML, poi in PDF
            html = markdown2.markdown(markdown_content)
            response = requests.post(
                "https://api.html2pdf.app/v1/generate",
                json={
                    "html": html,
                    "apiKey": "TUA_API_KEY"
                }
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(response.content)

            # 4. 📤 Invia PDF su Telegram
            async def send_pdf():
                async with bot:
                    await bot.send_document(chat_id=CHAT_ID, document=pdf_path.open("rb"), filename=f"{file_stem}.pdf")

            anyio.run(send_pdf)

            # 5. 🧹 Pulizia
            md_path.unlink()
            pdf_path.unlink()

            # 6. ✅ Risposta HTTP
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode())

        except Exception as e:
            print("❌ Errore:", str(e))
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

if __name__ == "__main__":
    print(f"🚀 Server in ascolto su http://0.0.0.0:{PORT}")
    server = HTTPServer(("0.0.0.0", PORT), PDFHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server interrotto")

