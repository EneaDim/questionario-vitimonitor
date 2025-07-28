# --- COLORI ---
ORANGE=\033[38;5;208m
NC=\033[0m

# --- VARIABILI ---
ifneq (,$(wildcard .env))
	include .env
	export
endif

VENV_DIR=.venv
REQUIREMENTS=requirements.txt
SCRIPT_BACKEND=scripts/backend.py
PORT=5000

# --- TARGETS ---

help:
	@echo ""
	@echo "$(ORANGE)Usage: make [target]$(NC)"
	@echo ""
	@echo "$(ORANGE)Targets:$(NC)"
	@echo "  help             Mostra questo messaggio"
	@echo "  init             Crea .venv e installa dipendenze"
	@echo "  venv             Suggerisce come attivare l'ambiente virtuale"
	@echo "  freeze           Genera $(REQUIREMENTS) aggiornato"
	@echo "  run              Avvia backend Flask su $(PORT)"
	@echo "  test             Simula invio JSON al backend locale"
	@echo "  clean            Rimuove cache Python"
	@echo ""

init:
	@echo "$(ORANGE)🔧 Setup progetto questionario...$(NC)"
	@if [ ! -d $(VENV_DIR) ]; then \
		echo "$(ORANGE)📦 Creo ambiente virtuale $(VENV_DIR)$(NC)"; \
		python3 -m venv $(VENV_DIR); \
	fi
	@echo "$(ORANGE)📥 Installo dipendenze da $(REQUIREMENTS)$(NC)"
	@. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r $(REQUIREMENTS)
	@echo "$(ORANGE)✅ Ambiente pronto$(NC)"

venv:
	@echo "$(ORANGE)✨ Attiva l'ambiente con:$(NC)"
	@echo "source $(VENV_DIR)/bin/activate"

freeze:
	@echo "$(ORANGE)📦 Aggiorno $(REQUIREMENTS)$(NC)"
	@. $(VENV_DIR)/bin/activate && pip freeze > $(REQUIREMENTS)

run:
	@echo "$(ORANGE)🚀 Avvio backend FastAPI$(NC)"
	RAILWAY=$(RAILWAY) TOKEN=$(TOKEN) ADMIN_CHAT_ID=$(ADMIN_CHAT_ID) \
	$(VENV_DIR)/bin/uvicorn scripts.backend:app --host 0.0.0.0 --port $(PORT) --reload

test:
	@echo "$(ORANGE)📤 Invio richiesta JSON di test al backend$(NC)"
	curl -X POST http://localhost:$(PORT)/submit \
	-H "Content-Type: application/json" \
	-d '{"nome": "Mario", "email": "mario@example.com", "superficie": "5", "unita_superficie": "ha"}'

clean:
	@echo "$(ORANGE)🧹 Pulizia file temporanei e cache$(NC)"
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

