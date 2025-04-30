from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory

def create_my_agent_with_vector(llm, tools):
    """
    Tạo agent có hỗ trợ tool-calling và truy vấn vector database.

    Args:
        llm: Một instance của LLM.
        tools: Danh sách tools đã định nghĩa.

    Returns:
        Agent đã sẵn sàng để dùng với AgentExecutor và memory instance.
    """
    # Define the summary prompt with correct input variables
    summary_prompt = PromptTemplate(
        input_variables=["summary", "new_lines"],
        template="""
        Dựa trên tóm tắt hội thoại hiện tại và các dòng hội thoại mới, hãy tạo một tóm tắt ngắn gọn, tập trung vào:
        - Công ty được nhắc đến (nếu có, ví dụ: VHM).
        - Loại thông tin người dùng hỏi (ví dụ: thông tin chung, báo cáo tài chính).
        - Ngữ cảnh chính của hội thoại.

        Tóm tắt hiện tại:
        {summary}

        Các dòng hội thoại mới:
        {new_lines}

        Tóm tắt mới:
        """
    )

    # Initialize ConversationSummaryMemory with the corrected prompt
    memory = ConversationSummaryMemory(
        llm=llm,
        memory_key="chat_history",
        prompt=summary_prompt,
        return_messages=True
    )

    # Prompt template for the agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Bạn là một trợ lý tài chính thông minh. Nếu câu hỏi liên quan đến tài chính, hãy ưu tiên trả lời chi tiết, chuyên sâu bằng cách gọi tool nếu cần. Nếu người dùng hỏi về báo cáo tài chính của công ty, hãy dùng công cụ 'truy_van_bao_cao_tai_chinh' để trả lời dựa trên dữ liệu embedding. Nếu không liên quan, hãy trả lời trung lập và chính xác."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    return agent, memory