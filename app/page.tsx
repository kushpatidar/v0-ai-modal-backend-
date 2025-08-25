"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Loader2, Brain, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface PredictionResult {
  prediction: string
  confidence: number
  risk_score: number
  features: Record<string, any>
}

export default function FraudDetectionDashboard() {
  const [inputData, setInputData] = useState("")
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handlePredict = async () => {
    if (!inputData.trim()) {
      setError("Please enter transaction data")
      return
    }

    setLoading(true)
    setError("")

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "https://your-render-app.onrender.com"

      let transactionData
      try {
        transactionData = JSON.parse(inputData)
      } catch (parseError) {
        throw new Error("Invalid JSON format")
      }

      const response = await fetch(`${backendUrl}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(transactionData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || "Prediction failed")
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("Failed to get prediction. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (riskScore: number) => {
    if (riskScore < 0.3) return "text-green-600"
    if (riskScore < 0.7) return "text-yellow-600"
    return "text-red-600"
  }

  const getRiskIcon = (riskScore: number) => {
    if (riskScore < 0.3) return <CheckCircle className="h-5 w-5 text-green-600" />
    if (riskScore < 0.7) return <AlertTriangle className="h-5 w-5 text-yellow-600" />
    return <XCircle className="h-5 w-5 text-red-600" />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2">
            <Brain className="h-8 w-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-gray-900">AI Fraud Detection</h1>
          </div>
          <p className="text-gray-600">Advanced machine learning for transaction analysis</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Transaction Analysis</CardTitle>
            <CardDescription>Enter transaction data (JSON format) to analyze for potential fraud</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder='{"amount": 1500.00, "merchant": "Online Store", "location": "New York", "time": "14:30", "card_type": "credit"}'
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              rows={4}
              className="font-mono text-sm"
            />

            {error && <div className="text-red-600 text-sm">{error}</div>}

            <Button onClick={handlePredict} disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-4 w-4" />
                  Analyze Transaction
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getRiskIcon(result.risk_score)}
                Analysis Results
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">
                    <Badge variant={result.prediction === "fraud" ? "destructive" : "default"}>
                      {result.prediction.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Prediction</div>
                </div>

                <div className="text-center">
                  <div className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</div>
                  <div className="text-sm text-gray-600 mt-1">Confidence</div>
                </div>

                <div className="text-center">
                  <div className={`text-2xl font-bold ${getRiskColor(result.risk_score)}`}>
                    {(result.risk_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Risk Score</div>
                </div>
              </div>

              {result.features && (
                <div>
                  <h4 className="font-semibold mb-2">Feature Analysis</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {Object.entries(result.features).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600">{key}:</span>
                        <span className="font-mono">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
