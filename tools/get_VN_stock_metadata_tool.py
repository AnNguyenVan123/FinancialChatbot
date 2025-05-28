import json
import logging
from typing import Optional
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
from langchain_core.prompts import ChatPromptTemplate
from aws_db import stock_metadata_table
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from llm import llm
from langchain_core.callbacks import CallbackManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup LLM and prompt template
llm.callback_manager = CallbackManager([])

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a financial assistant. Answer the question based on the following context:\n{context}"),
    ("human", "{question}")
])

chain = prompt | llm

def query_stock_metadata(symbol: str, question: str) -> str:
    """Fetch stock metadata from DynamoDB and answer the question using an LLM."""
    try:
      if not symbol or not question:
        return "Error: Both 'symbol' and 'question' must be provided."

    # Retrieve record
      response = stock_metadata_table.get_item(Key={'Mã CK': symbol})
      item = response.get('Item')

      if item:
        # Convert item (dictionary) to string format for context
        context = json.dumps(item, ensure_ascii=False, indent=2)  # Or str(item) if you prefer a simpler format
      else:
        context = "No information found for the stock symbol."

      if not context.strip():
        return "Error: No context available to answer the question."

    # Call LLM chain
      response = chain.invoke({"context": context, "question": question})
      return response.content

  


    except ClientError as e:
        logger.error(f"DynamoDB error for symbol {symbol}: {e.response['Error']['Message']}")
        return "Error: Could not retrieve stock data."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error generating response: {str(e)}"



class StockMetadataInput(BaseModel):
    symbol: str = Field(description="Stock symbol, e.g., AAPL or VHM")
    question: str = Field(description="Question about the company")

stock_metadata_tool = StructuredTool.from_function(
    name="StockMetadataTool",
    description="Output : Toàn bộ thông tin cổ phiếu, thông tin cơ bản về công ty Việt Nam . Input: mã cổ phiếu hoặc tên công ty  (ví dụ: Vingroup hoặc VHM). ",
    func=query_stock_metadata,
    args_schema=StockMetadataInput
)



