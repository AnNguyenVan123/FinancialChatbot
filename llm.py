from langchain_google_genai import ChatGoogleGenerativeAI
import os
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_output_tokens=2048,
    google_api_key=GOOGLE_API_KEY,
    timeout=30  # Thêm timeout tránh kẹt
)