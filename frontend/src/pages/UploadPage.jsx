import { useState, useRef } from "react"
import { uploadFile } from "../services/api"

function HealthBar({ label, value }) {
  const pct = Math.round(value)
  const color = pct >= 20 ? "bg-indigo-500" : "bg-red-500"
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{label}</span><span>{pct}/25</span>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${(pct / 25) * 100}%` }} />
      </div>
    </div>
  )
}

export default function UploadPage({ onSuccess }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const inputRef = useRef()

  const handleFile = async (file) => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const res = await uploadFile(file)
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed.")
    } finally {
      setLoading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Upload Dataset</h2>
      <p className="text-gray-400 text-sm mb-6">Upload a CSV file to profile your data and get a health score before generating synthetic data.</p>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
          dragging ? "border-indigo-500 bg-indigo-950/30" : "border-gray-700 hover:border-gray-500"
        }`}
      >
        <div className="text-4xl mb-3">📂</div>
        <p className="text-gray-300 font-medium">Drag & drop a CSV file here</p>
        <p className="text-gray-500 text-sm mt-1">or click to browse</p>
        <input ref={inputRef} type="file" accept=".csv" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
      </div>

      {loading && <p className="text-indigo-400 text-sm mt-4 animate-pulse">Uploading and profiling dataset...</p>}
      {error && <p className="text-red-400 text-sm mt-4">{error}</p>}

      {/* Results */}
      {result && (
        <div className="mt-6 grid grid-cols-2 gap-6">
          {/* Dataset info */}
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h3 className="font-medium mb-3 text-sm text-gray-300 uppercase tracking-wide">Dataset Info</h3>
            <p className="text-sm text-gray-400">File: <span className="text-white">{result.filename}</span></p>
            <p className="text-sm text-gray-400 mt-1">Rows: <span className="text-white">{result.rows}</span></p>
            <p className="text-sm text-gray-400 mt-1">Columns: <span className="text-white">{result.columns}</span></p>
            <div className="mt-3">
              {Object.entries(result.column_types).map(([col, type]) => (
                <span key={col} className="inline-block text-xs bg-gray-800 text-gray-300 rounded px-2 py-0.5 mr-1 mb-1">
                  {col} <span className="text-gray-500">({type})</span>
                </span>
              ))}
            </div>
          </div>

          {/* Health score */}
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h3 className="font-medium mb-1 text-sm text-gray-300 uppercase tracking-wide">Dataset Health Score</h3>
            <div className="text-5xl font-bold text-indigo-400 mb-3">{result.health_score}<span className="text-xl text-gray-500">/100</span></div>
            <HealthBar label="Missing Values" value={result.health_breakdown.missing_values} />
            <HealthBar label="Duplicates" value={result.health_breakdown.duplicates} />
            <HealthBar label="Outliers" value={result.health_breakdown.outliers} />
            <HealthBar label="Class Balance" value={result.health_breakdown.imbalance} />
          </div>

          {/* Recommendation */}
          <div className="col-span-2 bg-indigo-950/40 border border-indigo-800 rounded-xl p-5">
            <h3 className="font-medium mb-1 text-indigo-300 text-sm uppercase tracking-wide">Recommended Synthesizer</h3>
            <p className="text-white font-semibold capitalize">{result.recommended_synthesizer.replace("_", " ")}</p>
            <p className="text-gray-400 text-sm mt-1">{result.recommendation_reason}</p>
          </div>

          <div className="col-span-2">
            <button
              onClick={() => onSuccess(result)}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-colors"
            >
              Continue to Generate →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}