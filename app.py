import streamlit as st
import os
import json
from together import Together

# App title
st.set_page_config(page_title="💬 AI Chatbot")
st.set_page_config(page_title="🧠💬 AI Chatbot")

# Add custom CSS for buttons
st.markdown(
@@ -26,48 +27,117 @@
        vertical-align: top;
        margin: 0 5px;
    }
    .message-button {
        display: inline-block;
        vertical-align: bottom;
        margin-left: 10px;
        font-size: 12px;
        cursor: pointer;
    }
    </style>
    """, 
    """,
    unsafe_allow_html=True
)

# Together API API Key
with st.sidebar:
    st.title('💬 AI Chatbot')
    st.write('This chatbot is created using the open-source Models.')

    if 'TOGETHER_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        together_api_key = st.secrets['TOGETHER_API_KEY']
    else:
        together_api_key = st.text_input('Enter Together API key:', type='password')
    st.title('🧠💬 AI Chatbot')
    st.write('This chatbot is created using the open-source LLM models from Together.Ai.')

    if not together_api_key:
        st.warning('Please enter your API key!', icon='⚠️')
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')

    os.environ['TOGETHER_API_KEY'] = together_api_key
    together_api_key = "06ae5e599e89f3dc4a8b52f53432c9811567c5341238b8479c96ff45d5861b88"

# Initialize Together API client
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
client = Together(api_key=together_api_key)

# Fetch available models from Together
models = client.models.list()
model_names = [model.id for model in models]
model_context_lengths = {model.id: model.context_length for model in models}

st.subheader('Chat Here')
selected_model = st.sidebar.selectbox('Choose a model', model_names, key='selected_model')
# Load and Save Chat Sessions
session_file = 'chat_sessions.json'

def load_sessions():
    if os.path.exists(session_file):
        with open(session_file, 'r') as file:
            return json.load(file)
    return {}

def save_sessions(sessions):
    with open(session_file, 'w') as file:
        json.dump(sessions, file)

sessions = load_sessions()

# Sidebar Chat History
st.sidebar.subheader('Chat History')
session_to_load = None
for session_name in sessions:
    if st.sidebar.button(session_name):
        session_to_load = session_name

new_session_name = st.sidebar.text_input('Save current session as:')
if st.sidebar.button('Save Session'):
    if new_session_name:
        sessions[new_session_name] = {
            "messages": st.session_state.messages,
            "model": st.session_state.selected_model,
            "temperature": st.session_state.temperature,
            "top_p": st.session_state.top_p,
            "max_length": st.session_state.max_length
        }
        save_sessions(sessions)
        st.sidebar.success(f'Session saved as {new_session_name}')
    else:
        st.sidebar.error('Please enter a session name')

# Save Current Session Button
if st.sidebar.button('Save Current Session'):
    current_session_name = st.sidebar.selectbox('Select Session to Save', options=list(sessions.keys()))
    if current_session_name:
        sessions[current_session_name] = {
            "messages": st.session_state.messages,
            "model": st.session_state.selected_model,
            "temperature": st.session_state.temperature,
            "top_p": st.session_state.top_p,
            "max_length": st.session_state.max_length
        }
        save_sessions(sessions)
        st.sidebar.success(f'Session {current_session_name} updated!')

# New Chat Button
if st.sidebar.button('New Chat'):
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.edit_mode = -1
    st.session_state.selected_model = model_names[0]
    st.session_state.temperature = 0.1
    st.session_state.top_p = 0.9
    st.session_state.max_length = 120
    st.experimental_rerun()

temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('max_length', min_value=32, max_value=model_context_lengths.get(selected_model, 2048), value=model_context_lengths.get(selected_model, 120), step=8, key='max_length')
# Model Settings
if session_to_load:
    session = sessions[session_to_load]
    st.session_state.messages = session["messages"]
    st.session_state.selected_model = session["model"]
    st.session_state.temperature = session["temperature"]
    st.session_state.top_p = session["top_p"]
    st.session_state.max_length = session["max_length"]

st.markdown('📖 Use it as you wish')
selected_model = st.sidebar.selectbox('Choose a model', model_names, key='selected_model')
st.session_state.temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=st.session_state.get('temperature', 0.1), step=0.01)
st.session_state.top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=st.session_state.get('top_p', 0.9), step=0.01)
st.session_state.max_length = st.sidebar.slider('max_length', min_value=32, max_value=model_context_lengths.get(selected_model, 2048), value=st.session_state.get('max_length', 120), step=8)

# Chat Heading
if session_to_load:
    st.header(f"Chat: {session_to_load}")
else:
    st.header("New Chat")
st.markdown("---")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = -1
@@ -105,24 +175,34 @@ def generate_llama2_response(prompt_input, temperature, top_p, max_length):
# Display messages with edit and delete buttons
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if st.session_state.edit_mode == i:
            edited_message = st.text_input("Edit message:", value=message["content"], key=f"edited_message_{i}")
            if st.button("Save", key=f"save_{i}"):
                st.session_state.messages[i]["content"] = edited_message
        st.write(message["content"])
        edit_col, delete_col = st.columns([1, 1])
        with edit_col:
            if st.button("✏️", key=f"edit_{i}", help="Edit this message", use_container_width=True):
                st.session_state.edit_mode = i
        with delete_col:
            if st.button("🗑️", key=f"delete_{i}", help="Delete this message", use_container_width=True):
                del st.session_state.messages[i]
                st.session_state.edit_mode = -1
                st.experimental_rerun()
                break

# Edit message modal using expander and form
if st.session_state.edit_mode != -1:
    with st.expander("Edit Message", expanded=True):
        with st.form("edit_message_form"):
            role = st.session_state.messages[st.session_state.edit_mode]["role"]
            st.subheader(f"Edit {role} message")
            edited_message = st.text_area("Message", value=st.session_state.messages[st.session_state.edit_mode]["content"])
            save_button = st.form_submit_button("💾 Save")
            cancel_button = st.form_submit_button("Cancel")
            if save_button:
                st.session_state.messages[st.session_state.edit_mode]["content"] = edited_message
                st.session_state.edit_mode = -1
                st.experimental_rerun()
            elif cancel_button:
                st.session_state.edit_mode = -1
                st.experimental_rerun()
        else:
            st.write(message["content"])
            cols = st.columns([1, 1])
            with cols[0]:
                if st.button("Edit", key=f"edit_{i}", help="Edit this message"):
                    st.session_state.edit_mode = i
                    st.experimental_rerun()
            with cols[1]:
                if st.button("Delete", key=f"delete_{i}", help="Delete this message"):
                    del st.session_state.messages[i]
                    st.experimental_rerun()
                    break

# User-provided prompt
if prompt := st.chat_input(disabled=not together_api_key):
@@ -134,7 +214,7 @@ def generate_llama2_response(prompt_input, temperature, top_p, max_length):
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt, temperature, top_p, max_length)
                response = generate_llama2_response(prompt, st.session_state.temperature, st.session_state.top_p, st.session_state.max_length)
                st.write(response)
                message = {"role": "assistant", "content": response}
                st.session_state.messages.append(message)
