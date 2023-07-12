from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage
from langchain.tools import format_tool_to_openai_function
import os
import inspect
import requests
import socket
import json
import datetime

os.environ['OPENAI_API_KEY'] = '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'
model = 'gpt-3.5-turbo-0613'
llm = ChatOpenAI(model=model)
function_descriptions = [
    {
        "name": "ScrapSteelStorage",
        "description": "关于废钢入库的信息在此",
        "parameters": {
            "type": "object",
            "properties": {
                "keyWorks": {
                    "type": "string",
                    "description": "这是关键字",
                }
            },
            "required": [],
        },
    }
]
query = "2023年7月3日一共有几车废钢入库？请列出车牌号和对应的判定地点。"
question = """
问题：{query}

以下内容是注意事项，请严格遵守。
请采用new Date()函数获取当前时间，时间格式为:'YYYY-MM-DD'，对于时间的处理，一定要遵循以上规则。

对于数据库字段有如下规则：
低价值：low_value_per，检验批号：check_number，车牌号：license_plate，
判定地点：judge_location，判定结果：is_change_judgment。
如果遇到字段相关的问题，请转换成中文解释。

"""

def get_function_parameter_names(function):
  if function is not None and inspect.isfunction(function):
      parameter_names = inspect.signature(function).parameters.keys()
      return list(parameter_names)
  else:
      return None



def ScrapSteelStorage(keyWorks):
    localIP = socket.gethostbyname(socket.gethostname())  # 这个得到本地ip
    str = 'keyWorks='+keyWorks
    url = 'http://'+localIP+':8081/ScrapSteelStorage?' + str
    response = requests.get(url)
    return response.text

# 获取函数的参数
parameter_names = get_function_parameter_names(ScrapSteelStorage)
print(parameter_names)

question = question.replace("{query}", query)

first_response = llm.predict_messages([HumanMessage(content=question)], functions=function_descriptions)
print(first_response)


function_name = first_response.additional_kwargs["function_call"]["name"]
arguments = json.loads(first_response.additional_kwargs["function_call"]["arguments"])

# Locate the function and make the call
the_function = globals().get(function_name)
parameter_names = get_function_parameter_names(the_function)
parameter_values = []
for parameter_name in parameter_names:
    parameter_values.append(arguments[parameter_name])

returned_value = the_function(*parameter_values)
print(returned_value)

second_response = llm.predict_messages(
    [
        HumanMessage(content=question),
        AIMessage(content=str(first_response.additional_kwargs)),
        ChatMessage(
            role='function',
            additional_kwargs = {'name': function_name},
            content = returned_value
        )
    ],
    functions=function_descriptions
)
print("second_response")
print(second_response)
print("===============================")
third_response = llm.predict_messages(
    [
        HumanMessage(content=question),
        AIMessage(content=str(first_response.additional_kwargs)),
        AIMessage(content=str(second_response.additional_kwargs)),
        ChatMessage(
            role='function',
            additional_kwargs = {'name': function_name},
            content = returned_value
        )
    ], functions=function_descriptions
)

print(third_response)