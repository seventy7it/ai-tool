from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType, Tool

# Define the search tool with correct name/description
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

# Build the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)

# Prompt user for input
query = input("💬 Enter your search prompt: ")
result = agent.run(query)

import os
import datetime

# Define output directory
output_dir = os.path.expanduser("~/my-docs/outputs")
os.makedirs(output_dir, exist_ok=True)  # Create it if it doesn't exist

# Create timestamped filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"ai_output_{timestamp}.txt"
filepath = os.path.join(output_dir, filename)

# Write result to file
with open(filepath, "w") as f:
    f.write(result)

print(f"✅ Output saved to: {filepath}")

# Save the input + output to a uniquely named file
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, f"ai_output_{timestamp}.txt")

with open(filename, "w") as f:
    f.write(f"🧠 Prompt:\n{query}\n\n📝 Response:\n{result}\n")

print(f"\n✅ Output saved to: {filename}\n")
os.system(f"cat {filename}")

# Automatically display the file contents
with open(filepath, "r") as f:
    print(f.read())
