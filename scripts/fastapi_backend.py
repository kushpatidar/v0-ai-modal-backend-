from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Fraud Detection API",
    description="Advanced fraud detection using machine learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TransactionData(BaseModel):
    amount: Optional[float] = Field(None, description="Transaction amount")
    merchant: Optional[str] = Field(None, description="Merchant name")
    location: Optional[str] = Field(None, description="Transaction location")
    time: Optional[str] = Field(None, description="Transaction time")
    card_type: Optional[str] = Field(None, description="Card type")

class PredictionRequest(BaseModel):
    data: str = Field(..., description="JSON string containing transaction data")

class BatchPredictionRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions")

class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Fraud prediction (fraud/legitimate)")
    confidence: float = Field(..., description="Prediction confidence score")
    risk_score: float = Field(..., description="Risk score (0-1)")
    features: Dict[str, Any] = Field(..., description="Extracted features")

class HealthResponse(BaseModel):
    status: str
    timestamp: str

class FraudDetectionModel:
    """Advanced fraud detection model"""
    
    def __init__(self):
        self.risk_factors = {
            'high_amount_threshold': 1000,
            'very_high_amount_threshold': 5000,
            'suspicious_merchants': ['unknown', 'cash_advance', 'gambling', 'crypto'],
            'unusual_times': ['late_night', 'early_morning'],
            'high_risk_locations': ['foreign', 'unknown', 'offshore'],
            'velocity_threshold': 5  # Max transactions per hour
        }
        
        # In production, load your trained ML model here
        # self.model = joblib.load('fraud_model.pkl')
    
    def extract_features(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive features from transaction data"""
        features = {}
        
        # Amount-based features
        amount = transaction_data.get('amount', 0)
        features['amount'] = amount
        features['high_amount'] = amount > self.risk_factors['high_amount_threshold']
        features['very_high_amount'] = amount > self.risk_factors['very_high_amount_threshold']
        features['amount_category'] = self._categorize_amount(amount)
        
        # Merchant-based features
        merchant = str(transaction_data.get('merchant', '')).lower()
        features['merchant'] = merchant
        features['suspicious_merchant'] = any(sus in merchant for sus in self.risk_factors['suspicious_merchants'])
        features['merchant_category'] = self._categorize_merchant(merchant)
        
        # Time-based features
        time = transaction_data.get('time', '')
        features['time'] = time
        features['unusual_time'] = self._is_unusual_time(time)
        features['time_category'] = self._categorize_time(time)
        
        # Location-based features
        location = str(transaction_data.get('location', '')).lower()
        features['location'] = location
        features['high_risk_location'] = any(risk in location for risk in self.risk_factors['high_risk_locations'])
        features['location_category'] = self._categorize_location(location)
        
        # Card type features
        card_type = transaction_data.get('card_type', 'unknown')
        features['card_type'] = card_type
        features['high_risk_card'] = card_type in ['prepaid', 'gift', 'unknown']
        
        return features
    
    def _categorize_amount(self, amount: float) -> str:
        """Categorize transaction amount"""
        if amount < 50:
            return 'micro'
        elif amount < 200:
            return 'small'
        elif amount < 1000:
            return 'medium'
        elif amount < 5000:
            return 'large'
        else:
            return 'very_large'
    
    def _categorize_merchant(self, merchant: str) -> str:
        """Categorize merchant type"""
        if any(word in merchant for word in ['grocery', 'supermarket', 'food']):
            return 'grocery'
        elif any(word in merchant for word in ['gas', 'fuel', 'station']):
            return 'gas_station'
        elif any(word in merchant for word in ['restaurant', 'cafe', 'dining']):
            return 'restaurant'
        elif any(word in merchant for word in ['online', 'web', 'internet']):
            return 'online'
        elif any(word in merchant for word in ['atm', 'cash']):
            return 'cash_service'
        else:
            return 'other'
    
    def _is_unusual_time(self, time_str: str) -> bool:
        """Check if transaction time is unusual"""
        try:
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
                return hour < 6 or hour > 23
        except:
            pass
        return False
    
    def _categorize_time(self, time_str: str) -> str:
        """Categorize transaction time"""
        try:
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
                if 6 <= hour < 12:
                    return 'morning'
                elif 12 <= hour < 18:
                    return 'afternoon'
                elif 18 <= hour < 23:
                    return 'evening'
                else:
                    return 'night'
        except:
            pass
        return 'unknown'
    
    def _categorize_location(self, location: str) -> str:
        """Categorize transaction location"""
        if any(word in location for word in ['online', 'internet', 'web']):
            return 'online'
        elif any(word in location for word in ['foreign', 'international', 'overseas']):
            return 'international'
        elif 'atm' in location:
            return 'atm'
        else:
            return 'domestic'
    
    def predict(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fraud prediction with advanced scoring"""
        features = self.extract_features(transaction_data)
        
        # Advanced risk scoring algorithm
        risk_score = 0.0
        risk_factors = []
        
        # Amount-based risk
        if features['very_high_amount']:
            risk_score += 0.4
            risk_factors.append('Very high amount')
        elif features['high_amount']:
            risk_score += 0.25
            risk_factors.append('High amount')
        
        # Merchant-based risk
        if features['suspicious_merchant']:
            risk_score += 0.35
            risk_factors.append('Suspicious merchant')
        
        # Time-based risk
        if features['unusual_time']:
            risk_score += 0.2
            risk_factors.append('Unusual time')
        
        # Location-based risk
        if features['high_risk_location']:
            risk_score += 0.3
            risk_factors.append('High-risk location')
        
        # Card type risk
        if features['high_risk_card']:
            risk_score += 0.15
            risk_factors.append('High-risk card type')
        
        # Combination risk factors
        if features['unusual_time'] and features['high_amount']:
            risk_score += 0.1  # Bonus risk for combination
        
        if features['suspicious_merchant'] and features['very_high_amount']:
            risk_score += 0.15  # High risk combination
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine prediction with dynamic threshold
        threshold = 0.5
        prediction = 'fraud' if risk_score > threshold else 'legitimate'
        
        # Calculate confidence
        if prediction == 'fraud':
            confidence = min(risk_score * 1.2, 1.0)  # Higher confidence for clear fraud
        else:
            confidence = min((1 - risk_score) * 1.1, 1.0)  # Higher confidence for clear legitimate
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'risk_score': risk_score,
            'features': features,
            'risk_factors': risk_factors,
            'threshold_used': threshold
        }

# Initialize model
model = FraudDetectionModel()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(request: PredictionRequest):
    """Main fraud prediction endpoint"""
    try:
        # Parse transaction data
        try:
            transaction_data = json.loads(request.data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format in data field")
        
        logger.info(f"Processing transaction: {transaction_data}")
        
        # Make prediction
        result = model.predict(transaction_data)
        
        logger.info(f"Prediction result: {result['prediction']} (confidence: {result['confidence']:.2f})")
        
        return PredictionResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/batch_predict")
async def batch_predict(request: BatchPredictionRequest):
    """Batch prediction endpoint"""
    try:
        results = []
        
        for i, transaction in enumerate(request.transactions):
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
        
        return {'results': results}
    
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/model/info")
async def get_model_info():
    """Get model information and statistics"""
    return {
        'model_type': 'Rule-based Fraud Detection',
        'version': '1.0.0',
        'features': [
            'Amount analysis',
            'Merchant categorization',
            'Time pattern analysis',
            'Location risk assessment',
            'Card type evaluation'
        ],
        'risk_factors': model.risk_factors,
        'last_updated': datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
