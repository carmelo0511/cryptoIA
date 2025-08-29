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
        logger.info("Starting data ingestion Lambda")
        ingestion = CryptoDataIngestion()
        
        # For Lambda, we'll process batch data rather than maintain WebSocket
        # This would be triggered by CloudWatch Events every 5 minutes
        
        # Get recent market data from Binance REST API
        import requests
        
        results = []
        # Switch to CoinGecko API due to Binance geo-blocking Lambda IPs
        coingecko_symbols = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum', 
            'ADAUSDT': 'cardano',
            'SOLUSDT': 'solana',
            'DOTUSDT': 'polkadot'
        }
        
        logger.info(f"Processing symbols via CoinGecko: {list(coingecko_symbols.keys())}")
        
        # Get current prices for all coins in one request
        coin_ids = ','.join(coingecko_symbols.values())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
        logger.info(f"Fetching data from CoinGecko: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            prices = response.json()
            logger.info(f"Got prices for {len(prices)} coins")
            current_timestamp = int(datetime.now().timestamp())
            
            for binance_symbol, coingecko_id in coingecko_symbols.items():
                if coingecko_id in prices and 'usd' in prices[coingecko_id]:
                    price = prices[coingecko_id]['usd']
                    
                    from decimal import Decimal
                    # Store simplified market data (CoinGecko doesn't provide OHLCV in simple/price)
                    item = {
                        'symbol': binance_symbol,
                        'timestamp': current_timestamp,
                        'price': Decimal(str(price)),
                        'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
                    }
                    
                    ingestion.market_data_table.put_item(Item=item)
                    results.append(f"Stored {binance_symbol} price {price} for timestamp {current_timestamp}")
                    logger.info(f"Stored {binance_symbol} price {price} for timestamp {current_timestamp}")
        else:
            logger.error(f"Failed to fetch data from CoinGecko: {response.status_code}")
        
        logger.info(f"Completed data ingestion with {len(results)} items stored")
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