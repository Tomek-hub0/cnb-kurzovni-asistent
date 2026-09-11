from fastapi import FastAPI
from pydantic import BaseModel
from rag import answer_with_rag
from agent import ask_agent

app = FastAPI(title="ČNB Kurzovní asistent")

@app.get("/health")
def health_check():
    return {"status": "ok"}

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: AskRequest):
    answer = answer_with_rag(request.question)
    return {"question": request.question, "answer": answer}

class AgentRequest(BaseModel):
    question: str

@app.post("/exchange-rate")
def exchange_rate(request: AgentRequest):
    answer = ask_agent(request.question)
    return {"question": request.question, "answer": answer}