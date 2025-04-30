import os
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from tool_list import tools
from llm import llm
from agent_create import create_my_agent_with_vector

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Create agent and executor
agent, memory = create_my_agent_with_vector(llm, tools)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

# Define Gradio chatbot function
def chat(user_input, history):
    try:
        # Convert Gradio history to LangChain format
        chat_history = []
        for msg in history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))

        # Execute agent
        response = executor.invoke({
            "input": user_input,
            "chat_history": chat_history,
        })

        # Extract bot's response
        bot_reply = response["output"]


        # Return response in Gradio format
        return {"role": "assistant", "content": bot_reply}

    except Exception as e:
        error_message = f"Đã xảy ra lỗi: {str(e)}. Vui lòng thử lại."
        print(e)
        return {"role": "assistant", "content": error_message}

# Gradio UI
chatbot = gr.ChatInterface(
    fn=chat,
    type="messages",
    chatbot=gr.Chatbot(),
    additional_inputs=[],
    title="Trợ lý Tài chính Thông minh",
    description="Hỏi về thông tin tài chính, báo cáo tài chính, hoặc bất kỳ chủ đề nào khác!"
)

if __name__ == "__main__":
    chatbot.launch()
