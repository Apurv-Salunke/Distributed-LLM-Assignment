from enum import Enum
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

class Model(str, Enum):
    zephyr = "HuggingFaceH4/zephyr-7b-beta"
    llama2 = "meta-llama/Llama-2-7b-chat-hf"
    mistral = "mistralai/Mistral-7B-Instruct-v0.1"

# Model context storage
model_context: Dict[str, List[str]] = {}

class Query(BaseModel):
    model: Model
    prompt: str = Field(..., min_length=1)

class Response(BaseModel):
    response: str

# Set up Hugging Face endpoints
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

def get_context(model: Model) -> List[str]:
    if model.value not in model_context:
        model_context[model.value] = []
    return model_context[model.value]

@app.post("/query", response_model=Response)
async def query_llm(query: Query, context: List[str] = Depends(get_context)):
    context.append(query.prompt)
    full_prompt = "\n".join(context)
    
    try:
        llm = create_llm(query.model)
        template = """Question: {question}
        Answer: Let's think step by step."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        response = llm_chain.invoke(full_prompt)
        
        response_text = response.get('text', '')
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    context.append(response_text)
    
    return Response(response=response_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)