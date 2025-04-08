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

# Tool: Always search and summarize the query
# Let the model decide what's most relevant

def search_and_summarize(query: str) -> str:
    results = search.run(query)
    if not results or not isinstance(results, list):
        return "No relevant search results found."

    summaries = []
    cutoff_date = datetime.now() - timedelta(days=7)
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    time_str = datetime.now().strftime("%I:%M %p")

    for r in results[:5]:
        content = r.get("content", "")
        title = r.get("title", "Untitled")

        # Normalize whitespace for better date detection
        content_cleaned = re.sub(r"\s+", " ", content)

        # Try to detect a recent date in the content
        date_match = re.search(r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) \d{1,2}, \d{4}\b", content_cleaned)
        if date_match:
            try:
                parsed_date = datetime.strptime(date_match.group(), "%B %d, %Y")
                if parsed_date < cutoff_date:
                    continue  # skip old content
            except:
                pass  # ignore parse errors

        try:
            summaries.append(f"▶ {title}\n{content[:400]}...\n")
        except UnicodeEncodeError:
            summaries.append(f"▶ {title}\n(Unable to display summary due to encoding error)\n")

    try:
        summaries.insert(0, f"📅 Today's Date: {today_str}\n⏰ Current Time: {time_str}\n")
    except UnicodeEncodeError:
        summaries.insert(0, f"[Date: {today_str}] [Time: {time_str}]\n")

    # Strip or replace any invalid surrogate characters
    safe_output = "\n".join(summaries)
    return safe_output.encode("utf-16", "surrogatepass").decode("utf-16", errors="ignore")

# Tool: Get current date and time

def get_current_datetime(input: Optional[str] = None) -> str:
    now = datetime.now()
    return f"📅 Today is {now.strftime('%A, %B %d, %Y')} and the current time is {now.strftime('%I:%M %p')}"

# Wrap tools for the agent
tools = [
    Tool.from_function(
        func=search_and_summarize,
        name="tavily_summarized_search",
        description="Search the web and summarize relevant current or recent information. Always use this tool to gather context before answering a query.",
        args_schema=TavilyInput,
        return_direct=True
    ),
    Tool.from_function(
        func=get_current_datetime,
        name="get_current_datetime",
        description="Use this to answer any question about today's date or current time.",
        return_direct=True
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

        # Prepend guidance so the agent always uses the tools
        now_full = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

final_prompt = (
    f"You are an assistant with access to web search and current datetime tools.\n"
    f"Today is {now_full}.\n"
    f"Answer the user's question using your tools if needed, otherwise answer directly.\n"
    f"Question: {request.query}"
)
        result = agent_executor.invoke({"input": final_prompt})
        response = result.get("output") or str(result)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
