from aws_db import coin_metadata_table
from langchain.tools import Tool
def query_coin_metadata(symbol):
    try:
        response = coin_metadata_table.get_item(Key={'symbol': symbol})
        item = response.get('Item')
        if item:
            return item
        else:
            return {"error": f"Không tìm thấy metadata cho {symbol}"}
    except Exception as e:
        return {"error": str(e)}


query_coin_metadata_tool = Tool(
    name="query_coin_metadata_tool",
    func=query_coin_metadata,
    description="Truy vấn thông tin metadata của coin. Input: mã coin, ví dụ: BTC, ETH"
)

