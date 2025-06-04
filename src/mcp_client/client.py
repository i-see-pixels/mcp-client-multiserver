#!/usr/bin/env python

import asyncio
import os 
import sys
import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

class CustomEncoder(json.JSONEncoder):
  def default(self, obj):
    if hasattr(obj, 'content'):
      return {"type": obj.__class__.__name__, "content": obj.content}
    
    return super().default(obj)
  

def read_config_json():
  config_path = os.getenv("MCP_CONFIG_PATH")

  if not config_path:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "mcp_config.json")
    print(f"⚠️ MCP_CONFIG_PATH not set. Using default config path: {config_path}")

  try:
    with open(config_path, 'r') as f:
      config = json.load(f)
      print(f"✅ Loaded MCP config from {config_path}")
      return config
    
  except Exception as e:
    print(f"❌ Error loading MCP config: {e}")
    sys.exit(1)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_retries=2,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

async def run_agent():
  config = read_config_json()
  print("Config: ", config)
  mcp_servers = config["mcp_servers"]
  if not mcp_servers:
    print("❌ No MCP servers found in config.")
    sys.exit(1)
  
  tools = []

  async with AsyncExitStack() as stack:
    for server_name, server_info in mcp_servers.items():
      print(f"\n🔗 Connecting to MCP server: {server_name}")
      server_params = StdioServerParameters(
          command=server_info["command"],
          args=server_info["args"],
      )
      
      try:
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(read, write))

        await session.initialize()

        server_tools = await load_mcp_tools(session)

        for tool in server_tools:
          print(f"\n🔧 Loaded tool: {tool.name} from server {server_name}")
          tools.append(tool)
        
        print(f"\n✅ Successfully connected to {server_name} and loaded {len(server_tools)} tools.")

      except Exception as e:
        print(f"❌ Error connecting to {server_name}: {e}")

    if not tools:
      print("❌ No tools loaded from any MCP servers.")
      return
    
    agent = create_react_agent(llm, tools)

    print("\n🤖 Starting MCP agent loop. Type 'quit' to quit.")

    while True:
      query = input("\nYou: ").strip()

      if query.lower() == "quit":
        print("👋 Exiting agent loop.")
        break

      response = await agent.ainvoke({"messages": query})

      print("\nAgent Response:")

      try:
        formatted_response = json.dumps(response, cls=CustomEncoder, indent=2)
        print(formatted_response)
      except Exception:
        print(str(response))


if __name__ == "__main__":
  asyncio.run(run_agent())