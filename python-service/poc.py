from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain import PromptTemplate, LLMChain
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)

question="Who won the Cricket World Cup in the year 2011?"
template = """Question: {question}
Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])
print(prompt)


llm_chain=LLMChain(llm=llm,prompt=prompt)
print(llm_chain.invoke(question))