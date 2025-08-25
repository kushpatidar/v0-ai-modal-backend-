# AI Fraud Detection Backend

A Flask-based REST API for real-time fraud detection using machine learning techniques.

## Features

- Real-time fraud prediction
- Batch transaction processing
- Risk scoring and confidence levels
- RESTful API with JSON responses
- Production-ready with proper error handling
- CORS enabled for frontend integration

## API Endpoints

### Health Check
\`\`\`
GET /
\`\`\`
Returns service status and health information.

### Single Prediction
\`\`\`
POST /api/predict
Content-Type: application/json

{
  "data": "{\"amount\": 1500.00, \"merchant\": \"Online Store\", \"location\": \"New York\", \"time\": \"14:30\", \"card_type\": \"credit\"}"
}
\`\`\`

### Batch Prediction
\`\`\`
POST /api/batch-predict
Content-Type: application/json

{
  "transactions": [
    {"amount": 100, "merchant": "Store A"},
    {"amount": 2000, "merchant": "Store B"}
  ]
}
\`\`\`

### Model Information
\`\`\`
GET /api/model-info
\`\`\`
Returns model details and configuration.

## Deployment on Render

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure the service:**
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Python Version: 3.11.0

4. **Deploy and get your API URL**

## Local Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
\`\`\`

The API will be available at `http://localhost:5000`

## Environment Variables

- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Environment mode (production/development)

## Response Format

\`\`\`json
{
  "prediction": "fraud" | "legitimate",
  "confidence": 0.85,
  "risk_score": 0.72,
  "features": {
    "amount": 1500.00,
    "high_amount": true,
    "unusual_time": false,
    "suspicious_merchant": false,
    "foreign_location": false
  }
}
\`\`\`

## Risk Factors

The model evaluates transactions based on:
- Transaction amount (high amounts increase risk)
- Transaction time (unusual hours increase risk)
- Merchant type (suspicious merchants increase risk)
- Location (high-risk locations increase risk)
- Card type and usage patterns

## Production Considerations

- The current model uses rule-based logic
- For production, consider integrating with actual ML models
- Add authentication and rate limiting
- Implement proper logging and monitoring
- Add database integration for transaction history
