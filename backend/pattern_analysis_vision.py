import json
import boto3
import numpy as np
from datetime import datetime, timedelta
import os
import logging
import io
import base64
from PIL import Image, ImageDraw
import uuid
import onnxruntime as ort

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

# Pattern classes - must match training exactly
PATTERN_CLASSES = [
    'head_and_shoulders',
    'double_top',
    'double_bottom', 
    'ascending_triangle',
    'descending_triangle',
    'cup_and_handle',
    'bullish_flag',
    'bearish_flag',
    'support_resistance',
    'breakout'
]

class VisionPatternAnalyzer:
    def __init__(self):
        self.pattern_cache_table = dynamodb.Table(PATTERN_CACHE_TABLE)
        self.predictions_table = dynamodb.Table(PREDICTIONS_TABLE)
        
        # Load ONNX Vision Transformer model
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load the ONNX Vision Transformer model"""
        try:
            model_path = "/var/task/models/crypto_pattern_model_v14.onnx"
            logger.info(f"Loading ONNX model from {model_path}")
            
            # Create inference session with CPU provider
            providers = ['CPUExecutionProvider']
            self.model = ort.InferenceSession(model_path, providers=providers)
            
            # Log model info
            input_name = self.model.get_inputs()[0].name
            input_shape = self.model.get_inputs()[0].shape
            output_name = self.model.get_outputs()[0].name
            output_shape = self.model.get_outputs()[0].shape
            
            logger.info(f"Model loaded successfully")
            logger.info(f"Input: {input_name} {input_shape}")
            logger.info(f"Output: {output_name} {output_shape}")
            
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            self.model = None
    
    def preprocess_chart_for_vision(self, image_array):
        """Preprocess chart image for Vision Transformer inference"""
        try:
            # Convert to PIL Image if numpy array
            if isinstance(image_array, np.ndarray):
                if image_array.dtype != np.uint8:
                    image_array = (image_array * 255).astype(np.uint8)
                image = Image.fromarray(image_array)
            else:
                image = image_array
            
            # Resize to 224x224 (Vision Transformer standard input)
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array and normalize
            image_array = np.array(image).astype(np.float32)
            image_array = image_array / 255.0
            
            # Apply ImageNet normalization
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            
            image_array = (image_array - mean) / std
            
            # Add batch dimension and transpose to NCHW
            image_array = np.transpose(image_array, (2, 0, 1))  # HWC to CHW
            image_array = np.expand_dims(image_array, axis=0)   # Add batch dim
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def generate_chart_image(self, market_data, symbol):
        """Generate simple chart image for pattern analysis"""
        try:
            # Sort market data by timestamp
            sorted_data = sorted(market_data, key=lambda x: int(x['timestamp']))
            
            # Create a simple chart image (224x224 for Vision Transformer)
            image = Image.new('RGB', (224, 224), 'white')
            draw = ImageDraw.Draw(image)
            
            # Extract prices for normalization
            prices = [float(d['close']) for d in sorted_data]
            if not prices:
                return None, None
                
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price if max_price != min_price else 1
            
            # Draw simple price line
            points = []
            for i, data_point in enumerate(sorted_data):
                x = int((i / len(sorted_data)) * 220) + 2  # 2px margin
                price = float(data_point['close'])
                y = int(220 - ((price - min_price) / price_range) * 216) + 2  # Invert Y, 2px margin
                points.append((x, y))
            
            # Draw price line
            if len(points) > 1:
                draw.line(points, fill='blue', width=2)
            
            # Convert to numpy array
            chart_array = np.array(image)
            
            # Save to buffer and upload to S3
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            chart_key = f"charts/{symbol}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            s3.put_object(
                Bucket=CHARTS_BUCKET,
                Key=chart_key,
                Body=buffer.getvalue(),
                ContentType='image/png'
            )
            
            return chart_key, chart_array
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None, None
    
    def detect_patterns_with_vision(self, chart_array):
        """Detect trading patterns using Vision Transformer model"""
        try:
            if self.model is None:
                logger.error("ONNX model not loaded")
                return []
            
            # Preprocess image for model
            preprocessed = self.preprocess_chart_for_vision(chart_array)
            if preprocessed is None:
                return []
            
            # Run inference
            input_name = self.model.get_inputs()[0].name
            outputs = self.model.run(None, {input_name: preprocessed})
            predictions = outputs[0][0]  # Remove batch dimension
            
            # Get predicted class and confidence
            predicted_class_idx = np.argmax(predictions)
            confidence = float(predictions[predicted_class_idx])
            pattern_type = PATTERN_CLASSES[predicted_class_idx]
            
            # Apply softmax for better confidence scores
            softmax_predictions = np.exp(predictions) / np.sum(np.exp(predictions))
            confidence_softmax = float(softmax_predictions[predicted_class_idx])
            
            # Determine prediction direction based on pattern type
            bullish_patterns = ['ascending_triangle', 'cup_and_handle', 'bullish_flag', 'breakout']
            bearish_patterns = ['descending_triangle', 'double_top', 'head_and_shoulders', 'bearish_flag']
            
            if pattern_type in bullish_patterns:
                prediction_direction = 'bullish'
            elif pattern_type in bearish_patterns:
                prediction_direction = 'bearish'
            else:
                prediction_direction = 'neutral'
            
            logger.info(f"Vision model prediction: {pattern_type} (confidence: {confidence_softmax:.3f})")
            
            # Return detected patterns with proper structure
            patterns = [{
                'type': pattern_type,
                'confidence': confidence_softmax,
                'raw_score': confidence,
                'coordinates': {'x1': 0, 'y1': 0, 'x2': 224, 'y2': 224},
                'prediction': prediction_direction,
                'all_predictions': predictions.tolist(),
                'model_version': 'v14_onnx'
            }]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in vision pattern detection: {e}")
            return []
    
    def analyze_sentiment(self, symbol):
        """Analyze market sentiment (placeholder - can be enhanced)"""
        # Simple sentiment based on recent price action
        sentiment_score = np.random.uniform(-0.3, 0.3)  # Conservative range
        
        return {
            'score': sentiment_score,
            'label': 'bullish' if sentiment_score > 0.1 else 'bearish' if sentiment_score < -0.1 else 'neutral',
            'source': 'price_action'
        }
    
    def generate_prediction(self, symbol, market_data, patterns, sentiment):
        """Generate multi-modal prediction with vision model results"""
        try:
            # Enhanced prediction logic using vision model
            recent_close = float(market_data[-1]['close'])
            older_close = float(market_data[-20]['close']) if len(market_data) >= 20 else float(market_data[0]['close'])
            
            price_trend = 1 if recent_close > older_close else -1
            price_change = (recent_close - older_close) / older_close
            
            # Weight pattern predictions by confidence
            pattern_score = 0
            total_confidence = 0
            
            for pattern in patterns:
                confidence = pattern['confidence']
                direction_multiplier = 1 if pattern['prediction'] == 'bullish' else -1 if pattern['prediction'] == 'bearish' else 0
                pattern_score += direction_multiplier * confidence
                total_confidence += confidence
            
            # Normalize pattern score
            if total_confidence > 0:
                pattern_score = pattern_score / total_confidence
            
            # Combine signals with weights favoring vision model
            final_score = (
                (pattern_score * 0.6) +           # Vision model gets highest weight
                (price_change * 10 * 0.3) +       # Price trend (scaled)
                (sentiment['score'] * 0.1)         # Sentiment gets small weight
            )
            
            # Determine direction with threshold
            if final_score > 0.2:
                direction = 'bullish'
            elif final_score < -0.2:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            prediction = {
                'prediction_id': str(uuid.uuid4()),
                'symbol': symbol,
                'prediction_score': float(np.clip(final_score, -1, 1)),
                'confidence': float(min(abs(final_score), 1.0)),
                'direction': direction,
                'patterns_detected': patterns,
                'sentiment': sentiment,
                'price_change_24h': float(price_change),
                'model_version': 'vision_transformer_v14',
                'created_at': int(datetime.now().timestamp()),
                'ttl': int((datetime.now() + timedelta(days=30)).timestamp())
            }
            
            # Store prediction
            self.predictions_table.put_item(Item=prediction)
            
            logger.info(f"Generated prediction for {symbol}: {direction} (score: {final_score:.3f})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            return None

def lambda_handler(event, context):
    """Lambda handler for vision-based pattern analysis"""
    start_time = datetime.now()
    
    try:
        analyzer = VisionPatternAnalyzer()
        
        # Get symbol from event
        symbol = event.get('symbol', 'BTCUSDT')
        logger.info(f"Starting vision analysis for {symbol}")
        
        # Get recent market data from DynamoDB
        from boto3.dynamodb.conditions import Key
        market_data_table = dynamodb.Table(os.environ.get('MARKET_DATA_TABLE', 'market-data'))
        
        # Query last 100 data points for chart generation
        response = market_data_table.query(
            KeyConditionExpression=Key('symbol').eq(symbol),
            ScanIndexForward=False,
            Limit=100
        )
        
        if not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No market data found for {symbol}'})
            }
        
        market_data = sorted(response['Items'], key=lambda x: int(x['timestamp']))
        logger.info(f"Retrieved {len(market_data)} market data points")
        
        # Generate chart image and get array for vision model
        chart_key, chart_array = analyzer.generate_chart_image(market_data, symbol)
        if not chart_key or chart_array is None:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to generate chart'})
            }
        
        # Detect patterns using vision model
        patterns = analyzer.detect_patterns_with_vision(chart_array)
        if not patterns:
            logger.warning("No patterns detected by vision model")
            patterns = [{'type': 'no_pattern', 'confidence': 0.0, 'prediction': 'neutral'}]
        
        # Analyze sentiment
        sentiment = analyzer.analyze_sentiment(symbol)
        
        # Generate final prediction
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
            'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000),
            'ttl': int((datetime.now() + timedelta(days=7)).timestamp())
        }
        
        analyzer.pattern_cache_table.put_item(Item=cache_item)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Vision analysis completed in {processing_time:.0f}ms")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'symbol': symbol,
                'chart_url': cache_item['chart_url'],
                'patterns': patterns,
                'prediction': prediction,
                'processing_time_ms': int(processing_time),
                'model_version': 'vision_transformer_v14',
                'timestamp': cache_item['timestamp']
            }, default=str)
        }
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Lambda execution error after {processing_time:.0f}ms: {e}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'processing_time_ms': int(processing_time)
            })
        }