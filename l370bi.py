# %%
import streamlit as st
import replicate
import os

# %%
# App title
st.set_page_config(page_title="FM Chatbot")

# Replicate Credentials (API token)
with st.sidebar:
    st.title('meta-llama-3-70b-instruct')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

#adjust model parameters
    st.subheader('Models and parameters')
    # selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    # i
    # f selected_model == 'Llama2-7B':
    #     llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    # elif selected_model == 'Llama2-13B':
    #     llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
#session_state: for app rerun for each user, but keep track of the data (user inputs, conversation history)
if "messages" not in st.session_state.keys(): # =first time this session is initialized
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
#role: assistant = this message is from the assistant (chatbot)

# Display or clear chat messages
for message in st.session_state.messages: #iterates through each message stored in the st.session_state.messages list
    with st.chat_message(message["role"]): #Each message is a dictionary containing two keys: "role" (who sent the message)
        st.write(message["content"]) #"content" (the text of the message)

#Function of reset chat history, could be triggered by an action
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history) #add a button

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    #starts with instructions to the model, specifying that it should act as a helpful assistant
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    #loop iterates through each message stored in st.session_state.messages
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            #appends the user's message to string_dialogue with the prefix "User: "
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            #appends the assistant's response with the prefix "Assistant:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    
    #replicate.run: sends a request to the Replicate API to run a specific model
    
    # output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
    #                        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
    #                               "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    
    output = replicate.run('meta/meta-llama-3-70b-instruct', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api): #chat_input = text box, not allowed to input message if without key
    st.session_state.messages.append({"role": "user", "content": prompt}) #adds the user's message to the chat history
    #displays the user's message in the chat interface
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)


