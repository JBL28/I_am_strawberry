import streamlit as st
from st_multimodal_chatinput import multimodal_chatinput
import openai
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from gtts import gTTS
from langchain_openai import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from weather_api.weather import get_weather_forecast
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from weather_api.function_list import functions
from api_keys import OPENAI_API_KEY
# 기존 메시지 리스트
import os
import json
import io
import base64



os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# vector DB path
vector_path = "../index_store2"
embeddings = OpenAIEmbeddings()


location = [st.session_state['sido'],st.session_state['gugun']]
vector_index = Chroma(persist_directory = vector_path,embedding_function = embeddings)

retriever = vector_index.as_retriever(search_type = "similarity",
                                      search_kwargs={ "k": 3 }
                                      )


st.set_page_config(
    page_title="농업용 코파일럿",
    #page_icon="🧊",
    initial_sidebar_state="expanded",
)

client = openai
client.api_key = st.secrets['openai_api_key']


#tts 요청함수
def text_speech(text):
    tts = gTTS(text=text, lang='ko')

    # Save speech to a BytesIO object
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)

    # Convert speech to base64 encoding
    b64 = base64.b64encode(speech_bytes.read()).decode('utf-8')
    md = f"""
            <audio id="audioTag" controls autoplay>
            <source src="data:audio/mp3;base64,{b64}"  type="audio/mpeg" format="audio/mpeg">
            </audio>
            """
    st.markdown(
        md,
        unsafe_allow_html=True,
    )
    
#side bar
sidebar = st.sidebar

sidebar.header("Chatbot")
sidebar.text("copilot")

#st.session_state['api_key'] = True
if not st.secrets['openai_api_key']:
    sidebar.error(":x: API 인증 안됨")
else :
    sidebar.success(":white_check_mark: API 인증 완료")

sidebar.subheader("Models and parameters")

model = sidebar.selectbox(
    label="모델 선택",
    options=["gpt-4-turbo", "gpt-3.5-turbo-1106"]
)
                    

params = sidebar.expander("Parameters")

#temperature
temperature = params.slider(
    label="temperature",
    min_value=0.01,
    max_value=5.00,
    step=0.01
)

#top_p
top_p = params.slider(
    label="top_p",
    min_value=0.01,
    max_value=1.00,
    step=0.01,
    value=0.90
)

#max_length
max_length = params.slider(
    label= "max_length",
    min_value=32,
    max_value=128,
    step = 1,
    value=120
)

# sidebar.button(
#     label= "Clear Chat History"
# )  



# model setting

def retrieve_general_information(query, retriever):
    results = retriever.get_relevant_documents(query)
    return f"Retrieving information for query: {query}, Results: {results}"


llm = ChatOpenAI(temperature=temperature,
                 model_name = "gpt-4-turbo",
                 openai_api_key = st.secrets['openai_api_key']
                 )
def convert_prompt_template(user_input):
    messages = []
    for i in st.session_state['chat']:
        if i.sender == 'user':
            messages.append(HumanMessage(content=i.msg))
        elif i.sender == 'assistant':
            messages.append(AIMessage(content=i.msg))
    return messages

#1. user input 으로 prompt 생성(chat history, query)  user-input->st.session['chat']에서 prompt_template - model_
def get_completion(user_input, location):

    prompt = convert_prompt_template(user_input)
    #chain_input = {'messages': prompt}
    #2. prompt로 llm 통과 -> output을 가지고 model.bind_tools(auto)-> output
    chain = llm.bind_tools(tools=functions, tool_choice="auto") # invoke -> str, or PromptValue, str, or list of BaseMessages.
    output = chain.invoke(prompt) # output.content 

    #3. output.additional_kwargs.get("tool_calls")
    print(output)

    # function call 적용 부분
    if output.additional_kwargs.get("tool_calls"):
        available_functions = {"get_weather_forecast": get_weather_forecast, "retrieval" : retrieve_general_information}
        function_name = output.additional_kwargs["tool_calls"][0]["function"]["name"]
        function_to_call = available_functions[function_name] # 불러야할 function name

        function_args = json.loads(output.additional_kwargs["tool_calls"][0]["function"]["arguments"]) # 불러야할 function 에 필요한 args
        
        # function_response = function_to_call(
        #         location=function_args.get("location"),
        #     )
        # location = ["시도", "군구"]
        if function_name == "get_weather_forecast":
            #location = function_args.get("location", location)
            function_response = function_to_call(location=location)
        elif function_name == "retrieval":
            query = user_input[-1].msg # list obj need to convert str
            function_response = function_to_call(query=query, retriever =retriever)

        #prompt = prompter.get_prompt_for_function(function_response)
        prompt.append(AIMessage(content=function_response))
        final_prompt = ChatPromptTemplate.from_messages(prompt)
        function_chain = final_prompt | llm.with_retry() | StrOutputParser()
        output_with_function = function_chain.invoke({})
        
        # function 적용 후 output
        return output_with_function
    
    else: 
        return output.content # general 한 gpt 사용

