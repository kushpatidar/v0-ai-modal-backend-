"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Loader2, Brain, AlertTriangle, CheckCircle, XCircle, Upload, FileText, Download } from "lucide-react"

interface PredictionResult {
  prediction: string
  confidence: number
  risk_score: number
  features: Record<string, any>
}

interface FileUploadResult {
  results: (PredictionResult & { transaction_id: number; original_data: any })[]
  summary: {
    total_transactions: number
    fraud_detected: number
    legitimate_transactions: number
    fraud_percentage: number
    filename: string
  }
}

export default function FraudDetectionDashboard() {
  const [inputData, setInputData] = useState("")
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [fileResult, setFileResult] = useState<FileUploadResult | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [fileLoading, setFileLoading] = useState(false)
  const [error, setError] = useState("")
  const [activeTab, setActiveTab] = useState<"single" | "batch">("single")

  const getBackendUrl = () => {
    const envUrl = process.env.NEXT_PUBLIC_BACKEND_URL
    if (envUrl && envUrl !== "https://your-render-app.onrender.com") {
      return envUrl
    }
    // Fallback to localhost for development
    return "http://localhost:5000"
  }

  const handlePredict = async () => {
    if (!inputData.trim()) {
      setError("Please enter transaction data")
      return
    }

    setLoading(true)
    setError("")

    try {
      const backendUrl = getBackendUrl()

      let transactionData
      try {
        transactionData = JSON.parse(inputData)
      } catch (parseError) {
        throw new Error("Invalid JSON format")
      }

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout

      const response = await fetch(`${backendUrl}/api/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(transactionData),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Server error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError("Request timeout. Please check your backend connection and try again.")
        } else if (err.message.includes("fetch")) {
          setError(`Connection failed. Please ensure your backend is running at ${getBackendUrl()}`)
        } else {
          setError(err.message)
        }
      } else {
        setError("Failed to get prediction. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file")
      return
    }

    setFileLoading(true)
    setError("")

    try {
      const backendUrl = getBackendUrl()

      const formData = new FormData()
      formData.append("file", selectedFile)

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 second timeout for file uploads

      const response = await fetch(`${backendUrl}/api/upload-file`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Upload failed: ${response.status}`)
      }

      const data = await response.json()
      setFileResult(data)
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError("File upload timeout. Please try with a smaller file or check your connection.")
        } else if (err.message.includes("fetch")) {
          setError(`Upload failed. Please ensure your backend is running at ${getBackendUrl()}`)
        } else {
          setError(err.message)
        }
      } else {
        setError("Failed to process file. Please try again.")
      }
    } finally {
      setFileLoading(false)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setFileResult(null)
      setError("")
    }
  }

  const exportResults = () => {
    if (!fileResult) return

    const csvContent = [
      ["Transaction ID", "Prediction", "Confidence", "Risk Score", "Amount", "Merchant", "Location"],
      ...fileResult.results.map((result) => [
        result.transaction_id,
        result.prediction,
        (result.confidence * 100).toFixed(1) + "%",
        (result.risk_score * 100).toFixed(1) + "%",
        result.original_data?.amount || "N/A",
        result.original_data?.merchant || "N/A",
        result.original_data?.location || "N/A",
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n")

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `fraud_analysis_${fileResult.summary.filename}_results.csv`
    a.click()
    window.URL.revokeObjectURL(url)
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
          <p className="text-xs text-gray-500">Backend: {getBackendUrl()}</p>
        </div>

        <div className="flex justify-center space-x-4">
          <Button variant={activeTab === "single" ? "default" : "outline"} onClick={() => setActiveTab("single")}>
            Single Transaction
          </Button>
          <Button variant={activeTab === "batch" ? "default" : "outline"} onClick={() => setActiveTab("batch")}>
            Batch Upload
          </Button>
        </div>

        {activeTab === "single" && (
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
        )}

        {activeTab === "batch" && (
          <Card>
            <CardHeader>
              <CardTitle>Batch File Upload</CardTitle>
              <CardDescription>Upload CSV or JSON file with multiple transactions for batch analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Upload CSV or JSON file (max 16MB)</p>
                  <p className="text-xs text-gray-500">CSV format: amount, merchant, location, time, card_type</p>
                  <input
                    type="file"
                    accept=".csv,.json,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button variant="outline" className="cursor-pointer bg-transparent" asChild>
                      <span>
                        <Upload className="mr-2 h-4 w-4" />
                        Choose File
                      </span>
                    </Button>
                  </label>
                </div>
              </div>

              {selectedFile && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">{selectedFile.name}</span>
                  <span className="text-xs text-gray-500">{(selectedFile.size / 1024).toFixed(1)} KB</span>
                </div>
              )}

              {error && <div className="text-red-600 text-sm">{error}</div>}

              <Button onClick={handleFileUpload} disabled={fileLoading || !selectedFile} className="w-full">
                {fileLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing File...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Analyze File
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        )}

        {result && activeTab === "single" && (
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

        {fileResult && activeTab === "batch" && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Batch Analysis Summary</span>
                  <Button onClick={exportResults} variant="outline" size="sm">
                    <Download className="mr-2 h-4 w-4" />
                    Export CSV
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{fileResult.summary.total_transactions}</div>
                    <div className="text-sm text-gray-600">Total Transactions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{fileResult.summary.fraud_detected}</div>
                    <div className="text-sm text-gray-600">Fraud Detected</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {fileResult.summary.legitimate_transactions}
                    </div>
                    <div className="text-sm text-gray-600">Legitimate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{fileResult.summary.fraud_percentage}%</div>
                    <div className="text-sm text-gray-600">Fraud Rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Transaction Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {fileResult.results.map((transaction) => (
                    <div
                      key={transaction.transaction_id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {getRiskIcon(transaction.risk_score)}
                        <div>
                          <div className="font-medium">Transaction #{transaction.transaction_id}</div>
                          <div className="text-sm text-gray-600">
                            ${transaction.original_data?.amount || "N/A"} -{" "}
                            {transaction.original_data?.merchant || "Unknown"}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge variant={transaction.prediction === "fraud" ? "destructive" : "default"}>
                          {transaction.prediction.toUpperCase()}
                        </Badge>
                        <div className="text-sm text-gray-600 mt-1">
                          {(transaction.confidence * 100).toFixed(1)}% confidence
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
