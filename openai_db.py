import gradio as gr
import random
import time
from langchain import SQLDatabase, SQLDatabaseChain, OpenAI
import os

os.environ["OPENAI_API_KEY"] = "sk-"

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(elem_id="chat-box",
                         show_label=False).style(height=750)
    msg = gr.Textbox(placeholder="请输入问题，按回车确认！")


    def respond(message, chat_history):
        db = SQLDatabase.from_uri(f"mysql+pymysql://root:123456@192.168.20.105/scrap_grading")
        llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo")
        db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
        db_answer = db_chain.run(message)
        chat_history.append((message, db_answer))
        return "", chat_history


    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    demo.launch(server_name='0.0.0.0',
                server_port=7866,
                show_api=False,
                share=False,
                inbrowser=False)
