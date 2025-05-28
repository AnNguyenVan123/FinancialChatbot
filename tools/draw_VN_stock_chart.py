import os
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta, date
from vnstock import Vnstock
from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.tools import StructuredTool
from llm import llm
# Cấu hình
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# Mô hình LLM (OpenAI, nhưng bạn có thể thay thế bằng bất kỳ langchain-compatible LLM nào)


class StockChartInput(BaseModel):
    symbol: str = Field(description="Mã cổ phiếu, ví dụ: 'VIC'")
    duration: int = Field(description="Số ngày dữ liệu, phải là số nguyên dương")
    end_time: str = Field(
        default_factory=lambda: date.today().strftime('%Y-%m-%d'),
        description="Ngày kết thúc, định dạng 'YYYY-MM-DD'"
    )
    interval: str = Field(
        description="Khoảng thời gian: '1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M'",
        default="1D"
    )

def draw_VN_stock_chart(symbol: str, duration: int, end_time: str, interval: str = '1D') -> str:
    valid_intervals = {'1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M'}
    if interval not in valid_intervals:
        raise ValueError(f"interval không hợp lệ. Chỉ chấp nhận: {', '.join(valid_intervals)}")

    try:
        end_date = datetime.strptime(end_time, "%Y-%m-%d")
    except ValueError:
        raise ValueError("end_time phải có định dạng 'YYYY-MM-DD'")

    if not isinstance(duration, int) or duration <= 0:
        raise ValueError("duration phải là số nguyên dương")

    start_date = end_date - timedelta(days=duration)

    stock = Vnstock().stock(symbol=symbol, source='VCI')
    df = stock.quote.history(
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval=interval
    )

    if df.empty:
        raise ValueError(f"Không có dữ liệu cho {symbol} từ {start_date.strftime('%Y-%m-%d')} đến {end_date.strftime('%Y-%m-%d')} với interval {interval}")

    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Tính MSI
    df['MSI'] = (df['Close'] - df['Low']) / (df['High'] - df['Low']).replace(0, 1)

    # Tạo thêm chỉ báo phụ
    apds = [mpf.make_addplot(df['MSI'], panel=1, color='purple', ylabel='MSI')]

    # Style biểu đồ
    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='-', y_on_right=False)

    # Lưu biểu đồ
    chart_filename = f"chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)

    mpf.plot(
        df,
        type='candle',
        style=s,
        title=f'Biểu đồ nến {symbol.upper()} ({interval})',
        ylabel='Giá (VND)',
        volume=True,
        mav=(10, 20),
        addplot=apds,
        savefig=chart_path
    )

    # Trích xuất dữ liệu 20 dòng cuối
    last_data = df[['Open', 'High', 'Low', 'Close', 'Volume', 'MSI']].tail(20).to_string()

    # Prompt phân tích kỹ thuật
    prompt = f"""
Dưới đây là dữ liệu kỹ thuật 20 phiên gần nhất của mã cổ phiếu {symbol.upper()}:

{last_data}

Hãy phân tích kỹ thuật ngắn hạn cho cổ phiếu này dựa trên xu hướng giá, khối lượng, MA10, MA20, và chỉ báo MSI.
Đưa ra nhận định xu hướng sắp tới và rủi ro chính nếu có.
"""

    response = llm([
        SystemMessage(content="Bạn là một chuyên gia phân tích kỹ thuật chứng khoán."),
        HumanMessage(content=prompt)
    ])

    return (
    
        f"🤖{response.content}"
    )

# LangChain tool
draw_VN_stock_chart_tool = StructuredTool.from_function(
    func=draw_VN_stock_chart,
    name="draw_VN_stock_chart_tool",
    description="Vẽ biểu đồ nến cho cổ phiếu VN, tích hợp MA, MSI, trích xuất dữ liệu 20 phiên và gọi LLM để phân tích kỹ thuật.",
    args_schema=StockChartInput,
    return_direct=True
)
