import os
from api_keys import (OPENAI_API_KEY,
                      LANGSMITH_API_KEY
)
import argparse

from langchain_core.output_parsers import StrOutputParser
from models import get_api_model # model config에서 모델에 하이퍼 파라미터를 적용해서 모델을 불러옴
from prompts.prompter import Prompter # Prompter: 모델에 넣을 프롬프트를 리턴 {"system", self.system_message}, {human, self.human_message}
from utils import (load_yaml,
                   setting_for_langsmith,
)

from langsmith import traceable
from functions import functions
from weather import (get_weather_forecast,
)
import json

@traceable
def run(args):
    config = load_yaml(args.config_filepath) # load config yaml 
    """
    yaml coonfig
        model:
            name: gpt-3.5-turbo-0125
            temperature:0.3
            top_p: 0.9
            max_tokens: 512

        dataset:
            name: null

        prompt:
            template_path: ./prompts/generation_template.yaml
            template: naive
        
        cache_dir: ./cache_dir
        output_dir: ./outputs

        project_name: curr_weather_test
    """
    
    setting_for_langsmith(OPENAI_API_KEY, LANGSMITH_API_KEY, config) # api 키 입력하고 나서
    model = get_api_model(config) # load model 모델설정 불러와서

    prompt_templates = load_yaml(config['prompt']['template_path']) # load prompt template 템플릿 형식도 불러와서
    prompt_template = prompt_templates[config['prompt']['template']]
    prompter = Prompter(config, prompt_template)

    # Load dataset and prompter
    prompt = prompter.get_prompt()

    # Construct a chain
    # LLM 판단 하에 function 적용
    # chain = prompt | model.bind_tools(tools=functions, tool_choice="auto")
    
    # 항상 function 적용
    chain = prompt | model.bind_tools(tools=functions, tool_choice={"type": "function", "function": {"name": "get_weather_forecast"}})
    
    # Invoke a generation
    output = chain.invoke({}) 
    
    # function 적용 전 output
    print(output)
    
    # function call 적용 부분
    if output.additional_kwargs.get("tool_calls"): # llm 이 판단하기에 tool의 필요성이 있는가?
        
        available_functions = {"get_weather_forecast": get_weather_forecast} #value로 LLM 에 함수를 전달

        function_name = output.additional_kwargs["tool_calls"][0]["function"]["name"] # 
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(output.additional_kwargs["tool_calls"][0]["function"]["arguments"])

        function_response = fuction_to_call( # response 에서는 function의 결과값 날씨 결과값
                location=function_args.get("location"), # output 에 담겨있는 prompt 에서 추출한 내용이 담겨져 있다
            ) # functions 에 저장되어 있는 arguments 이름
        
        prompt = prompter.get_prompt_for_function(function_response)
        
        function_chain = prompt | model.with_retry() | StrOutputParser()
        output_with_function = function_chain.invoke({})
        
        # function 적용 후 output
        print(output_with_function)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_filepath", default=None, type=str, help="config filepath")
    args = parser.parse_args()

    run(args)