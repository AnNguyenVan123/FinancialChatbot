from datetime import datetime
from vnstock import Vnstock  # assuming you have this library
from langchain.tools import Tool
def get_VN_stock_price(symbol: str):
    stock = Vnstock().stock(symbol=symbol, source="VCI")
    history = stock.quote.history(
        start='2025-01-01',
        end=datetime.now().strftime("%Y-%m-%d"),
        interval='1m'
    )
    return f"{int(history.tail(1)['close'].values[0] *1000)} đ"

VN_stock_price_tool = Tool (
    name= 'get_VN_stock_price',
    description="Lấy giá cổ phiếu ở Việt Nam hiện tại . Nếu người dùng đưa ra tên công ty tìm mã cổ phiếu của nó để đưa vào input. Input: mã cổ phiếu  (ví dụ: VHM).",
    func= get_VN_stock_price
)
    
