from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool
from dotenv import load_dotenv
import os
import datetime
import sys

# Load environment variables
load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")

# Define the Tavily search tool
search = TavilySearchResults()
tools = [
    Tool.from_function(
        func=search.run,
        name="tavily_search_results_json",
        description="Useful for answering questions by searching the web for recent or real-time information."
    )
]

# Initialize the model
llm = ChatOllama(model="mistral", base_url="http://localhost:11434")

# Set up the agent
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=15,
    max_execution_time=60
)

# Get query from input or fallback
if sys.stdin.isatty():
    query = input("💬 Enter your search prompt: ")
else:
    query = "summarize the latest headlines from this morning"

# Run the agent
response = agent_executor.invoke({"input": query})
result = response["output"] if "output" in response else str(response)

# Save to file
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.expanduser("~/my-docs/outputs")
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, f"ai_output_{timestamp}.txt")

with open(filepath, "w") as f:
    f.write(f"🧠 Prompt:\n{query}\n\n📝 Response:\n{result}\n")

print(f"\n✅ Output saved to: {filepath}\n")

# Display the file contents
os.system(f"cat {filepath}")
