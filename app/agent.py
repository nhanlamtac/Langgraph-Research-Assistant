from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
import logging

# === Import custom tool functions ===
from app.tools.upload_pdf import upload_pdf
from app.tools.internal_search import internal_search
from app.tools.compare_papers import compare_papers
from app.tools.web_search import search_arxiv
from app.tools.list_papers import list_papers

# === Load environment variables (e.g., OpenAI API key) ===
load_dotenv()

# === Initialize the LLM (ChatOpenAI) with temperature for creativity ===
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# === Define available tools for the agent to choose from ===
tools = [
    Tool(name="upload_pdf", func=upload_pdf, description="Upload and store research paper"),
    Tool(name="search_paper", func=internal_search, description="Search papers by topic or keyword"),
    Tool(name="compare_papers", func=compare_papers, description="Compare two papers using their IDs"),
    Tool(name="web_search",
         func=search_arxiv,
         description="Use this tool to search for the most recent research papers on a specific topic from arXiv. Useful for external academic search."),
    Tool(name="list_papers", func=list_papers, description="List all stored papers from the internal database including their IDs and titles"),
]

# === Logging configuration for comparison actions or errors ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/compare_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Create a LangGraph ReAct agent using the LLM and tools ===
agent_executor = create_react_agent(llm, tools=tools)

# === Run the agent with a user query and return the final LLM message ===
def run_agent(query: str) -> str:
    # Invoke the LangGraph agent with a user message and recursion limit
    result = agent_executor.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config={"recursion_limit": 100}
    )
    
    # Debug print of all agent steps (useful for development)
    print("Agent Full Trace:")
    for m in result["messages"]:
        print(m.type, ":", m.content)

    # Return only the final assistant message content
    return result["messages"][-1].content
