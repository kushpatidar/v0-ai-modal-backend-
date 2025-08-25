from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class FraudDetectionModel:
    """Simple fraud detection model for demonstration"""
    
    def __init__(self):
        # In a real implementation, you would load a trained model here
        self.risk_factors = {
            'high_amount_threshold': 1000,
            'suspicious_merchants': ['unknown', 'cash_advance', 'gambling'],
            'unusual_times': ['late_night', 'early_morning'],
            'high_risk_locations': ['foreign', 'unknown']
        }
    
    def extract_features(self, transaction_data):
        """Extract features from transaction data"""
        features = {}
        
        # Amount-based features
        amount = transaction_data.get('amount', 0)
        features['amount'] = amount
        features['high_amount'] = amount > self.risk_factors['high_amount_threshold']
        
        # Merchant-based features
        merchant = transaction_data.get('merchant', '').lower()
        features['merchant'] = merchant
        features['suspicious_merchant'] = any(sus in merchant for sus in self.risk_factors['suspicious_merchants'])
        
        # Time-based features
        time = transaction_data.get('time', '')
        features['time'] = time
        features['unusual_time'] = self._is_unusual_time(time)
        
        # Location-based features
        location = transaction_data.get('location', '').lower()
        features['location'] = location
        features['high_risk_location'] = any(risk in location for risk in self.risk_factors['high_risk_locations'])
        
        # Card type
        features['card_type'] = transaction_data.get('card_type', 'unknown')
        
        return features
    
    def _is_unusual_time(self, time_str):
        """Check if transaction time is unusual"""
        try:
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
                return hour < 6 or hour > 23
        except:
            pass
        return False
    
    def predict(self, transaction_data):
        """Predict fraud probability"""
        features = self.extract_features(transaction_data)
        
        # Simple rule-based scoring (in reality, you'd use ML model)
        risk_score = 0.0
        
        if features['high_amount']:
            risk_score += 0.3
        
        if features['suspicious_merchant']:
            risk_score += 0.4
        
        if features['unusual_time']:
            risk_score += 0.2
        
        if features['high_risk_location']:
            risk_score += 0.3
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine prediction
        prediction = 'fraud' if risk_score > 0.5 else 'legitimate'
        confidence = risk_score if prediction == 'fraud' else 1 - risk_score
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'risk_score': risk_score,
            'features': features
        }

# Initialize model
model = FraudDetectionModel()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/predict', methods=['POST'])
def predict_fraud():
    """Main prediction endpoint"""
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse transaction data
        if 'data' in request_data:
            try:
                transaction_data = json.loads(request_data['data'])
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format in data field'}), 400
        else:
            transaction_data = request_data
        
        logger.info(f"Processing transaction: {transaction_data}")
        
        # Make prediction
        result = model.predict(transaction_data)
        
        logger.info(f"Prediction result: {result['prediction']} (confidence: {result['confidence']:.2f})")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Batch prediction endpoint"""
    try:
        request_data = request.get_json()
        
        if not request_data or 'transactions' not in request_data:
            return jsonify({'error': 'No transactions provided'}), 400
        
        transactions = request_data['transactions']
        results = []
        
        for i, transaction in enumerate(transactions):
            try:
                result = model.predict(transaction)
                result['transaction_id'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing transaction {i}: {str(e)}")
                results.append({
                    'transaction_id': i,
                    'error': str(e)
                })
        
        return jsonify({'results': results})
    
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
