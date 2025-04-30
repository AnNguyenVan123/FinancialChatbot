import os
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from tools import tools
from llm import llm
from agent_create import create_my_agent_with_vector

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Create agent and executor
agent = create_my_agent_with_vector(llm=llm, tools=tools)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Initialize chat history
chat_history = []

# Define Gradio chatbot function
def chat(user_input, history):
    try:
        # Execute your logic
        response = executor.invoke({
            "input": user_input,
            "chat_history": chat_history,
        })
        
        # Extract bot's response
        bot_reply = response["output"]
       

        # Update history in Gradio's format: [(user_message, bot_response), ...]
        # history.append({"role": "user", "content": user_input})
        
    
        # Return history as is (Gradio expects it to be a list of tuples)
        return {"role": "assistant", "content": bot_reply}
    
    except Exception as e:
        # Return error in case of failure, ensuring Gradio's format
        if history is None:
            history = []
        history.append((user_input, f"❌ Error: {str(e)}"))
        return history

# Gradio UI
chatbot = gr.ChatInterface(fn=chat,
                           type="messages",
                           chatbot=gr.Chatbot(),
                           additional_inputs=[]
                    )

if __name__ == "__main__":
    chatbot.launch()


