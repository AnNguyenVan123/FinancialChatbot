from functions import get_company_info ,get_stock_price, draw_stock_chart, get_financial_statement, explain_financial_term, compare_stocks ,suggest_investment_ideas ,summarize_financial_news,chatbot_general_response
#from functions import get_stock_price
from langchain.tools import Tool
import os
from dotenv import load_dotenv
from tools.get_VN_financial_statement_tool import query_VN_financial_statement_tool
from tools.get_VN_stock_metadata_tool import stock_metadata_tool
from tools.get_VN_stock_price_tool import VN_stock_price_tool
from tools.draw_VN_stock_chart import draw_VN_stock_chart_tool
from tools.draw_coin_chart import draw_coin_chart_tool
from tools.get_today_tool import get_time_tool
from tools.coin_price_tool import query_coin_latest_price_tool ,get_current_coin_price_tool
from tools.coin_metadata import query_coin_metadata_tool
from langchain_community.tools.tavily_search import TavilySearchResults
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if TAVILY_API_KEY is None:
    raise ValueError("TAVILY_API_KEY not found in environment variables.")

# ==== Các tool ====
search = TavilySearchResults(max_results=10, tavily_api_key=TAVILY_API_KEY)
tools = [
    search,
    stock_metadata_tool
    ,
    draw_coin_chart_tool ,
    # get_current_coin_price_tool,
    query_VN_financial_statement_tool ,
    VN_stock_price_tool ,
    draw_VN_stock_chart_tool,
    query_coin_latest_price_tool,
    query_coin_metadata_tool
    ,
    get_time_tool,
    Tool(
        name="get_stock_price",
        description="Lấy giá cổ phiếu hiện tại. Input: mã cổ phiếu (ví dụ: AAPL).",
        func=get_stock_price
    ),
    Tool(
        name="draw_stock_chart",
        description="Vẽ biểu đồ giá cổ phiếu theo khoảng thời gian. Input: mã cổ phiếu (ví dụ: AAPL), start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).",
        func=draw_stock_chart
    ),

    Tool(
        name="get_company_info",
        description="Lấy thông tin cơ bản về công ty mỹ . Input: mã cổ phiếu hoặc tên công ty  (ví dụ: MSFT).",
        func=get_company_info
    ),

    Tool(
        name="get_financial_statement",
        description="Lấy báo cáo tài chính của công ty. Input: mã cổ phiếu (ví dụ: AMZN).",
        func=get_financial_statement
    ),
    
    Tool(
        name="explain_financial_term",
        description="Giải thích một thuật ngữ tài chính bất kỳ. Input: tên thuật ngữ (ví dụ: EBITDA, PE ratio).",
        func=explain_financial_term
    ),

    Tool(
        name="compare_stocks",
        description="So sánh thông tin nhiều cổ phiếu. Input: danh sách các mã cổ phiếu (ví dụ: ['AAPL', 'GOOG', 'MSFT']).",
        func=compare_stocks
    ),

    Tool(
        name="suggest_investment_ideas",
        description="Gợi ý các xu hướng và ý tưởng đầu tư nổi bật.",
        func=suggest_investment_ideas
    ),
    Tool(
        name="summarize_financial_news",
        description="Tóm tắt tin tức tài chính liên quan đến một từ khóa (ví dụ: lãi suất, Nvidia, Apple).",
        func=summarize_financial_news
    ),
    Tool(
        name="chatbot_general_response",
        description="Trả lời các câu hỏi tổng quát, có thể không liên quan đến tài chính hoặc trò chuyện chung chung không cần dùng công cụ. Input: nội dung câu hỏi.",
        func=chatbot_general_response
    ),

    
]
