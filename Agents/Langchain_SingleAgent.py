"""
LangChain Single Agent with Tools
Updated for LangChain 1.0+ compatibility
"""

import os
import asyncio
import nest_asyncio
from typing import Any

# Allow nested event loops (needed for Jupyter/notebooks)
nest_asyncio.apply()

# Set the OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = ""

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage

# Try old API imports first (simpler)
try:
    from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
    from langchain.agents import AgentExecutor
    USE_OLD_API = True
    print("Using old LangChain API (AgentExecutor)")
except ImportError:
    USE_OLD_API = False
    print("Old API not available, using simple agent implementation...")

# Try new API imports
try:
    from langchain.agents import create_agent
    USE_NEW_API = True
    print("New API (create_agent) available")
except ImportError:
    USE_NEW_API = False
    print("New API not available")

# Simple format function for tool messages (for old API)
def format_to_openai_tool_messages(intermediate_steps):
    """Format intermediate steps to OpenAI tool messages."""
    messages = []
    for agent_action, observation in intermediate_steps:
        if hasattr(agent_action, 'tool_calls') and agent_action.tool_calls:
            messages.append(AIMessage(content="", tool_calls=agent_action.tool_calls))
            for tool_call in agent_action.tool_calls:
                tool_call_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, "id", None)
                messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call_id))
        elif hasattr(agent_action, 'tool') and hasattr(agent_action, 'tool_input'):
            from langchain_core.messages.tool import ToolCall
            tool_call = ToolCall(
                name=agent_action.tool,
                args=agent_action.tool_input if isinstance(agent_action.tool_input, dict) else {"input": agent_action.tool_input},
                id=f"call_{len(messages)}"
            )
            messages.append(AIMessage(content="", tool_calls=[tool_call]))
            messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    return messages

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

tool_usage_log = []

def log_tool_usage(tool_name: str, input_data: Any):
    """Logs the tool used and its input."""
    tool_usage_log.append({"tool": tool_name, "input": input_data})

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    log_tool_usage("get_word_length", word)
    return len(word)

@tool
def calculator(expression: str) -> str:
    """Evaluates mathematical expression"""
    log_tool_usage("calculator", expression)
    try:
        maths_result = eval(expression)
        return str(maths_result)
    except Exception as e:
        return f"Error: {str(e)}"

tools = [get_word_length, calculator]

# Create agent based on available API
if USE_OLD_API:
    # Use old AgentExecutor API (simplest)
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are very powerful assistant, but bad at calculating lengths of words and mathematical expressions",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
elif USE_NEW_API:
    # Use new create_agent API (LangGraph-based)
    agent_graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are very powerful assistant, but bad at calculating lengths of words and mathematical expressions"
    )
    
    # Simple wrapper to make LangGraph work like AgentExecutor
    class SimpleAgentExecutor:
        def __init__(self, agent_graph):
            self.agent_graph = agent_graph
            self.verbose = True
            
        def invoke(self, input_dict):
            """Invoke the agent with input dictionary."""
            messages = input_dict.get("chat_history", []) + [HumanMessage(content=input_dict.get("input", ""))]
            result = self.agent_graph.invoke({"messages": messages})
            
            # Extract the last AI message content
            result_messages = result.get("messages", [])
            output = ""
            for msg in reversed(result_messages):
                if isinstance(msg, AIMessage):
                    output = msg.content or ""
                    break
            
            return {"output": output}
    
    agent_executor = SimpleAgentExecutor(agent_graph)
    
else:
    # Simple agent implementation without AgentExecutor - old API style
    tools_dict = {tool.name: tool for tool in tools}
    
    class SimpleAgentExecutor:
        def __init__(self, llm, tools, system_prompt):
            self.llm = llm.bind_tools(tools)
            self.tools = tools_dict
            self.system_prompt = system_prompt
            self.verbose = True
            
        def invoke(self, input_dict):
            """Simple agent loop - similar to old API style."""
            messages = list(input_dict.get("chat_history", []))
            user_input = input_dict.get("input", "")
            
            # Build message list with system prompt
            conversation_messages = [SystemMessage(content=self.system_prompt)]
            conversation_messages.extend(messages)
            conversation_messages.append(HumanMessage(content=user_input))
            
            max_iterations = 10
            for _ in range(max_iterations):
                # Get LLM response
                response = self.llm.invoke(conversation_messages)
                conversation_messages.append(response)
                
                # Check if there are tool calls
                if not response.tool_calls:
                    # No more tool calls, return the response
                    return {"output": response.content or ""}
                
                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    
                    if tool_name in self.tools:
                        tool_result = self.tools[tool_name].invoke(tool_args)
                        conversation_messages.append(ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        ))
                    else:
                        conversation_messages.append(ToolMessage(
                            content=f"Tool {tool_name} not found",
                            tool_call_id=tool_call["id"]
                        ))
            
            # If we've exhausted iterations, return the last response
            last_ai_msg = None
            for msg in reversed(conversation_messages):
                if isinstance(msg, AIMessage):
                    last_ai_msg = msg
                    break
            return {"output": last_ai_msg.content if last_ai_msg else "Error: No response generated"}
    
    agent_executor = SimpleAgentExecutor(
        llm=llm,
        tools=tools,
        system_prompt="You are very powerful assistant, but bad at calculating lengths of words and mathematical expressions"
    )


async def main():
    chat_history = []
    while True:
        print("Enter question or type exit to quit")
        input1 = input("User: ")

        if input1.lower() == "exit":
            print("Exiting the chat.")
            break

        # Clear tool usage log for this interaction
        tool_usage_log.clear()
        
        # Invoke agent (synchronous call)
        result = agent_executor.invoke({"input": input1, "chat_history": chat_history})

        # Update chat history with user input and AI response
        chat_history.append(HumanMessage(content=input1))
        chat_history.append(AIMessage(content=result["output"]))
        
        # Keep chat history manageable (optional: limit to last N messages)
        if len(chat_history) > 20:  # Keep last 10 exchanges
            chat_history = chat_history[-20:]
        
        print("\nTools Used:")
        if tool_usage_log:
            for usage in tool_usage_log:
                print(f"Tool: {usage['tool']}, Input: {usage['input']}")
        else:
            print("No tools were used in this interaction.")
            
        print("\n\n Message:\n", result["output"])

if __name__ == "__main__":
    # For Jupyter/notebooks, use asyncio.run with nest_asyncio
    # For regular Python scripts, you can use asyncio.run(main())
    asyncio.run(main())
