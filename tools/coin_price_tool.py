import requests
from langchain.tools import Tool
def get_coin_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Gây lỗi nếu mã trạng thái HTTP không phải 200
        data = response.json()
        return float(data['price'])
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        return None
get_current_coin_price_tool = Tool(
    name= 'get_current_coin_price_tool',
    func= get_coin_price,
    description= 'Lấy giá coin hiện tại . Input : mã coin(USDT) (VD : BTCUSDT , ETHUSDT)'
    
)
    
    

    