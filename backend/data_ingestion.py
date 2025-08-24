import json
import boto3
import websocket
import threading
import time
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
MARKET_DATA_TABLE = os.environ['MARKET_DATA_TABLE']
CHARTS_BUCKET = os.environ['CHARTS_BUCKET']
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

# Crypto symbols to track
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']

class CryptoDataIngestion:
    def __init__(self):
        self.market_data_table = dynamodb.Table(MARKET_DATA_TABLE)
        self.ws = None
        self.running = False
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if 'data' in data:
                self.process_market_data(data['data'])
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket connection closed")
        self.running = False
    
    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        # Subscribe to kline/candlestick streams
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@kline_1m" for symbol in SYMBOLS],
            "id": 1
        }
        ws.send(json.dumps(subscribe_msg))
    
    def process_market_data(self, data):
        """Process incoming market data and store in DynamoDB"""
        try:
            kline = data['k']
            symbol = kline['s']
            timestamp = int(kline['t']) // 1000  # Convert to seconds
            
            from decimal import Decimal
            item = {
                'symbol': symbol,
                'timestamp': timestamp,
                'open': Decimal(str(kline['o'])),
                'high': Decimal(str(kline['h'])),
                'low': Decimal(str(kline['l'])),
                'close': Decimal(str(kline['c'])),
                'volume': Decimal(str(kline['v'])),
                'trades': int(kline['n']),
                'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
            }
            
            self.market_data_table.put_item(Item=item)
            logger.info(f"Stored market data for {symbol} at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    def start_websocket(self):
        """Start WebSocket connection to Binance"""
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws/",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        self.running = True
        self.ws.run_forever()

def lambda_handler(event, context):
    """Lambda handler for data ingestion"""
    try:
        ingestion = CryptoDataIngestion()
        
        # For Lambda, we'll process batch data rather than maintain WebSocket
        # This would be triggered by CloudWatch Events every 5 minutes
        
        # Get recent market data from Binance REST API
        import requests
        
        results = []
        for symbol in SYMBOLS:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=5"
            response = requests.get(url)
            
            if response.status_code == 200:
                klines = response.json()
                for kline in klines:
                    timestamp = int(kline[0]) // 1000
                    
                    from decimal import Decimal
                    item = {
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'open': Decimal(str(kline[1])),
                        'high': Decimal(str(kline[2])),
                        'low': Decimal(str(kline[3])),
                        'close': Decimal(str(kline[4])),
                        'volume': Decimal(str(kline[5])),
                        'trades': int(kline[8]),
                        'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
                    }
                    
                    ingestion.market_data_table.put_item(Item=item)
                    results.append(f"Stored {symbol} data for timestamp {timestamp}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data ingestion completed',
                'results': results
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }