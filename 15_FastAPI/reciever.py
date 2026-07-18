from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SupportTicket(BaseModel):
    student_name : str
    issue: str

@app.post("/webhooks/support")
def recieve_ticket(ticket: SupportTicket):
    print(ticket)
    #LLM application
    return {
        "status": "recieved",
        "student": ticket.student_name
    }