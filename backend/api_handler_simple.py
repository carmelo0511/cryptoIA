import json
import boto3
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }

def lambda_handler(event, context):
    """Simplified API handler for testing"""
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        logger.info(f"Processing {http_method} {path}")
        
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': ''
            }
        
        # Test DynamoDB access
        if 'PREDICTIONS_TABLE' in os.environ:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(os.environ['PREDICTIONS_TABLE'])
            
            # Test response
            response_data = {
                'status': 'API test successful',
                'timestamp': datetime.now().isoformat(),
                'path': path,
                'method': http_method
            }
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(response_data)
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'message': 'API handler test - no database configured'
            })
        }
        
    except Exception as e:
        logger.error(f"API handler error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }