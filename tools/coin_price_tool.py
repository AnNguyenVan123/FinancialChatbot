import boto3
from boto3.dynamodb.conditions import Key
from langchain.tools import Tool
from aws_db import coin_prices_table
import requests
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

def query_coin_latest_price(symbol):
    try:
        print(f"Querying price for symbol: {symbol}")
        response = coin_prices_table.query(
            KeyConditionExpression=Key('symbol').eq(symbol),
            ScanIndexForward=False,  # Lấy bản ghi mới nhất
            Limit=1
        )
        print("DynamoDB response:", response)

        items = response.get('Items', [])
        if not items:
            return {"error": f"Không tìm thấy giá cho {symbol}"}
        return items[0]
    except Exception as e:
        print("Exception when querying DynamoDB:", e)
        return {"error": f"Lỗi khi truy vấn dữ liệu: {str(e)}"}

query_coin_latest_price_tool = Tool(
    name="query_coin_latest_price_tool",
    func=query_coin_latest_price,
    description="Lấy giá coin mới nhất (hôm nay, hiện nay). Input: mã coin (VD: BTC, ETH)"
)
