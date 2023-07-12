import inspect
import json

import gradio as gr
import requests
from langchain import SQLDatabase, SQLDatabaseChain, OpenAI
import os
import socket
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage

os.environ["OPENAI_API_KEY"] = "sk-"
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


def get_function_parameter_names(function):
    if function is not None and inspect.isfunction(function):
        parameter_names = inspect.signature(function).parameters.keys()
        return list(parameter_names)
    else:
        return None


def ScrapSteelStorage(keyWorks):
    localIP = socket.gethostbyname(socket.gethostname())  # 这个得到本地ip
    str = 'keyWorks=' + keyWorks
    url = 'http://192.168.20.105:8081/ScrapSteelStorage?' + str
    print(url)
    response = requests.get(url)
    return response.text


# 获取函数的参数
first_response = ""
second_response = ""
returned_value = ""
function_name = ""
ai_history = []


def get_Aanswer(func, query):
    question = """
    问题：{query}

    以下内容是注意事项，请严格遵守。
    请采用new Date()函数获取当前时间，时间格式为:'YYYY-MM-DD'，对于时间的处理，一定要遵循以上规则。

    对于数据库字段有如下规则：
    低价值：low_value_per，检验批号：check_number，车牌号：license_plate，
    判定地点：judge_location，判定结果：is_change_judgment。
    如果遇到字段相关的问题，请转换成中文解释。

    """

    parameter_names = get_function_parameter_names(func)
    print(parameter_names)

    question = question.replace("{query}", query)
    first_response = llm.predict_messages([
        HumanMessage(content=question)
    ], functions=function_descriptions)
    print(first_response)
    ai_history.append(first_response.additional_kwargs)

    try:
        function_name = first_response.additional_kwargs["function_call"]["name"]
        arguments = json.loads(first_response.additional_kwargs["function_call"]["arguments"])

        the_function = globals().get(function_name)
        parameter_names = get_function_parameter_names(the_function)
        parameter_values = []
        for parameter_name in parameter_names:
            parameter_values.append(arguments[parameter_name])

        returned_value = the_function(*parameter_values)
        print("===========================returned_value===========================")
        print(returned_value)
        print("====================================================================")
        second_response = llm.predict_messages(
            [
                HumanMessage(content=question),
                AIMessage(content=str(ai_history)),
                ChatMessage(
                    role='function',
                    additional_kwargs={'name': function_name},
                    content=returned_value
                )
            ],
            functions=function_descriptions
        )
        print("===========================second_response===========================")
        print(second_response)
        print("====================================================================")
        ai_history.append(second_response.additional_kwargs)
        if second_response == "":
            second_response = "暂时没有找到，请重新提问！"
        return second_response
    except Exception as e:
        return "暂时没有找到，请重新提问！"


query = ""

with gr.Blocks() as demo:
    with gr.Tab("数据库查询"):
        chatbot = gr.Chatbot(elem_id="chat-box",
                             show_label=False).style(height=700)
        msg = gr.Textbox(placeholder="请输入问题，按回车确认！")


        def respond(message, chat_history):
            db = SQLDatabase.from_uri(f"mysql+pymysql://root:123456@192.168.20.105/test")
            prompt = """
                          根据提问到数据库查询数据，一定按实际情况叙述，不要篡改结果，只能用中文回答。如果找不到相关信息，返回"暂未找到"
                      """
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0613")
            db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
            db_answer = db_chain.run(message)

            # toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0,prompt=prompt))
            # agent_executor = create_sql_agent(
            #     llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
            #     toolkit=toolkit,
            #     verbose=True,
            #     agent_type=AgentType.OPENAI_FUNCTIONS
            # )
            # db_answer = agent_executor.run(message)
            chat_history.append((message, db_answer))
            return "", chat_history


        msg.submit(respond, [msg, chatbot], [msg, chatbot])

    with gr.Tab("API查询"):
        chatbot = gr.Chatbot(elem_id="chat-box",
                             show_label=False).style(height=700)
        msg = gr.Textbox(placeholder="请输入问题，按回车确认！")


        def respond(message, chat_history):
            answer = get_Aanswer(ScrapSteelStorage, message)
            chat_history.append((message, answer.content))
            return "", chat_history


        msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name='127.0.0.1',
                server_port=7866,
                show_api=False,
                share=False,
                inbrowser=False)
