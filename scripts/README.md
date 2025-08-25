# AI Fraud Detection Backend

This repository contains both Flask and FastAPI implementations for the AI fraud detection backend.

## Features

- **Real-time fraud detection** with confidence scoring
- **Batch processing** for multiple transactions
- **Feature extraction** from transaction data
- **Risk factor analysis** with detailed explanations
- **RESTful API** with comprehensive documentation
- **CORS support** for frontend integration

## Quick Start

### Option 1: Flask Backend

\`\`\`bash
pip install flask flask-cors numpy python-dateutil
python scripts/flask_backend.py
\`\`\`

Server runs on: `http://localhost:5000`

### Option 2: FastAPI Backend (Recommended)

\`\`\`bash
pip install fastapi uvicorn pydantic python-multipart
python scripts/fastapi_backend.py
\`\`\`

Server runs on: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Health Check
- **GET** `/health` - Check server status

### Fraud Prediction
- **POST** `/predict` - Single transaction analysis
- **POST** `/batch_predict` - Multiple transaction analysis
- **GET** `/model/info` - Model information (FastAPI only)

### Example Request

\`\`\`json
{
  "data": "{\"amount\": 1500.00, \"merchant\": \"Online Store\", \"location\": \"New York\", \"time\": \"14:30\", \"card_type\": \"credit\"}"
}
\`\`\`

### Example Response

\`\`\`json
{
  "prediction": "legitimate",
  "confidence": 0.75,
  "risk_score": 0.25,
  "features": {
    "amount": 1500.0,
    "high_amount": true,
    "merchant": "online store",
    "suspicious_merchant": false,
    "unusual_time": false,
    "location": "new york",
    "high_risk_location": false
  }
}
\`\`\`

## Deployment

### Local Development
Both servers include CORS support for local development.

### Production Deployment
- Use environment variables for configuration
- Implement proper authentication
- Add rate limiting
- Use HTTPS
- Configure proper CORS origins
- Add monitoring and logging

## Model Enhancement

The current implementation uses rule-based detection. To enhance with ML:

1. Collect labeled training data
2. Train models using scikit-learn, TensorFlow, or PyTorch
3. Replace the `predict()` method with model inference
4. Add model versioning and A/B testing

## Integration

Update your frontend API calls to point to:
- Flask: `http://localhost:5000/predict`
- FastAPI: `http://localhost:8000/predict`
