import streamlit as st
import os
from together import Together

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Add custom CSS for buttons
st.markdown(
    """
    <style>
    .chat-button {
        background-color: #f0f0f5;
        border: 1px solid #ccc;
        color: #333;
        border-radius: 5px;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
    }
    .chat-button:hover {
        background-color: #e0e0eb;
    }
    .chat-column {
        display: inline-block;
        vertical-align: top;
        margin: 0 5px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Together API API Key
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')

    if 'TOGETHER_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        together_api_key = st.secrets['TOGETHER_API_KEY']
    else:
        together_api_key = st.text_input('Enter Together API key:', type='password')

    if not together_api_key:
        st.warning('Please enter your API key!', icon='⚠️')
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')

    os.environ['TOGETHER_API_KEY'] = together_api_key

# Initialize Together API client
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

# Fetch available models from Together
models = client.models.list()
model_names = [model.id for model in models]
model_context_lengths = {model.id: model.context_length for model in models}

st.subheader('Choose a model')
selected_model = st.sidebar.selectbox('Choose a model', model_names, key='selected_model')

temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('max_length', min_value=32, max_value=model_context_lengths.get(selected_model, 2048), value=model_context_lengths.get(selected_model, 120), step=8, key='max_length')

st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = -1

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.edit_mode = -1
    st.experimental_rerun()

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input, temperature, top_p, max_length):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."

    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    messages = [{"role": "user", "content": f"{string_dialogue} {prompt_input} Assistant:"}]

    response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_length,
        repetition_penalty=1.0
    )

    return response.choices[0].message.content

# Display messages with edit and delete buttons
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if st.session_state.edit_mode == i:
            edited_message = st.text_input("Edit message:", value=message["content"], key=f"edited_message_{i}")
            if st.button("Save", key=f"save_{i}"):
                st.session_state.messages[i]["content"] = edited_message
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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt, temperature, top_p, max_length)
                st.write(response)
                message = {"role": "assistant", "content": response}
                st.session_state.messages.append(message)
