from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool
from pydantic import BaseModel as PydanticBaseModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define tool input schema
class TavilyInput(PydanticBaseModel):
    query: str

# Initialize Tavily search instance
search = TavilySearchResults()

# Fancy summarizing wrapper for Tavily results
def search_and_summarize(query: str) -> str:
    results = search.run(query)
    if isinstance(results, list) and results:
        top = results[0]
        title = top.get("title", "No title")
        content = top.get("content", "No content available.")
        return f"{title}\n\nSummary: {content[:500]}..."  # Truncated summary
    return "No relevant search results found."

# Wrap tool for the agent
tools = [
    Tool.from_function(
        func=search_and_summarize,
        name="tavily_summarized_search",
        description="Perform a web search and return a summarized snippet of the top result.",
        args_schema=TavilyInput,
        return_direct=True  # Directly respond with summary
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
    try:
        result = agent_executor.invoke({"input": request.query})
        response = result.get("output") or str(result)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
