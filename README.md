# ČNB Kurzovní asistent

AI asistent postavený jako REST API, který kombinuje dva přístupy:
- **RAG** – odpovídá na dotazy o finančních pojmech na základě vlastní znalostní báze
- **AI agent** – umí si sám zjistit aktuální kurz měny přes veřejné [API ČNB](https://api.cnb.cz/cnbapi/exrates/daily)

## Endpointy

- `POST /ask` – dotaz na finanční pojmy (deviza, valuta, kurzovní lístek)
- `POST /exchange-rate` – aktuální kurz libovolné měny vůči CZK
- `GET /health` – kontrola dostupnosti
- `GET /docs` – interaktivní dokumentace (Swagger UI)

## Tech stack

Google Gemini API · FastAPI · ChromaDB · Docker · GitHub Actions

## Spuštění lokálně

```bash
git clone https://github.com/<tvoje-jmeno>/cnb-kurzovni-asistent.git
cd cnb-kurzovni-asistent
python -m venv venv
venv\Scripts\Activate.ps1     

pip install -r requirements.txt
```

Vytvoř soubor `.env` s API klíčem (zdarma na [Google AI Studio](https://aistudio.google.com/apikey)):

```
GEMINI_API_KEY=tvuj_api_klic
```

Spuštění:

```bash
uvicorn main:app --reload
```

Appka poběží na `http://127.0.0.1:8000/docs`.

## Spuštění přes Docker

```bash
docker build -t cnb-asistent .
docker run -p 8000:8000 --env-file .env cnb-asistent
```

## Ukázka

```bash
curl -X POST "http://127.0.0.1:8000/exchange-rate" \
  -H "Content-Type: application/json" \
  -d '{"question": "Kolik je aktuálně dolar v korunách?"}'
```

```json
{
  "answer": "Aktuální oficiální kurz amerického dolaru (USD) podle ČNB je 20,88 CZK."
}
```

