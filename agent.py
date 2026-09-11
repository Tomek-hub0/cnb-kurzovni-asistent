import os
import json
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.8-flash"

exchange_rate_function = {
    "type": "function",
    "name": "get_exchange_rate",
    "description": "Vrátí aktuální oficiální kurz dané měny vůči české koruně podle ČNB.",
    "parameters": {
        "type": "object",
        "properties": {
            "currency_code": {
                "type": "string",
                "description": "Třípísmenný ISO kód měny, např. 'USD', 'EUR', 'GBP'.",
            },
        },
        "required": ["currency_code"],
    },
}


def get_exchange_rate(currency_code):
    response = requests.get(
        "https://api.cnb.cz/cnbapi/exrates/daily",
        params={"lang": "EN"},
        timeout=10,  
    )
    response.raise_for_status()
    data = response.json()

    for entry in data["rates"]:
        if entry["currencyCode"] == currency_code.upper():
            return {
                "currency": entry["currencyCode"],
                "country": entry["country"],
                "amount": entry["amount"],
                "rate_czk": entry["rate"],
            }

    return {"error": f"Měna {currency_code} nebyla nalezena."}


def ask_agent(question):
    current_interaction = client.interactions.create(
        model=MODEL,
        input=question,
        tools=[exchange_rate_function],
    )

    max_kola = 5
    kolo = 0

    while kolo < max_kola:
        kolo += 1
        fc_step = None
        for step in current_interaction.steps:
            if step.type == "function_call":
                fc_step = step
                break

        if fc_step is None:
            return current_interaction.output_text

        result = get_exchange_rate(**fc_step.arguments)

        current_interaction = client.interactions.create(
            model=MODEL,
            input=[{
                "type": "function_result",
                "name": fc_step.name,
                "call_id": fc_step.id,
                "result": [{"type": "text", "text": json.dumps(result)}],
            }],
            tools=[exchange_rate_function],
            previous_interaction_id=current_interaction.id,
        )

    return "Omlouvám se, nepodařilo se mi zjistit odpověď (příliš mnoho pokusů)."