from datetime import datetime
import os
from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import uvicorn
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    model = Column(String, index=True)
    human = Column(String)
    ai = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class Model(str, Enum):
    mistral = "mistralai/Mistral-Nemo-Instruct-2407"
    llama2 = "meta-llama/Llama-2-7b-chat-hf"

class Query(BaseModel):
    prompt: str = Field(..., min_length=1)

class Response(BaseModel):
    response: str

def create_llm(model: Model) -> HuggingFaceEndpoint:
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

    return HuggingFaceEndpoint(
        repo_id=model.value,
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
        huggingfacehub_api_token=api_key,
    )

@app.post("/select_model")
async def select_model(model: Model):
    global SELECTED_MODEL
    SELECTED_MODEL = model
    return {"message": f"Model selected: {model.value}"}

@app.post("/query", response_model=Response)
async def query_llm(query: Query):
    if not SELECTED_MODEL:
        raise HTTPException(status_code=400, detail="No model selected. Please select a model first.")

    try:
        llm = create_llm(SELECTED_MODEL)

        # Retrieve context from conversation history
        db = SessionLocal()
        context_entries = db.query(Conversation).filter_by(model=SELECTED_MODEL.value).order_by(Conversation.timestamp.asc()).all()
        db.close()
        
        context = "\n".join([f"Human: {item.human}\nAI: {item.ai}" for item in context_entries])
        
        full_prompt = f"{context}\nHuman: {query.prompt}\nAI:"
        
        template = """{full_prompt}
        Answer: Let's think step by step."""
        prompt = PromptTemplate(template=template, input_variables=["full_prompt"])
        
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        response = llm_chain.invoke({"full_prompt": full_prompt})
        
        response_text = response.get('text', '').strip()
        
        # Store conversation in database
        db = SessionLocal()
        new_conversation = Conversation(
            id=f"{datetime.utcnow().timestamp()}",
            model=SELECTED_MODEL.value,
            human=query.prompt,
            ai=response_text
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        db.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(response=response_text)

@app.get("/conversation_history")
async def get_conversation_history():
    if not SELECTED_MODEL:
        raise HTTPException(status_code=400, detail="No model selected. Please select a model first.")

    db = SessionLocal()
    history = db.query(Conversation).filter_by(model=SELECTED_MODEL.value).order_by(Conversation.timestamp.desc()).all()
    db.close()

    return [
        {
            "human": item.human,
            "ai": item.ai,
            "timestamp": item.timestamp.isoformat()
        } for item in history
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
