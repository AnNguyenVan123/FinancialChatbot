import os
import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
import base64
from tool_list import tools
from typing import Dict
from extractor.extract_user_input import extract_user_facts
from knowledge_base import knowledge_base
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Initialize memory and chat model
memory = MemorySaver()
model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")

# Create agent executor
agent_executor = create_react_agent(model, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

# Optional: update knowledge base
def update_knowledge_base(facts: Dict) -> None:
    knowledge_base.update(facts)

# Define function to handle user input
def chat_fn(message, history):
    messages = [HumanMessage(content=message)]
    bot_response = ""
    
    for step in agent_executor.stream(
        {"messages": messages},
        config,
        stream_mode="values",
    ):  
        
   
        bot_message = step["messages"][-1]
        bot_response = bot_message.content

    # Kiểm tra xem có cần gửi kèm ảnh không
    image_path = './charts/chart.png'
    
    if  os.path.exists(image_path):
        # Đọc ảnh và encode base64
        with open(image_path, 'rb') as f:
            img_data = f.read()
        base64_img = base64.b64encode(img_data).decode("utf-8")
        markdown_img = f"![biểu đồ](data:image/png;base64,{base64_img})"

        os.remove(image_path)  # dọn dẹp file tạm

        # Trả cả văn bản và ảnh
        return markdown_img +  "\n\n" + bot_response 

    return bot_response
# Create Gradio interface
chat_interface = gr.ChatInterface(
    fn=chat_fn,
    title="Trợ lý AI của bạn",
    description="Hỏi bất kỳ điều gì như thời tiết, giá cổ phiếu, v.v.",
    
)

# Launch app
if __name__ == "__main__":
    chat_interface.launch(share=True)