#chat
class chat:
    img = None
    msg: str = None
    sender: str = None
    isTTS = None
    def __init__(self, img = None, msg = None, sender = None):
         self.msg = msg
         self.sender = sender
         self.img = img
        

if 'chat' not in st.session_state:
    st.session_state['chat'] = []
    st.session_state['chat'].append(chat(msg = "무엇을 도와드릴까요?", sender='assistant')) ##첫 채팅
        
chatContainer = st.container(height=450)
userInput = multimodal_chatinput()

for i in st.session_state['chat']:
    with chatContainer:
        with st.chat_message(i.sender):
            if i.img:
                st.image(i.img)
            st.write(i.msg)

if "userinput_check" not in st.session_state: #이전에 썼는지 체크
    st.session_state['userinput_check'] = None

if userInput and userInput['text'] != st.session_state['userinput_check']:
    #유저 입력
    chatting = chat()
    if userInput['images']:
        chatting.img = userInput['images']
    chatting.msg = userInput['text']
    chatting.sender = 'user'
    st.session_state['chat'].append(chatting)
    st.session_state['userinput_check'] = userInput['text']
    #메시지 출력
    with chatContainer:
        with st.chat_message('user'):
            if userInput['images']:
                st.image(userInput['images'])
            st.write(userInput['text'])
        # for i in st.session_state['chat']:
        #     with st.chat_message(i.sender):
        #         if i.img:
        #             st.image(i.img)
        #         st.write(i.msg)
    #챗봇

    # generation = get_completion(userInput['text'])
    response_message = get_completion(st.session_state['chat'], location)

    response = chat()

    response.msg = response_message
    response.sender = 'assistant'
    st.session_state['chat'].append(response)
    #메시지 출력
    with chatContainer:
        with st.chat_message('assistant'):
            st.write(response_message)
    # with chatContainer:
    #     for i in st.session_state['chat']:
    #         if i.sender is 'ai':
    #             with st.chat_message(i.sender):
    #                st.write(i.msg)
    userInput = None


# stt 사용
if "tts_check" not in st.session_state: #이전에 썼는지 체크
    st.session_state['tts_check'] = None


stt_button = Button(label="말하기", width=100, button_type="success")
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))


with sidebar:
    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=40,
        debounce_time=0,)
        

if result :
    if "GET_TEXT" in result and result.get("GET_TEXT") != st.session_state['tts_check']:
        speech = chat()
        #if result.get("GET_TEXT") != st.session_state['chat'][-1].msg:
        speech.msg = result.get("GET_TEXT")
        speech.sender = 'user'
        st.session_state['chat'].append(speech)
        #유저 메시지 출력
        with chatContainer:
            with st.chat_message('user'):
                st.write(result.get("GET_TEXT"))
        st.session_state['tts_check'] = result.get("GET_TEXT")

        #챗봇
        generation = get_completion(result.get("GET_TEXT"))

<<<<<<< HEAD
        response_message = generation
=======
        response_message = generation#['generation_result']
>>>>>>> 6de238ec2e7422e6fceea88efe05593154a18cfd

        response = chat()
        response.msg = response_message
        response.sender = 'assistant'
        response.isTTS = True
        st.session_state['chat'].append(response)
        
        #챗봇 메시지 출력
        with chatContainer:
            with st.chat_message('assistant'):
                st.write(response_message)
                text_speech(response_message)
        