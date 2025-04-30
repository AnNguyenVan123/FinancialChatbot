from langchain.tools import BaseTool
from typing import Type, Any
from pydantic import BaseModel, PrivateAttr
from langchain.chains.retrieval_qa.base import RetrievalQA


class FinancialQueryInput(BaseModel):
    query: str

class TruyVanBaoCaoTaiChinh(BaseTool):
    name: str = "truy_van_bao_cao_tai_chinh"
    description: str = (
        "Truy vấn báo cáo tài chính từ cơ sở dữ liệu embedding. "
        "Nhận đầu vào là một câu hỏi tài chính, trả về câu trả lời dựa trên vector DB."
    )
    args_schema: Type[BaseModel] = FinancialQueryInput

    # Private attributes (not part of Pydantic's validation)
    _qa_chain: RetrievalQA = PrivateAttr()
    _memory: dict = PrivateAttr()

    def __init__(self, qa_chain: RetrievalQA, memory: dict, **kwargs: Any):
        super().__init__(**kwargs)
        self._qa_chain = qa_chain
        self._memory = memory

    def _run(self, query: str) -> str:
        try:
            chat_history = self._memory.get("chat_history", [])
            result = self._qa_chain.invoke({"input": query, "chat_history": chat_history})
            return result["answer"]
        except Exception as e:
            return f"Không tìm thấy thông tin: {str(e)}"
