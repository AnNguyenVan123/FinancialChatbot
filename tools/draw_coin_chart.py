import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import os 
from datetime import date
from binance.client import Client
from binance.exceptions import BinanceAPIException
from llm import llm
from langchain.schema import SystemMessage, HumanMessage
CHART_DIR = "charts"
class CoinChartInput(BaseModel):
    symbol: str = Field(description="Mã cặp tiền điện tử, ví dụ: 'BTCUSDT', 'ETHUSDT'")
    duration: int = Field(description="Số ngày dữ liệu, phải là số nguyên dương")
    end_time: str = Field(
        default_factory=lambda: date.today().strftime('%Y-%m-%d'),
        description="Ngày kết thúc, định dạng 'YYYY-MM-DD'"
    )
    interval: str = Field(
        default="1d",
        description="Khoảng thời gian: '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'. Mặc định 1 ngày"
    )
# Đường dẫn lưu biểu đồ
CHART_DIR = "./charts"
os.makedirs(CHART_DIR, exist_ok=True)

def draw_coin_chart(symbol: str, duration: int, end_time: str, interval: str = '1d') -> str:
    try:
        valid_intervals = {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'}
        if interval not in valid_intervals:
            raise ValueError(f"interval không hợp lệ. Chỉ chấp nhận: {', '.join(valid_intervals)}")

        end_date = datetime.strptime(end_time, "%Y-%m-%d")
        if not isinstance(duration, int) or duration <= 0:
            raise ValueError("duration phải là số nguyên dương")
        start_date = end_date - timedelta(days=duration)

        client = Client()
        klines = client.get_historical_klines(
            symbol=symbol.upper(),
            interval=interval,
            start_str=start_date.strftime('%Y-%m-%d'),
            end_str=end_date.strftime('%Y-%m-%d')
        )

        if not klines:
            raise ValueError(f"Không có dữ liệu cho {symbol} trong khoảng thời gian đã chọn.")

        df = pd.DataFrame(klines, columns=[
            'time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close_time', 'Quote_asset_volume', 'Number_of_trades',
            'Taker_buy_base_volume', 'Taker_buy_quote_volume', 'Ignore'
        ])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', inplace=True)
        df = df.astype(float)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

        # Vẽ biểu đồ nến
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='-', y_on_right=False)
        chart_path = os.path.join(CHART_DIR, "chart.png")
        mpf.plot(df, type='candle', style=s, title=f'Biểu đồ nến {symbol.upper()} ({interval})',
                 ylabel='Giá (USDT)', volume=True, savefig=chart_path)

        # ----- PHÂN TÍCH BẰNG LLM DỰA TRÊN df.tail() -------
        recent_data = df.tail(30).to_string()
        prompt = f"""Dưới đây là dữ liệu nến gần nhất của cặp tiền điện tử {symbol.upper()}:
        
{recent_data}

Hãy phân tích kỹ thuật biểu đồ này (xu hướng, hỗ trợ/kháng cự, khối lượng, mô hình nến...) và đưa ra nhận định chi tiết. Nếu có thể, hãy gợi ý hành động (mua/bán/đợi)."""

        response = llm.invoke([HumanMessage(content=prompt)])
        analysis = response.content

        return f"{analysis}"

    except BinanceAPIException:
        return "⚠️ Không thể truy cập dữ liệu Binance. Vui lòng thử lại sau."
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


# Create the LangChain tool
draw_coin_chart_tool = StructuredTool.from_function(
    func=draw_coin_chart,
    name="draw_coin_chart_tool",
    description="Tạo biểu đồ nến cho tiền điện tử , hiển thị giá và khối lượng giao dịch , dựa vào dữ liệu kline ở trong output hãy phân tích kỹ thuật biểu đồ",
    args_schema= CoinChartInput,
    return_direct=True
)



    