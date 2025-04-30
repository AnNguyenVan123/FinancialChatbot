from langchain.chains import RetrievalQA
from financial_statement_retriever import retriever
from llm import llm
from langchain.tools import Tool

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

def truy_van_bao_cao_tai_chinh(query: str) -> str:
       """Trả lời câu hỏi tài chính dựa trên cơ sở dữ liệu báo cáo tài chính embedding."""
       return qa_chain.run(query)
   
query_VN_financial_statement_tool = Tool (
    name="query_VN_financial_statement",
    description="Truy vấn báo cáo tài chính của công ty Việt Nam . Input : Truy vấn của người dùng",
    func= truy_van_bao_cao_tai_chinh
)