from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool
from pydantic import BaseModel as PydanticBaseModel
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import re
from typing import Optional

# Load environment variables
load_dotenv()

# Define tool input schema
class TavilyInput(PydanticBaseModel):
    query: str

# Initialize Tavily search instance
search = TavilySearchResults()

# Improved summarizing wrapper for Tavily results
def search_and_summarize(query: str) -> str:
    results = search.run(query)
    if not results or not isinstance(results, list):
        return "No relevant search results found."

    summaries = []
    cutoff_date = datetime.now() - timedelta(days=7)

    for r in results[:5]:
        content = r.get("content", "")
        title = r.get("title", "Untitled")

        # Try to detect a recent date in the content
        date_match = re.search(r"\\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\.? \\d{1,2}, \\d{4}\\b", content)
        if date_match:
            try:
                parsed_date = datetime.strptime(date_match.group(), "%B %d, %Y")
                if parsed_date < cutoff_date:
                    continue  # skip old content
            except:
                pass  # ignore parse errors

        summaries.append(f"🔹 {title}\n{content[:400]}...\n")

    return "\n".join(summaries) if summaries else "No recent news found in the past week."

# Wrap tool for the agent
tools = [
    Tool.from_function(
        func=search_and_summarize,
        name="tavily_summarized_search",
        description="Perform a web search and return a summarized snippet of recent results from the past week.",
        args_schema=TavilyInput,
        return_direct=True  # Directly respond with summary
    )
]

# Set up FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = "mistral"

@app.post("/run-agent")
async def run_agent(request: QueryRequest):
    try:
        SUPPORTED_MODELS = ["mistral", "llama3", "codellama"]
        model_name = request.model or "mistral"
        if model_name not in SUPPORTED_MODELS:
            return {"error": f"Model '{model_name}' not supported."}

        llm = ChatOllama(model=model_name, base_url="http://localhost:11434")

        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            max_execution_time=60
        )

        result = agent_executor.invoke({"input": request.query})
        response = result.get("output") or str(result)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
