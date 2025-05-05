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

# Set Matplotlib backend to Agg (non-interactive) at the start
matplotlib.use('Agg')

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]


def update_knowledge_base(facts: Dict) -> None:
    """Update knowledge base with new information."""
    knowledge_base.update(facts)

# Create agent and executor
agent = create_my_agent_with_vector(llm, tools)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
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

        # Extract user facts
        user_facts = extract_user_facts(llm, user_input)
        if user_facts:
            update_knowledge_base(user_facts)

        # Execute agent
        response = executor.invoke({"input": user_input, "chat_history": chat_history})
        
        # Extract bot's response
        bot_reply = response["output"]
        print(bot_reply)
        # Check if response is a PIL Image
        if isinstance(bot_reply, str) and 'biểu đồ' in bot_reply :  
              image_path = './charts/chart.png'
              if(os.path.exists(image_path) is False):
                  return  {"role": "assistant", "content": bot_reply}
              with open(image_path, 'rb') as f:
                 img_data = f.read()
              base64_img = base64.b64encode(img_data).decode("utf-8")
              markdown_img = f"![chart](data:image/png;base64,{base64_img})"
              os.remove(image_path)
              return  [
        {"role": "assistant", "content": bot_reply},
        {"role": "assistant", "content": markdown_img}  # đường dẫn file ảnh
    ]
        else:
            # Handle text responses or unexpected output
            # print(f"Knowledge base: {knowledge_base}")
            if not bot_reply:
                bot_reply = "No response generated. Please try again."
            return [{"role": "assistant", "content": str(bot_reply)}]

    except Exception as e:
        error_message = f"Error occurred: {str(e)}. Please try again."
        print(f"Exception: {e}")
        return {"role": "assistant", "content": error_message}

# Gradio UI with Grok-inspired design
with gr.Blocks(
    theme=gr.themes.Base(),
) as chatbot:
    gr.Markdown(
        """
        <h1>Smart Financial Assistant</h1>
        <p>Ask about financial data, reports, or plot stock charts (e.g., "Plot VNM candlestick chart, 30 days, up to 2025-05-01, 1D").</p>
        """,
        elem_classes=["header"]
    )

    # Chatbot display
    chat_interface = gr.Chatbot(
        type="messages",
        elem_classes=["chatbot"],
        show_label=False,
        height=600,
        bubble_full_width=False
    )

    # Input and submit button
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

    # Loading spinner
    loading = gr.HTML("<div class='loading-spinner'>Processing...</div>")

    # Handle message submission
    def handle_submit(user_input, history):
            if not history:
               history = []

            history.append({"role": "user", "content": user_input})
            responses = chat(user_input, history)

            for r in responses:
                history.append(r)

            return history, "", gr.update(visible=False)
        
       

    # Show loading spinner
    def show_spinner():
        return gr.update(visible=True)

    # Event bindings
    submit_button.click(
        fn=show_spinner,
        outputs=[loading],
        queue=True
    ).then(
        fn=handle_submit,
        inputs=[user_input, chat_interface],
        outputs=[chat_interface, user_input, loading],
        queue=True
    )

    # Auto-scroll to bottom after new messages
    chat_interface.change(
        fn=lambda x: x,
        inputs=[chat_interface],
        outputs=[chat_interface],
    )

if __name__ == "__main__":
    chatbot.launch()