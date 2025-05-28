import os
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from tool_list import tools
from llm import llm
import base64
from typing import Dict

from agent_create import create_my_agent_with_vector
from extractor.extract_user_input import extract_user_facts
from knowledge_base import knowledge_base
import matplotlib

# Set Matplotlib backend to Agg (non-interactive)
matplotlib.use('Agg')

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

def update_knowledge_base(facts: Dict) -> None:
    knowledge_base.update(facts)

# Create agent and executor
agent = create_my_agent_with_vector(llm, tools)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

def chat(user_input, history):
    try:
        chat_history = []
        for msg in history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))

        user_facts = extract_user_facts(llm, user_input)
        if user_facts:
            update_knowledge_base(user_facts)

        response = executor.invoke({"input": user_input, "chat_history": chat_history})
        bot_reply = response.get("output", "")
        print(bot_reply)

        image_path = './charts/chart.png'
        if isinstance(bot_reply, str) and 'biểu đồ' in bot_reply:
            if not os.path.exists(image_path):
                print("Chart image not found at", image_path)
                return {"role": "assistant", "content": bot_reply}
            with open(image_path, 'rb') as f:
                img_data = f.read()
            base64_img = base64.b64encode(img_data).decode("utf-8")
            markdown_img = f"![chart](data:image/png;base64,{base64_img})"
            os.remove(image_path)
            return [
                {"role": "assistant", "content": bot_reply},
                {"role": "assistant", "content": markdown_img}
            ]
        else:
            if not bot_reply:
                bot_reply = "No response generated. Please try again."
            return [{"role": "assistant", "content": str(bot_reply)}]

    except Exception as e:
        error_message = f"Error occurred: {str(e)}. Please try again."
        print(f"Exception: {e}")
        return {"role": "assistant", "content": error_message}

with gr.Blocks(
    theme=gr.themes.Base(),
    css="""
    .chatbot-container {
        height: 90vh;
        display: flex;
        flex-direction: column;
    }
    .chatbox {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    .input-row {
        display: flex;
        margin-top: 10px;
    }
    .input-box textarea {
        border-radius: 8px;
        font-size: 1rem;
        padding: 0.75rem;
        width: 100%;
        border: 1px solid #ccc;
    }
    .submit-btn {
        margin-left: 10px;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        background-color: #10a37f;
        color: white;
        font-weight: bold;
        border: none;
    }
    .loading-spinner {
        color: #888;
        font-style: italic;
        margin-top: 10px;
    }
    .message.user {
        text-align: right;
        background-color: #000000;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 5px;
        display: inline-block;
        max-width: 80%;
    }
    .message.assistant {
        text-align: left;
        background-color: #F1F0F0;
        padding: 0.75rem;
        border-radius: 10px;
        margin: 5px;
        display: inline-block;
        max-width: 80%;
    }
    """
) as chatbot:
    gr.Markdown(
        """
        <h1 style='text-align: center;'>💬 Smart Financial Assistant</h1>
        <p style='text-align: center;'>Ask about financial data, reports, or plot stock charts (e.g., "Plot VNM candlestick chart, 30 days, up to 2025-05-01, 1D").</p>
        """,
        elem_classes=["header"]
    )

    chat_interface = gr.Chatbot(
        type="messages",
        elem_classes=["chatbot"],
        show_label=False,
        height=600,
        bubble_full_width=False
    )

    with gr.Row(elem_classes=["input-container"]):
        user_input = gr.Textbox(
            placeholder="Type your question or request...",
            label="",
            elem_classes=["input-box"],
            scale=4,
            show_label=False
        )
        submit_button = gr.Button(
            "Send",
            elem_classes=["submit-btn"],
            scale=1
        )

    loading = gr.HTML("<div class='loading-spinner'>Processing...</div>", visible=False)

    def add_user_message(user_input, history):
        if not history:
            history = []
        history.append({"role": "user", "content": user_input})
        return history, "", gr.update(visible=True)

    def generate_bot_reply(history):
        user_input = history[-1]["content"]
        responses = chat(user_input, history[:-1])
        if isinstance(responses, dict):
            responses = [responses]
        for r in responses:
            history.append(r)
        return history, gr.update(visible=False)

    submit_button.click(
        fn=add_user_message,
        inputs=[user_input, chat_interface],
        outputs=[chat_interface, user_input, loading],
        queue=False
    ).then(
        fn=generate_bot_reply,
        inputs=[chat_interface],
        outputs=[chat_interface, loading],
        queue=True
    )

    chat_interface.change(
        fn=lambda x: x,
        inputs=[chat_interface],
        outputs=[chat_interface],
    )

if __name__ == "__main__":
    chatbot.launch(share=True)