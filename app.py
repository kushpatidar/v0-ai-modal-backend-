from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import os
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

class FraudDetectionModel:
    def __init__(self):
        # Risk factors and weights
        self.risk_factors = {
            'high_amount': 0.3,
            'unusual_time': 0.2,
            'suspicious_merchant': 0.25,
            'foreign_location': 0.15,
            'multiple_transactions': 0.1
        }
        
        self.suspicious_merchants = [
            'unknown', 'cash advance', 'atm', 'gambling', 'adult entertainment'
        ]
        
        self.high_risk_locations = [
            'nigeria', 'russia', 'china', 'unknown location'
        ]
    
    def extract_features(self, transaction_data):
        """Extract features from transaction data"""
        features = {}
        
        try:
            # Parse amount
            amount = float(transaction_data.get('amount', 0))
            features['amount'] = amount
            features['high_amount'] = amount > 1000
            
            # Parse time
            time_str = transaction_data.get('time', '12:00')
            hour = int(time_str.split(':')[0]) if ':' in time_str else 12
            features['hour'] = hour
            features['unusual_time'] = hour < 6 or hour > 22
            
            # Parse merchant
            merchant = transaction_data.get('merchant', '').lower()
            features['merchant'] = merchant
            features['suspicious_merchant'] = any(sus in merchant for sus in self.suspicious_merchants)
            
            # Parse location
            location = transaction_data.get('location', '').lower()
            features['location'] = location
            features['foreign_location'] = any(risk in location for risk in self.high_risk_locations)
            
            # Card type
            card_type = transaction_data.get('card_type', 'unknown').lower()
            features['card_type'] = card_type
            features['credit_card'] = card_type == 'credit'
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            
        return features
    
    def calculate_risk_score(self, features):
        """Calculate risk score based on features"""
        risk_score = 0.0
        
        for factor, weight in self.risk_factors.items():
            if features.get(factor, False):
                risk_score += weight
        
        # Additional risk factors
        if features.get('amount', 0) > 5000:
            risk_score += 0.2
        
        if features.get('hour', 12) in [2, 3, 4]:
            risk_score += 0.15
            
        return min(risk_score, 1.0)
    
    def predict(self, transaction_data):
        """Make fraud prediction"""
        features = self.extract_features(transaction_data)
        risk_score = self.calculate_risk_score(features)
        
        # Determine prediction
        prediction = "fraud" if risk_score > 0.5 else "legitimate"
        confidence = risk_score if prediction == "fraud" else (1 - risk_score)
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "features": features
        }

# Initialize model
model = FraudDetectionModel()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Fraud Detection API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "Missing transaction data"}), 400
        
        # Check if data is nested in 'data' field (old format) or direct (new format)
        if 'data' in request_data:
            try:
                transaction_data = json.loads(request_data['data'])
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format in data field"}), 400
        else:
            # Direct JSON format
            transaction_data = request_data
        
        # Validate required fields
        required_fields = ['amount']
        for field in required_fields:
            if field not in transaction_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Make prediction
        result = model.predict(transaction_data)
        
        logger.info(f"Prediction made: {result['prediction']} (confidence: {result['confidence']:.2f})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Batch prediction endpoint"""
    try:
        request_data = request.get_json()
        
        if not request_data or 'transactions' not in request_data:
            return jsonify({"error": "Missing transactions data"}), 400
        
        transactions = request_data['transactions']
        results = []
        
        for i, transaction in enumerate(transactions):
            try:
                result = model.predict(transaction)
                result['transaction_id'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing transaction {i}: {e}")
                results.append({
                    "transaction_id": i,
                    "error": str(e)
                })
        
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        "model_type": "Rule-based Fraud Detection",
        "version": "1.0.0",
        "features": list(model.risk_factors.keys()),
        "risk_factors": model.risk_factors
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
