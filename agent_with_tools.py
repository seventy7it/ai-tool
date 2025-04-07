from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Tavily and tools
search = TavilySearchResults()
tools = [
    Tool.from_function(
        func=search.run,
        name="tavily_search_results_json",
        description="Web search for recent or real-time information."
    )
]

# Initialize model and agent
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=15,
    max_execution_time=60
)

# Set up FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/run-agent")
async def run_agent(request: QueryRequest):
    result = agent_executor.invoke({"input": request.query})
    response = result["output"] if "output" in result else str(result)
    return {"response": response}
