import streamlit as st
from langraph_backend import chatbot , retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

#utility functions

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    current_thread_id = generate_thread_id()
    st.session_state['current_thread_id'] = current_thread_id
    add_thread(st.session_state['current_thread_id'])
    st.session_state['messages_history'] = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state({"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])





#session history
# Initialize chat history in session state because Streamlit runs the script from top to bottom on each interaction, and we need to maintain the chat history across interactions.
if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = []

if 'current_thread_id' not in st.session_state:
    st.session_state['current_thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['current_thread_id'])


#sidebar UI

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(thread_id):
        st.session_state['current_thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                temp_messages.append({"role": "user", "content": msg.content})
            else:
                temp_messages.append({"role": "assistant", "content": msg.content})
        st.session_state['messages_history'] = temp_messages



# loading the conversation history for the current thread
for message in st.session_state["messages_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state["messages_history"].append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.text(user_input)
    
    # Get chatbot response
    # response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    
    # Add chatbot response to chat history
    # st.session_state["messages_history"].append({"role": "assistant", "content": response['messages'][-1].content})
    
    # Display chatbot response

    config  = {'configurable' : {'thread_id' : st.session_state['current_thread_id']}, 
               "metadata" : {"thread_id" : st.session_state['current_thread_id']} , 
               "run_name" : "chat_turn"
               }

    with st.chat_message("assistant"):
        # st.text(response['messages'][-1].content)
        ai_message = st.write_stream( 
            message_chunk.content for message_chunk , metadata in chatbot.stream({
            "messages": [HumanMessage(content=user_input)]} , 
            config=config , 
            stream_mode = "messages"))
        
        st.session_state["messages_history"].append({"role": "assistant", "content": ai_message})


