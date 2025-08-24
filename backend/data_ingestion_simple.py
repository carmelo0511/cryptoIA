import json
import boto3
import requests
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """Simplified Lambda handler for data ingestion testing"""
    try:
        # Test basic functionality
        logger.info("Data ingestion Lambda started")
        
        # Test DynamoDB access
        if 'MARKET_DATA_TABLE' in os.environ:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(os.environ['MARKET_DATA_TABLE'])
            
            # Test write
            from decimal import Decimal
            test_item = {
                'symbol': 'TEST',
                'timestamp': int(datetime.now().timestamp()),
                'price': Decimal('50000.0'),
                'ttl': int((datetime.now() + timedelta(days=1)).timestamp())
            }
            table.put_item(Item=test_item)
            logger.info("Test item written to DynamoDB")
        
        # Test Binance API
        response = requests.get('https://api.binance.com/api/v3/ping')
        if response.status_code == 200:
            logger.info("Binance API accessible")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data ingestion test successful',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }