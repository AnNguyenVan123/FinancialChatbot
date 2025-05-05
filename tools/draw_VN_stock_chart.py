import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
from vnstock import Vnstock
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import os 
from datetime import date

CHART_DIR = "charts"
class StockChartInput(BaseModel):
    symbol: str = Field(description="Mã cổ phiếu, ví dụ: 'VIC'")
    duration: int = Field(description="Số ngày dữ liệu, phải là số nguyên dương")
    end_time: str = Field(
        default_factory=lambda: date.today().strftime('%Y-%m-%d'),
        description="Ngày kết thúc, định dạng 'YYYY-MM-DD'"
    )
   

    interval: str = Field(description="Khoảng thời gian: '1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M'", default="1D")

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

    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='-', y_on_right=False)
    chart_filename = f"chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
 

    # Plot and save to file
    mpf.plot(
        df,
        type='candle',
        style=s,
        title=f'Biểu đồ nến {symbol.upper()} ({interval})',
        ylabel='Giá (VND)',
        volume=True,
        savefig=chart_path
    )
    
    print(f"Chart saved to: {chart_path}")
    return chart_path


# Create the LangChain tool
draw_VN_stock_chart_tool = StructuredTool.from_function(
    func=draw_VN_stock_chart,
    name="draw_VN_stock_chart_tool",
    description="Tạo biểu đồ nến cho cổ phiếu Việt Nam từ dữ liệu Vnstock, hiển thị giá và khối lượng giao dịch ",
    args_schema=StockChartInput
)
    
