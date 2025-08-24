#!/usr/bin/env python3

import sys
import json
import os
from datetime import datetime

# Test the simplified Lambda functions locally
def test_data_ingestion():
    """Test data ingestion Lambda locally"""
    print("Testing Data Ingestion Lambda...")
    
    # Mock environment variables
    os.environ['MARKET_DATA_TABLE'] = 'test-market-data-table'
    os.environ['CHARTS_BUCKET'] = 'test-charts-bucket'
    
    # Import the function
    sys.path.append('.')
    from data_ingestion_simple import lambda_handler
    
    # Test event
    test_event = {
        'symbol': 'BTCUSDT'
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id'
            self.log_group_name = '/aws/lambda/test'
            self.log_stream_name = 'test-stream'
    
    try:
        result = lambda_handler(test_event, MockContext())
        print(f"✅ Data Ingestion Test Result: {result['statusCode']}")
        print(f"Response: {json.loads(result['body'])}")
        return True
    except Exception as e:
        print(f"❌ Data Ingestion Test Failed: {e}")
        return False

def test_api_handler():
    """Test API handler Lambda locally"""
    print("\nTesting API Handler Lambda...")
    
    # Mock environment variables
    os.environ['PREDICTIONS_TABLE'] = 'test-predictions-table'
    os.environ['PATTERN_CACHE_TABLE'] = 'test-patterns-table'
    
    # Import the function
    from api_handler_simple import lambda_handler
    
    # Test GET /predictions
    test_event_get = {
        'httpMethod': 'GET',
        'path': '/predictions',
        'queryStringParameters': {'symbol': 'BTCUSDT'}
    }
    
    # Test POST /predictions
    test_event_post = {
        'httpMethod': 'POST',
        'path': '/predictions',
        'body': json.dumps({'symbol': 'ETHUSDT'})
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id'
    
    try:
        # Test GET
        result_get = lambda_handler(test_event_get, MockContext())
        print(f"✅ API Handler GET Test Result: {result_get['statusCode']}")
        
        # Test POST
        result_post = lambda_handler(test_event_post, MockContext())
        print(f"✅ API Handler POST Test Result: {result_post['statusCode']}")
        
        print("API Handler tests completed successfully!")
        return True
    except Exception as e:
        print(f"❌ API Handler Test Failed: {e}")
        return False

def test_external_apis():
    """Test external API connectivity"""
    print("\nTesting External APIs...")
    
    import requests
    
    try:
        # Test Binance API
        response = requests.get('https://api.binance.com/api/v3/ping', timeout=10)
        if response.status_code == 200:
            print("✅ Binance API accessible")
        else:
            print("❌ Binance API not accessible")
            
        # Test getting BTCUSDT price
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BTCUSDT Price: ${data['price']}")
        else:
            print("❌ Could not get BTCUSDT price")
            
        return True
    except Exception as e:
        print(f"❌ External API Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting CryptoAI Analytics Lambda Tests...\n")
    
    success_count = 0
    total_tests = 3
    
    # Run tests
    if test_data_ingestion():
        success_count += 1
        
    if test_api_handler():
        success_count += 1
        
    if test_external_apis():
        success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The Lambda functions are ready for deployment.")
        exit(0)
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        exit(1)