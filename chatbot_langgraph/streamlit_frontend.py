import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# st.session_state -> dict ->
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here')

if user_input:
    # 1. Display user message
    with st.chat_message('user'):
        st.text(user_input)
    # 2. Append user message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    
    # 3. Call the LangGraph chatbot backend
    response = chatbot.invoke(
        {'messages': [HumanMessage(content=user_input)]}, 
        config=CONFIG
    )
    
    # 4. Extract the bot's response
    bot_message = response['messages'][-1].content
    
    # 5. Display assistant response
    with st.chat_message('assistant'):
        st.text(bot_message)
    # 6. Append assistant message to history
    st.session_state['message_history'].append({'role': 'assistant', 'content': bot_message})
