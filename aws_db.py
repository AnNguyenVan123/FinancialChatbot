import boto3
import os
from boto3.session import Session
boto3.setup_default_session(
    aws_access_key_id= os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"]
)
# AWS clients
s3_client = boto3.client('s3')
FINANCIAL_REPORT_BUCKET = 'financial-data-chatbot'
dynamodb = boto3.resource('dynamodb')

stock_metadata_table = dynamodb.Table('stock-metadata')
qdrant_s3_links_table = dynamodb.Table('document_links')
finacial_statement_table =  dynamodb.Table('financial_statements')

nam_session = boto3.Session(
    aws_access_key_id=os.environ["Nam_AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["Nam_AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["Nam_AWS_REGION"]
)

nam_dynamodb = nam_session.resource('dynamodb')

# Truy cập đúng bảng từ session này
coin_metadata_table = nam_dynamodb.Table('coin-metadata')
coin_prices_table = nam_dynamodb.Table('coin-prices')


