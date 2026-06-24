from langgraph.graph import StateGraph , START , END
from typing import TypedDict , Annotated
from langchain_core.messages import BaseMessage , HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
# from langchain_google_vertexai import ChatVertexAI
from langchain_ollama import ChatOllama
import sqlite3
from dotenv import load_dotenv
load_dotenv()

from langgraph.checkpoint.memory import MemorySaver

from config import MODEL_NAME , API_KEY , SERVICE_ACCOUNT_FILE


import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage] , add_messages]


# llm =  ChatVertexAI(
#         model=MODEL_NAME,
#         temperature=0.3,
#         max_output_tokens=120,
#         thinking_budget=0,
#         include_thoughts=False
#     )

llm = ChatOllama(
    model="llama2",   # matches `ollama list`
    temperature=0.3
)

def chat_node(state: ChatState) -> ChatState:
    message = state['messages']

    response = llm.invoke(message)

    return {'messages' : [response]}


# checkpointer = MemorySaver()
#sqlite checkpointer
conn = sqlite3.connect('chatbot_checkpoints.db' , check_same_thread=False)
checkpointer = SqliteSaver(conn = conn)

graph  = StateGraph(ChatState)

#add nodes

graph.add_node('chat_node' , chat_node)

graph.add_edge(START , 'chat_node')
graph.add_edge('chat_node' , END)


chatbot = graph.compile(checkpointer=checkpointer)

# chatbot.invoke({"messages": [HumanMessage(content="Hello, how are you?")]}, config={"configurable": {"thread_id": "thread_1"}})

# #def retrive all thread
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in  checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])


    return list(all_threads)
