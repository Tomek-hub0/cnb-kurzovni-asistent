import os
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3.8-flash"

# Prozatím naše testovací znalostní báze - později nahradíme reálnými ČNB texty
chunks = [
    "Deviza je bezhotovostní pohledávka znějící na cizí měnu, například peníze na bankovním účtu. Kurz deviza se používá pro bezhotovostní platby.",
    "Valuta je hotovostní cizí měna, tedy fyzické bankovky a mince. Kurz valuta se používá při směně hotovosti, například na pobočce banky.",
    "Kurzovní lístek ČNB se aktualizuje jednou denně, obvykle kolem 14:30 v pracovní dny.",
]

def get_document_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return result.embeddings[0].values

def get_query_embedding(text):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return result.embeddings[0].values

# Připravíme databázi jednou při startu aplikace
embeddings = [get_document_embedding(chunk) for chunk in chunks]
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="cnb_znalosti")
collection.add(
    ids=[str(i) for i in range(len(chunks))],
    embeddings=embeddings,
    documents=chunks,
)


def answer_with_rag(question):
    query_embedding = get_query_embedding(question)
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    relevant_chunks = results["documents"][0]

    context = "\n\n".join(relevant_chunks)
    prompt = f"""Odpověz na otázku POUZE na základě následujícího kontextu.Pokud odpověď v kontextu není, řekni, že to nevíš.

    Kontext: {context}

    Otázka: {question}"""

    interaction = client.interactions.create(model=MODEL, input=prompt)
    return interaction.output_text