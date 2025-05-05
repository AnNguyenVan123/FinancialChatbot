from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import MessagesPlaceholder
from knowledge_base import knowledge_base
from langchain_core.prompts import PromptTemplate
def create_my_agent_with_vector(llm, tools) :
    """
    Create a financial assistant agent with tool-calling capability and conversational memory,
    returning a RunnableSequence.

    Args:
        llm: Language model for processing queries and summarization.
        tools: List of tools the agent will use.

    Returns:
        RunnableSequence representing the complete agent pipeline.
    """
    
    # Define prompt for agent
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import PromptTemplate
from knowledge_base import knowledge_base  # Assuming it's a string or a formatted summary

def create_my_agent_with_vector(llm, tools):
    """
    Create a financial assistant agent with tool-calling capability and conversational memory,
    returning a Runnable agent.
    
    Args:
        llm: Language model for processing queries and summarization.
        tools: List of tools the agent will use.

    Returns:
        Runnable representing the complete agent pipeline.
    """
    # Create prompt string manually
    template_str = (
    "Bạn là một trợ lý tài chính.\n"
    "Dữ liệu lịch sử:\n{knowledge_base}\n\n"
    "Lịch sử cuộc trò chuyện:\n{chat_history}\n\n"
    "Các bước suy luận trước đó:\n{agent_scratchpad}\n\n"
    "Người dùng nhập:\n{input}"
)
  
    prompt = PromptTemplate(
        input_variables=[ "chat_history", "agent_scratchpad", "input"],
        template=template_str
    ).partial(knowledge_base=knowledge_base)
    # Create the agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    return agent


   