import json
import re
from typing import Dict
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate

def extract_user_facts(llm, user_input: str) -> Dict:
    """
    Use LLM to extract key-value information from user's question.
    """
    extraction_prompt = PromptTemplate.from_template("""
    Trích xuất các thông tin liên quan từ câu sau đây. Chỉ đưa ra các cặp khóa–giá trị có ý nghĩa.
    Trả về kết quả ở dạng JSON không cần chú thích chỉ cần trả lời đúng dạng. 
    Ví dụ: {{ "name": "An", "balance": 15000000, "interest": "VHM báo cáo tài chính" }}
    Câu người dùng: {user_input}
    """)

    chain = extraction_prompt | llm
    response = chain.invoke({"user_input": user_input})

    # Safely get string content
    raw_output = response.content if isinstance(response, BaseMessage) else str(response)
    print("Raw response:", raw_output)

    # Extract JSON object using regex
    match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
    if match:
        try:
            extracted = json.loads(match.group(0))
            
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
          
    else:
        print("No valid JSON object found in response.")
        extracted = {}

    return extracted

