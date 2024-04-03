import os
import streamlit as st
import json
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI, OpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from typing import List, Any

if "OPENAI_KEY_FILE" in os.environ:
    with open(os.environ["OPENAI_KEY_FILE"], "r") as file:
        key_content = file.read()
    os.environ["OPENAI_API_KEY"] = key_content

configFile = open(os.path.join(os.path.dirname(__file__), "config.json"))
config = json.load(configFile)
configFile.close()

llm = ChatOpenAI(temperature=0, model_name="gpt-4", streaming=True)

characterPromptTemplate = """
You are a character generator that likes to generate characters that like to give advice and answer questions.
Your character must align with the following characteristics:

Quick description: {adjective} {noun}
Favorite activity: {verb} {adverb}
Best friend's name: {name}

Create a short description about this character in 2-3 sentences.
"""

characterPrompt = PromptTemplate.from_template(characterPromptTemplate)

blocking_llm = ChatOpenAI(temperature=0, model_name="gpt-4", streaming=False)
llmchain_chat = LLMChain(llm=blocking_llm, prompt=characterPrompt)
character = llmchain_chat.run({ 
    "adjective": config["metadata"]["adjective"], 
    "noun": config["metadata"]["noun"], 
    "verb": config["metadata"]["verb"], 
    "adverb": config["metadata"]["adverb"],
    "name": config["metadata"]["name"]
})

print (character)

template = """
You are a chatbot that has the likeness of the following character:

{character}

You must also somehow reference your favorite color, which is {color}. Although that's a hex code value,
feel free to turn it into a human understandable color.

You must answer the questions as this character, giving advice and answering questions as this character would.
If you do not know the answer, you are welcome to make up an answer that aligns with the character.
But, you must make it clear that you are making up the answer.
""".format(character=character, color=config["metadata"]["color"])

system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "{question}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def generate_llm_output(
    user_input: str, callbacks: List[Any], prompt=chat_prompt
) -> str:
    chain = prompt | llm
    answer = chain.invoke(
        {"question": user_input}, config={"callbacks": callbacks}
    ).content
    return {"answer": answer}

def chat_input():
    user_input = st.chat_input("How can I help you today?")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            stream_handler = StreamHandler(st.empty())
            result = generate_llm_output(
                {"question": user_input, "chat_history": []}, callbacks=[stream_handler]
            )["answer"]
            output = result
            st.session_state[f"user_input"].append(user_input)
            st.session_state[f"generated"].append(output)

def display_chat():
    # Session state
    if "generated" not in st.session_state:
        st.session_state[f"generated"] = []

    if "user_input" not in st.session_state:
        st.session_state[f"user_input"] = []

    if st.session_state[f"generated"]:
        size = len(st.session_state[f"generated"])
        # Display only the last three exchanges
        for i in range(max(size - 3, 0), size):
            with st.chat_message("user"):
                st.write(st.session_state[f"user_input"][i])

            with st.chat_message("assistant"):
                # st.caption(f"RAG: {st.session_state[f'rag_mode'][i]}")
                st.write(st.session_state[f"generated"][i])

        with st.container():
            st.write("&nbsp;")

st.write("Character storyline: {prompt}".format(prompt=character))
display_chat()
chat_input()