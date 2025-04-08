from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional

# Load environment variables
load_dotenv()

# Set up FastAPI app
app = FastAPI()

# Initialize Tavily search instance
search = TavilySearchResults()

# Tool: Always search and summarize the query
def search_and_summarize(query: str) -> str:
    results = search.run(query)
    if not results or not isinstance(results, list):
        return "No relevant search results found."

    summaries = []
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    time_str = datetime.now().strftime("%I:%M %p")

    for r in results[:5]:
        content = r.get("content", "")
        title = r.get("title", "Untitled")
        try:
            summaries.append(f"▶ {title}\n{content[:400]}...\n")
        except UnicodeEncodeError:
            summaries.append(f"▶ {title}\n(Unable to display summary due to encoding error)\n")

    try:
        summaries.insert(0, f"📅 Today's Date: {today_str}\n⏰ Current Time: {time_str}\n")
    except UnicodeEncodeError:
        summaries.insert(0, f"[Date: {today_str}] [Time: {time_str}]\n")

    safe_output = "\n".join(summaries)
    return safe_output.encode("utf-16", "surrogatepass").decode("utf-16", errors="ignore")

# Request body model
class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = "mistral"

@app.post("/run-agent")
async def run_agent(request: QueryRequest):
    try:
        query = request.query
        model_name = request.model or "mistral"

        print("\n===== AGENT INVOCATION =====")
        print(f"[MODEL] Using: {model_name}")
        print(f"[QUERY] {query}\n")

        # Use Tavily directly regardless of prompt
        summary = search_and_summarize(query)
        return {
            "response": summary,
            "model_used": model_name  # log model used in output
        }

    except Exception as e:
        return {"error": str(e)}
