import os
from enum import Enum
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

class Model(str, Enum):
    mistral = "mistralai/Mistral-Nemo-Instruct-2407"
    llama2 = "meta-llama/Llama-2-7b-chat-hf"

class Query(BaseModel):
    prompt: str = Field(..., min_length=1)

class Response(BaseModel):
    response: str

# Global variable to store the selected model
SELECTED_MODEL: Model = None

# Conversation history
conversation_history: Dict[str, List[Dict[str, str]]] = {
    Model.llama2.value: [],
    Model.mistral.value: []
}

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
        
        # Prepare context from conversation history
        context = "\n".join([f"Human: {item['human']}\nAI: {item['ai']}" for item in conversation_history[SELECTED_MODEL.value]])
        
        full_prompt = f"{context}\nHuman: {query.prompt}\nAI:"
        
        template = """{full_prompt}
        Answer: Let's think step by step."""
        prompt = PromptTemplate(template=template, input_variables=["full_prompt"])
        
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        response = llm_chain.invoke({"full_prompt": full_prompt})
        
        response_text = response.get('text', '').strip()
        
        # Update conversation history
        conversation_history[SELECTED_MODEL.value].append({
            "human": query.prompt,
            "ai": response_text
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return Response(response=response_text)

@app.get("/conversation_history")
async def get_conversation_history():
    if not SELECTED_MODEL:
        raise HTTPException(status_code=400, detail="No model selected. Please select a model first.")
    return conversation_history[SELECTED_MODEL.value]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)