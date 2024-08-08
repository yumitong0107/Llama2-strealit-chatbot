{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import streamlit as st\n",
    "import replicate\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "os.environ['api_token'] = \"r8_ARB5x85ncfGHWbbe0gy4avAO2mZfltK4GEcNR\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2024-08-08 19:06:02.696 Session state does not function when running a script without `streamlit run`\n"
     ]
    }
   ],
   "source": [
    "# App title\n",
    "st.set_page_config(page_title=\"FM Chatbot\")\n",
    "\n",
    "# Replicate Credentials (API token)\n",
    "with st.sidebar:\n",
    "    st.title('FM Chatbot')\n",
    "    if 'REPLICATE_API_TOKEN' in st.secrets:\n",
    "        st.success('API key already provided!', icon='✅')\n",
    "        replicate_api = st.secrets['REPLICATE_API_TOKEN']\n",
    "    else:\n",
    "        replicate_api = st.text_input('Enter Replicate API token:', type='password')\n",
    "        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):\n",
    "            st.warning('Please enter your credentials!', icon='⚠️')\n",
    "        else:\n",
    "            st.success('Proceed to entering your prompt message!', icon='👉')\n",
    "    os.environ['REPLICATE_API_TOKEN'] = replicate_api\n",
    "\n",
    "#adjust model parameters\n",
    "    st.subheader('Models and parameters')\n",
    "    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')\n",
    "    if selected_model == 'Llama2-7B':\n",
    "        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'\n",
    "    elif selected_model == 'Llama2-13B':\n",
    "        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'\n",
    "    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)\n",
    "    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)\n",
    "    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)\n",
    "    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')\n",
    "\n",
    "# Store LLM generated responses\n",
    "#session_state: for app rerun for each user, but keep track of the data (user inputs, conversation history)\n",
    "if \"messages\" not in st.session_state.keys(): # =first time this session is initialized\n",
    "    st.session_state.messages = [{\"role\": \"assistant\", \"content\": \"How may I assist you today?\"}]\n",
    "#role: assistant = this message is from the assistant (chatbot)\n",
    "\n",
    "# Display or clear chat messages\n",
    "for message in st.session_state.messages: #iterates through each message stored in the st.session_state.messages list\n",
    "    with st.chat_message(message[\"role\"]): #Each message is a dictionary containing two keys: \"role\" (who sent the message)\n",
    "        st.write(message[\"content\"]) #\"content\" (the text of the message)\n",
    "\n",
    "#Function of reset chat history, could be triggered by an action\n",
    "def clear_chat_history():\n",
    "    st.session_state.messages = [{\"role\": \"assistant\", \"content\": \"How may I assist you today?\"}]\n",
    "st.sidebar.button('Clear Chat History', on_click=clear_chat_history) #add a button\n",
    "\n",
    "# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot\n",
    "def generate_llama2_response(prompt_input):\n",
    "    #starts with instructions to the model, specifying that it should act as a helpful assistant\n",
    "    string_dialogue = \"You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'.\"\n",
    "    #loop iterates through each message stored in st.session_state.messages\n",
    "    for dict_message in st.session_state.messages:\n",
    "        if dict_message[\"role\"] == \"user\":\n",
    "            #appends the user's message to string_dialogue with the prefix \"User: \"\n",
    "            string_dialogue += \"User: \" + dict_message[\"content\"] + \"\\n\\n\"\n",
    "        else:\n",
    "            #appends the assistant's response with the prefix \"Assistant:\n",
    "            string_dialogue += \"Assistant: \" + dict_message[\"content\"] + \"\\n\\n\"\n",
    "    \n",
    "    #replicate.run: sends a request to the Replicate API to run a specific model\n",
    "    \n",
    "    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', \n",
    "                           input={\"prompt\": f\"{string_dialogue} {prompt_input} Assistant: \",\n",
    "                                  \"temperature\":temperature, \"top_p\":top_p, \"max_length\":max_length, \"repetition_penalty\":1})\n",
    "    \n",
    "    # output = replicate.run('meta/meta-llama-3-70b-instruct', \n",
    "    #                        input={\"prompt\": f\"{string_dialogue} {prompt_input} Assistant: \",\n",
    "    #                               \"temperature\":temperature, \"top_p\":top_p, \"max_length\":max_length, \"repetition_penalty\":1})\n",
    "    return output\n",
    "\n",
    "# User-provided prompt\n",
    "if prompt := st.chat_input(disabled=not replicate_api): #chat_input = text box, not allowed to input message if without key\n",
    "    st.session_state.messages.append({\"role\": \"user\", \"content\": prompt}) #adds the user's message to the chat history\n",
    "    #displays the user's message in the chat interface\n",
    "    with st.chat_message(\"user\"):\n",
    "        st.write(prompt)\n",
    "\n",
    "# Generate a new response if last message is not from assistant\n",
    "if st.session_state.messages[-1][\"role\"] != \"assistant\":\n",
    "    with st.chat_message(\"assistant\"):\n",
    "        with st.spinner(\"Thinking...\"):\n",
    "            response = generate_llama2_response(prompt)\n",
    "            placeholder = st.empty()\n",
    "            full_response = ''\n",
    "            for item in response:\n",
    "                full_response += item\n",
    "                placeholder.markdown(full_response)\n",
    "            placeholder.markdown(full_response)\n",
    "    message = {\"role\": \"assistant\", \"content\": full_response}\n",
    "    st.session_state.messages.append(message)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
