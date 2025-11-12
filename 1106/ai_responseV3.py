from openai import OpenAI
from dotenv import load_dotenv
import os
import json
# 🔄 기존 작성된 함수 사용
from ai_responseV2 import get_current_date_tz, get_current_time_tz
load_dotenv()
client=OpenAI() 

# 🔄 주요 함수 이름 변경
def get_ai_response_tools(question, functions=None):
   response = get_first_response_tools(question=question)
   fn_name = getattr(response.choices[0].message.function_call, "name", None)
   if fn_name:
    # 함수 호출 : get_current_time_tz ,get_current_date_tz 는 인자가 필요합니다.
    # funcion_call.arguments 문자열을 dict 로 변환
    tz = json.loads(response.choices[0].message.function_call.arguments)
    func_response =  globals()[fn_name](**tz)  
    followup_response=get_followup_response_tools(fn_name,func_response)
    return followup_response.choices[0].message.content
   else:
    return response.choices[0].message.content

def get_followup_response_tools(fn_name, func_response):
    followup_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant.using locale language."},
            {"role": "user", "content": f'{fn_name} 함수를 실행한 결과 {func_response} 이용하여 최종 응답을 만들어줘.'}
        ],
        tools=tools
    )
    return followup_response

def get_first_response_tools(question):
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "system", "content": "You are a helpful assistant.using locale language."},
      {"role": "user", "content": question}
    ],
    tools=tools,
  )
  return response

# tools 
tools = [
    {
        "name": "get_current_time_tz",
        "description": "현재 시간 출력 HH:MM:SS format",
        # 함수의 인자를 정의
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Time zone in 'Area/Location' format, e.g., 'Asia/Seoul', 'America/New_York'. Default is 'Asia/Seoul'."
                }
            },
            "required": ['timezone']
        }
    },
    { 
        "name": "get_current_date_tz",
        "description": "현재 날짜 출력 YYYY 년 MM 월 DD 일 format",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Time zone in 'Area/Location' format, e.g., 'Asia/Seoul', 'America/New_York'. Default is 'Asia/Seoul'."
                }
            },
            "required": ['timezone']
        }
    }
]