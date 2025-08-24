import json
import boto3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import logging
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
PATTERN_CACHE_TABLE = os.environ['PATTERN_CACHE_TABLE']
PREDICTIONS_TABLE = os.environ['PREDICTIONS_TABLE']
CHARTS_BUCKET = os.environ['CHARTS_BUCKET']
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')

class PatternAnalyzer:
    def __init__(self):
        self.pattern_cache_table = dynamodb.Table(PATTERN_CACHE_TABLE)
        self.predictions_table = dynamodb.Table(PREDICTIONS_TABLE)
        # Note: Vision Transformer model will be loaded here once trained
        self.model = None
        
    def generate_chart_image(self, market_data, symbol):
        """Generate candlestick chart image for pattern analysis"""
        try:
            df = pd.DataFrame(market_data)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('datetime')
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create candlestick chart
            for idx, row in df.iterrows():
                color = 'green' if row['close'] >= row['open'] else 'red'
                
                # Body
                body_height = abs(row['close'] - row['open'])
                body_bottom = min(row['open'], row['close'])
                
                ax.add_patch(Rectangle(
                    (mdates.date2num(row['datetime']), body_bottom),
                    0.6, body_height,
                    facecolor=color, alpha=0.7
                ))
                
                # Wicks
                ax.plot([mdates.date2num(row['datetime']), mdates.date2num(row['datetime'])],
                       [row['low'], row['high']], color='black', linewidth=1)
            
            ax.set_title(f'{symbol} Price Chart', fontsize=16)
            ax.set_ylabel('Price (USDT)', fontsize=12)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.grid(True, alpha=0.3)
            
            # Save to bytes
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # Upload to S3
            chart_key = f"charts/{symbol}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            s3.put_object(
                Bucket=CHARTS_BUCKET,
                Key=chart_key,
                Body=buffer.getvalue(),
                ContentType='image/png'
            )
            
            plt.close()
            return chart_key
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    def detect_patterns(self, chart_image_key):
        """Detect trading patterns using Vision Transformer (placeholder)"""
        # This is a placeholder for the Vision Transformer model
        # The actual model will be implemented in Phase 2
        
        patterns = [
            {
                'type': 'bullish_flag',
                'confidence': 0.75,
                'coordinates': {'x1': 100, 'y1': 150, 'x2': 200, 'y2': 180},
                'prediction': 'bullish'
            },
            {
                'type': 'support_resistance',
                'confidence': 0.68,
                'coordinates': {'x1': 0, 'y1': 120, 'x2': 300, 'y2': 125},
                'prediction': 'neutral'
            }
        ]
        
        return patterns
    
    def analyze_sentiment(self, symbol):
        """Analyze market sentiment (placeholder)"""
        # This would integrate with news/social media APIs
        sentiment_score = np.random.uniform(-1, 1)  # Placeholder
        
        return {
            'score': sentiment_score,
            'label': 'bullish' if sentiment_score > 0.2 else 'bearish' if sentiment_score < -0.2 else 'neutral'
        }
    
    def generate_prediction(self, symbol, market_data, patterns, sentiment):
        """Generate multi-modal prediction"""
        try:
            # Simple prediction logic (to be enhanced with ML)
            price_trend = 1 if float(market_data[-1]['close']) > float(market_data[0]['close']) else -1
            pattern_weight = sum([p['confidence'] for p in patterns if p['prediction'] == 'bullish']) - \
                           sum([p['confidence'] for p in patterns if p['prediction'] == 'bearish'])
            
            final_score = (price_trend * 0.4) + (pattern_weight * 0.4) + (sentiment['score'] * 0.2)
            
            prediction = {
                'prediction_id': str(uuid.uuid4()),
                'symbol': symbol,
                'prediction_score': float(final_score),
                'confidence': min(abs(final_score), 1.0),
                'direction': 'bullish' if final_score > 0.1 else 'bearish' if final_score < -0.1 else 'neutral',
                'patterns_detected': patterns,
                'sentiment': sentiment,
                'created_at': int(datetime.now().timestamp()),
                'ttl': int((datetime.now() + timedelta(days=30)).timestamp())
            }
            
            # Store prediction
            self.predictions_table.put_item(Item=prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            return None

def lambda_handler(event, context):
    """Lambda handler for pattern analysis"""
    try:
        analyzer = PatternAnalyzer()
        
        # Get symbol from event or default
        symbol = event.get('symbol', 'BTCUSDT')
        
        # Get recent market data from DynamoDB
        from boto3.dynamodb.conditions import Key
        market_data_table = dynamodb.Table(os.environ['MARKET_DATA_TABLE'])
        
        # Query last 100 data points
        response = market_data_table.query(
            KeyConditionExpression=Key('symbol').eq(symbol),
            ScanIndexForward=False,
            Limit=100
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No market data found'})
            }
        
        market_data = sorted(response['Items'], key=lambda x: x['timestamp'])
        
        # Generate chart image
        chart_key = analyzer.generate_chart_image(market_data, symbol)
        if not chart_key:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to generate chart'})
            }
        
        # Detect patterns
        patterns = analyzer.detect_patterns(chart_key)
        
        # Analyze sentiment
        sentiment = analyzer.analyze_sentiment(symbol)
        
        # Generate prediction
        prediction = analyzer.generate_prediction(symbol, market_data, patterns, sentiment)
        
        if not prediction:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to generate prediction'})
            }
        
        # Cache results
        cache_item = {
            'symbol': symbol,
            'timestamp': int(datetime.now().timestamp()),
            'chart_url': f"s3://{CHARTS_BUCKET}/{chart_key}",
            'patterns': patterns,
            'prediction': prediction,
            'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
        }
        
        analyzer.pattern_cache_table.put_item(Item=cache_item)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'symbol': symbol,
                'chart_url': cache_item['chart_url'],
                'patterns': patterns,
                'prediction': prediction,
                'timestamp': cache_item['timestamp']
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }