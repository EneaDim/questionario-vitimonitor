# 📋 Vitimonitor - Backend Questionario

Questo progetto riceve i dati del questionario da una form HTML, li converte in PDF e li invia tramite un bot Telegram.

## ▶️ Avvio rapido

```bash
make init        # Prepara ambiente virtuale e dipendenze
make run         # Avvia il backend Flask
make test        # Invia una richiesta di test al backend
```

## 📁 Struttura


```
.
├── Makefile            # Comandi automatizzati
├── .env                # Variabili segrete (non va su Git!)
├── requirements.txt    # Dipendenze del progetto
├── scripts/            # Codice bot
│   └── bot_telegram.py
└── backend.py          # Ricezione e gestione del form
```

