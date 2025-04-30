from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import RetrievalQA
from financial_statement_retriever import retriever
from langchain.tools import tool
def create_my_agent_with_vector(llm, tools):
    """
    Tạo agent có hỗ trợ tool-calling và truy vấn vector database.

    Args:
        llm: Một instance của LLM.
        tools: Danh sách tools đã định nghĩa.
        retriever: Một retriever (VD: từ FAISS, Chroma, v.v.)

    Returns:
        Agent đã sẵn sàng để dùng với AgentExecutor.
    """

    # Tạo QA chain từ retriever
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
       
    # Đóng gói thành tool
    @tool
    def truy_van_bao_cao_tai_chinh(query: str) -> str:
       """Trả lời câu hỏi tài chính dựa trên cơ sở dữ liệu báo cáo tài chính embedding."""
       return qa_chain.run(query)

    # Thêm tool vào danh sách
    tools.append(truy_van_bao_cao_tai_chinh)

    # Prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Bạn là một trợ lý tài chính thông minh. Nếu câu hỏi liên quan đến tài chính, hãy ưu tiên trả lời chi tiết, chuyên sâu bằng cách gọi tool nếu cần , nếu người dùng hỏi về báo cáo tài chính của công ty hãy dùng công cụ 'truy_van_bao_cao_tai_chinh' để trả lời dựa trên dữ liệu embedding . Nếu không liên quan, hãy trả lời trung lập và chính xác."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Tạo agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    return agent

