import json
import boto3
from datetime import datetime, timedelta
import os
import logging
from boto3.dynamodb.conditions import Key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
PATTERN_CACHE_TABLE = os.environ['PATTERN_CACHE_TABLE']
MARKET_DATA_TABLE = os.environ['MARKET_DATA_TABLE']
PREDICTIONS_TABLE = os.environ['PREDICTIONS_TABLE']
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

class APIHandler:
    def __init__(self):
        self.pattern_cache_table = dynamodb.Table(PATTERN_CACHE_TABLE)
        self.market_data_table = dynamodb.Table(MARKET_DATA_TABLE)
        self.predictions_table = dynamodb.Table(PREDICTIONS_TABLE)
    
    def get_predictions(self, symbol=None, limit=10):
        """Get recent predictions"""
        try:
            if symbol:
                response = self.predictions_table.query(
                    IndexName='symbol-created_at-index',
                    KeyConditionExpression=Key('symbol').eq(symbol),
                    ScanIndexForward=False,
                    Limit=limit
                )
            else:
                response = self.predictions_table.scan(Limit=limit)
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting predictions: {e}")
            return []
    
    def create_prediction_request(self, symbol):
        """Trigger pattern analysis for a symbol"""
        try:
            import boto3
            lambda_client = boto3.client('lambda')
            
            # Invoke pattern analysis Lambda
            function_name = f"cryptoai-analytics-pattern-analysis-{ENVIRONMENT}"
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',  # Asynchronous
                Payload=json.dumps({'symbol': symbol})
            )
            
            return {
                'message': f'Pattern analysis triggered for {symbol}',
                'request_id': response['ResponseMetadata']['RequestId']
            }
            
        except Exception as e:
            logger.error(f"Error creating prediction request: {e}")
            return {'error': str(e)}
    
    def get_patterns(self, symbol, hours=24):
        """Get cached patterns for a symbol"""
        try:
            # Get patterns from cache within the specified time window
            since_timestamp = int((datetime.now() - timedelta(hours=hours)).timestamp())
            
            response = self.pattern_cache_table.query(
                KeyConditionExpression=Key('symbol').eq(symbol) & 
                                     Key('timestamp').gte(since_timestamp),
                ScanIndexForward=False
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting patterns: {e}")
            return []
    
    def get_market_data(self, symbol, limit=100):
        """Get recent market data"""
        try:
            response = self.market_data_table.query(
                KeyConditionExpression=Key('symbol').eq(symbol),
                ScanIndexForward=False,
                Limit=limit
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return []

def cors_headers():
    """Return CORS headers"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

def lambda_handler(event, context):
    """Lambda handler for API requests"""
    try:
        handler = APIHandler()
        
        # Parse the request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        logger.info(f"Processing {http_method} {path}")
        
        # Handle OPTIONS for CORS
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': ''
            }
        
        # Route requests
        if path == '/predictions' and http_method == 'GET':
            symbol = query_params.get('symbol')
            limit = int(query_params.get('limit', 10))
            predictions = handler.get_predictions(symbol, limit)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'predictions': predictions,
                    'count': len(predictions)
                }, default=str)
            }
        
        elif path == '/predictions' and http_method == 'POST':
            try:
                request_body = json.loads(body) if body else {}
                symbol = request_body.get('symbol', 'BTCUSDT')
                
                result = handler.create_prediction_request(symbol)
                
                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps(result)
                }
                
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        
        elif path == '/patterns' and http_method == 'GET':
            symbol = query_params.get('symbol')
            if not symbol:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({'error': 'Symbol parameter is required'})
                }
            
            hours = int(query_params.get('hours', 24))
            patterns = handler.get_patterns(symbol, hours)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'symbol': symbol,
                    'patterns': patterns,
                    'count': len(patterns)
                }, default=str)
            }
        
        elif path == '/market-data' and http_method == 'GET':
            symbol = query_params.get('symbol')
            if not symbol:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({'error': 'Symbol parameter is required'})
                }
            
            limit = int(query_params.get('limit', 100))
            market_data = handler.get_market_data(symbol, limit)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'symbol': symbol,
                    'market_data': market_data,
                    'count': len(market_data)
                }, default=str)
            }
        
        elif path == '/analyze-chart' and http_method == 'POST':
            try:
                request_body = json.loads(body) if body else {}
                symbol = request_body.get('symbol', 'BTCUSDT')
                
                # Trigger vision-based pattern analysis
                result = handler.create_prediction_request(symbol)
                
                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': json.dumps({
                        'message': f'Vision analysis started for {symbol}',
                        'result': result
                    })
                }
                
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': cors_headers(),
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Not Found'})
            }
    
    except Exception as e:
        logger.error(f"API handler error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal Server Error'})
        }