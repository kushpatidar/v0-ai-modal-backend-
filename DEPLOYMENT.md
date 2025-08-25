# AI Fraud Detection Backend - Render Deployment Guide

## Quick Deploy to Render

1. **Create GitHub Repository**
   - Push this code to a new GitHub repository
   - Make sure all files are committed

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `ai-fraud-detection-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Instance Type**: Free tier is sufficient for testing

3. **Get Your API URL**
   - After deployment, Render will provide a URL like: `https://your-app-name.onrender.com`
   - Copy this URL for your frontend configuration

4. **Configure Frontend**
   - In your frontend project, add environment variable:
   - `NEXT_PUBLIC_BACKEND_URL=https://your-app-name.onrender.com`

## API Endpoints

- `GET /` - Health check
- `POST /api/predict` - Single fraud prediction
- `POST /api/batch-predict` - Batch predictions
- `GET /api/model-info` - Model information

## Example Usage

\`\`\`bash
curl -X POST https://your-app-name.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"amount": 1500, "merchant": "Online Store", "location": "New York", "time": "14:30", "card_type": "credit"}'
\`\`\`

## Environment Variables (Optional)

- `PORT` - Server port (automatically set by Render)

Your backend is now ready for production deployment!
