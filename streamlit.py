import streamlit as st
from google import genai
from google.genai import types
from pymongo import MongoClient
import concurrent.futures 
import uuid
import datetime
import os


client = genai.Client(api_key="AIzaSyCRCP0EysbC6XLSIy7GIxzjdJ9kXItd5a0")

# Load system instruction
# Read the system prompt from file
# Read system instruction
# Load system instruction
with open("prompt.txt", "r") as file:
    sys_instruct = file.read()

st.title("💬 AI-Powered Patient Report Management")

# Utility: Suggest prompts based on AI response (can enhance later)
def get_prompt_suggestions(user_input, ai_response):
    prompt = f"""
You are a helpful assistant that helps a user navigate medical reports. Based on the following user query and the AI response, suggest 3 to 5 follow-up questions or prompts that the user might ask next.

Format your output as a Python list of strings.

User Message:
\"\"\"{user_input}\"\"\"

AI Response:
\"\"\"{ai_response}\"\"\"

Give only a Python list like:
["Prompt 1", "Prompt 2", "Prompt 3", ...]
"""

    # Use Gemini to generate prompt suggestions
    suggestion_chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction="You are a medical assistant prompt suggester.",response_mime_type="application/json")
    )

    result = suggestion_chat.send_message(prompt)
    print(result.text)

    # Extract the list from LLM output safely
    try:
        suggestions = eval(result.text.strip())
        if isinstance(suggestions, list):
            return suggestions
    except Exception as e:
        print(f"Error extracting suggestions: {e}")
        pass
    
    # Fallback
    return [
        "Summarize patient condition",
        "List all diagnosis date-wise",
        "Show prescribed treatments",
    ]

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=sys_instruct),
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

# Initial greeting
if not st.session_state.messages:
    greeting = "Hi! I'm your AI assistant, here to help you analyze patient report details."
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle typed user input
user_input = st.chat_input("Ask something about the patient report...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = st.session_state.chat_session.send_message(user_input)
        bot_response = response.text

    st.session_state.last_response = bot_response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # Always generate suggestions after any model response
    st.session_state.suggestions = st.session_state.suggestions = get_prompt_suggestions(user_input, bot_response)


    st.rerun()

# Handle suggestion click
if st.session_state.selected_prompt:
    prompt = st.session_state.selected_prompt

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Analyzing..."):
        response = st.session_state.chat_session.send_message(prompt)
        bot_response = response.text

    st.session_state.last_response = bot_response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    with st.chat_message("assistant"):
        st.markdown(bot_response)

    # 🔁 Generate new suggestions after this Gemini response too!
    st.session_state.suggestions = st.session_state.suggestions = get_prompt_suggestions(prompt, bot_response)

    # Reset prompt selection
    st.session_state.selected_prompt = None

    st.rerun()

# Show suggestions below latest AI response
if st.session_state.suggestions and not st.session_state.selected_prompt:
    with st.chat_message("assistant"):
        st.markdown("You can also ask:")
        for i, suggestion in enumerate(st.session_state.suggestions):
            if st.button(suggestion, key=f"suggest_{i}_{st.session_state.session_id}"):
                st.session_state.selected_prompt = suggestion
                st.rerun()
