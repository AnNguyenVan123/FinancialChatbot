import json
import re
from typing import Dict
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate

def extract_user_facts(llm, user_input: str) -> Dict:
    from langchain_core.prompts import PromptTemplate
    import json

    prompt = PromptTemplate.from_template("""
    Trích xuất các thông tin quan trọng dưới dạng JSON. 
    Chỉ trả về một object JSON duy nhất, không thêm bất kỳ văn bản nào khác.
    
    Ví dụ: {{ "name": "An", "balance": 15000000, "interest": "VHM báo cáo tài chính" }}
    
    Câu: {user_input}
    """)

    response = (prompt | llm).invoke({"user_input": user_input})

    content = response.content if isinstance(response, BaseMessage) else str(response)
    print("Raw response:", content)

    # Xử lý nghiêm ngặt JSON
    try:
        first_brace = content.find('{')
        last_brace = content.rfind('}') + 1
        json_part = content[first_brace:last_brace]
        data = json.loads(json_part)
    except Exception as e:
        print("Lỗi parse JSON:", e)
        data = {}

    return data


