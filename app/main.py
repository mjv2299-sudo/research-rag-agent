from . import config  # loads .env
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import run_research

app = FastAPI(title="Research Agent")

class ResearchIn(BaseModel):
    question: str

@app.post("/research")
async def research(inp: ResearchIn):
    q = inp.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="question is required")
    report = await run_research(q)
    return report