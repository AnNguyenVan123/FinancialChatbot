from datetime import date
from langchain.tools import Tool
def get_time():
     return date.today().strftime('%Y-%m-%d')

get_time_tool = Tool(
    func= get_time ,
    description="Lấy thời gian hiện tại",
    name= "get_time_tool"
    
)