import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

import requests
import matplotlib.pyplot as plt
import datetime
import io
import base64
from typing import List
import sys
import os 
load_dotenv()
ALPHAVANTAGE_API_KEY = os.environ["ALPHAVANTAGE_API_KEY"]

# 1. Lấy giá cổ phiếu hiện tại
def get_stock_price(symbol: str) -> str:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    response = requests.get(url).json()
    try:
        price = response["Global Quote"]["05. price"]
        return f"Giá hiện tại của {symbol} là {price} USD."
    except:
        return f"Không lấy được giá cho {symbol}."

# 2. Vẽ biểu đồ cổ phiếu

def draw_stock_chart(symbol: str, start_date: str = None, end_date: str = None) -> str:
    """Vẽ biểu đồ giá cổ phiếu từ start_date đến end_date và trả về tin nhắn xác nhận."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}&outputsize=full"
    response = requests.get(url)
    data = response.json()

    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        st.error("❌ Không lấy được dữ liệu biểu đồ.")
        return "❌ Không có dữ liệu để vẽ."

    # DataFrame xử lý chuẩn
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={"4. close": "Close"})
    df["Close"] = df["Close"].astype(float)

    # Lọc theo ngày
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.index <= pd.to_datetime(end_date)]

    if df.empty:
        st.warning("⚠️ Không có dữ liệu trong khoảng thời gian đã chọn.")
        return "⚠️ Không có dữ liệu để vẽ."

    # Vẽ trực tiếp
    st.line_chart(df["Close"], use_container_width=True)

    # Trả về text thông báo
    return f"✅ Đã vẽ xong biểu đồ giá cổ phiếu {symbol} từ {start_date} đến {end_date}."




# 3. Lấy thông tin công ty
def get_company_info(symbol: str) -> str:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    data = requests.get(url).json()
    if not data:
        return f"Không tìm thấy thông tin cho {symbol}."
    description = data.get("Description", "Không có mô tả chi tiết.")
    sector = data.get("Sector", "Chưa rõ ngành.")
    return f"{symbol}: {description} Ngành: {sector}"

# 4. Lấy báo cáo tài chính
def get_financial_statement(symbol: str) -> str:
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    data = requests.get(url).json()
    if "annualReports" not in data:
        return "Không lấy được báo cáo tài chính."
    latest_report = data["annualReports"][0]
    revenue = latest_report.get("totalRevenue", "N/A")
    net_income = latest_report.get("netIncome", "N/A")
    return f"{symbol}: Doanh thu: {revenue} USD, Lợi nhuận ròng: {net_income} USD."




# 5. Giải thích thuật ngữ tài chính (simple LLM based)
def explain_financial_term(term: str) -> str:
    # Có thể call LLM Gemini hoặc viết từ điển đơn giản trước
    return f"{term} là một thuật ngữ tài chính. Để biết chi tiết hơn, vui lòng hỏi rõ hơn."

# 6. So sánh nhiều cổ phiếu
def compare_stocks(symbols: List[str]) -> str:
    results = []
    for symbol in symbols:
        info = get_company_info(symbol)
        results.append(info)
    return "\n\n".join(results)

# 7. Gợi ý ý tưởng đầu tư
def suggest_investment_ideas() -> str:
    return "Hiện tại, ngành công nghệ, năng lượng xanh, và trí tuệ nhân tạo đang là những xu hướng đầu tư tiềm năng."

# 8. Tóm tắt tin tức tài chính (giả lập)
def summarize_financial_news(keyword: str) -> str:
    return f"Tóm tắt nhanh tin tức liên quan đến {keyword}: thị trường đang có nhiều biến động do lãi suất và chính sách tiền tệ."


