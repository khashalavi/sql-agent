from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

from .tools import tools
from .tools import langchain_llm 


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=langchain_llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)
