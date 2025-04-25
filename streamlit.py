import streamlit as st
from google import genai
from google.genai import types
from pymongo import MongoClient
import concurrent.futures 
import uuid
import datetime
import os

#COLLECTION_NAME = "conversations"

# GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
# MONGO_URI = st.secrets["MONGO_URI"]
# DB_NAME = "transaction_chatbot"

# client_mongo = MongoClient(MONGO_URI)
# db = client_mongo[DB_NAME]
#collection = db[COLLECTION_NAME]
# Initialize Google Generative AI Client
client = genai.Client(api_key="AIzaSyCRCP0EysbC6XLSIy7GIxzjdJ9kXItd5a0")

#read the prompt.txt and assign to sys_instruct
with open("prompt.txt", "r") as file:
    sys_instruct = file.read()
# System Instruction for AI Agent
#sys_instruct = """"""
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)


# def save_to_mongodb_async(session_id, user_msg, bot_response):
#     """Save conversation data asynchronously using a separate thread."""
#     def save():
#         session_collection = db[f"session_{session_id}"]
#         conversation_entry = {
#             "session_id": session_id,
#             "timestamp": datetime.datetime.utcnow(),
#             "user_message": user_msg,
#             "bot_response": bot_response
#         }
#         session_collection.insert_one(conversation_entry)
#     # Execute save operation asynchronously
#     executor.submit(save)
# Initialize Streamlit UI
st.title("💬 AI-Powered Patient Report Managment")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat session in session_state
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct,
            #tools=[types.Tool(google_search=types.GoogleSearchRetrieval)],
        ),
    )

# Initialize messages history
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    greeting_message = """Hi! I'm your AI assistant, here to help you to analyze patient report details."""
    st.session_state.messages.append({"role": "assistant", "content": greeting_message})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Hi!")

if user_input:
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Use the stored chat session instead of creating a new one
    response = st.session_state.chat_session.send_message(user_input)

    # Extract response text
    bot_response = response.text
    # Append bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
     # Display bot response
    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # save_to_mongodb_async(st.session_state.session_id, user_input, bot_response)

   
