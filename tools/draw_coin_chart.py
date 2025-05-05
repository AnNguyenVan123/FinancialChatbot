import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import os 
from datetime import date
from binance.client import Client

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
    valid_intervals = {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'}
    if interval not in valid_intervals:
        raise ValueError(f"interval không hợp lệ. Chỉ chấp nhận: {', '.join(valid_intervals)}")

    try:
        end_date = datetime.strptime(end_time, "%Y-%m-%d")
    except ValueError:
        raise ValueError("end_time phải có định dạng 'YYYY-MM-DD'")

    if not isinstance(duration, int) or duration <= 0:
        raise ValueError("duration phải là số nguyên dương")

    start_date = end_date - timedelta(days=duration)

    # Khởi tạo client Binance (không cần API key nếu chỉ truy vấn public)
    client = Client()

    klines = client.get_historical_klines(
        symbol=symbol.upper(),
        interval=interval,
        start_str=start_date.strftime('%Y-%m-%d'),
        end_str=end_date.strftime('%Y-%m-%d')
    )

    if not klines:
        raise ValueError(f"Không có dữ liệu cho {symbol} từ {start_date.strftime('%Y-%m-%d')} đến {end_date.strftime('%Y-%m-%d')} với interval {interval}")

    # Tạo DataFrame
    df = pd.DataFrame(klines, columns=[
        'time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_time', 'Quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base_volume', 'Taker_buy_quote_volume', 'Ignore'
    ])

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    df = df.astype(float)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='-', y_on_right=False)
    chart_filename = f"chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)

    mpf.plot(
        df,
        type='candle',
        style=s,
        title=f'Biểu đồ nến {symbol.upper()} ({interval})',
        ylabel='Giá (USDT)',
        volume=True,
        savefig=chart_path
    )

    print(f"Chart saved to: {chart_path}")
    return chart_path


# Create the LangChain tool
draw_coin_chart_tool = StructuredTool.from_function(
    func=draw_coin_chart,
    name="draw_coin_chart_tool",
    description="Tạo biểu đồ nến cho tiền điện tử , hiển thị giá và khối lượng giao dịch ",
    args_schema= CoinChartInput
)



    