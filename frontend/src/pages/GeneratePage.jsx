import { useState } from "react"
import { generateSynthetic } from "../services/api"

const SYNTHESIZERS = [
  { id: "auto", label: "Auto", desc: "Let DataForge recommend based on your data" },
  { id: "gaussian_copula", label: "Gaussian Copula", desc: "Fast, great for small numerical datasets" },
  { id: "ctgan", label: "CTGAN", desc: "Handles mixed data types well" },
  { id: "tvae", label: "TVAE", desc: "Best for large, complex distributions" },
]

export default function GeneratePage({ fileId, profile, onSuccess }) {
  const [synthesizer, setSynthesizer] = useState(profile?.recommended_synthesizer || "auto")
  const [numRows, setNumRows] = useState(100)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleGenerate = async () => {
    if (!fileId) return
    setLoading(true)
    setError(null)
    try {
      const res = await generateSynthetic(fileId, synthesizer, numRows)
      setResult(res.data)
      setTimeout(() => onSuccess(res.data), 1200)
    } catch (e) {
      setError(e.response?.data?.detail || "Generation failed.")
    } finally {
      setLoading(false)
    }
  }

  if (!fileId) return (
    <div className="text-center py-20 text-gray-500">Please upload a dataset first.</div>
  )

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Generate Synthetic Data</h2>
      <p className="text-gray-400 text-sm mb-6">Choose a synthesizer and how many rows to generate. We've pre-selected the best option for your dataset.</p>

      {/* Synthesizer selection */}
      <div className="mb-6">
        <label className="text-sm text-gray-400 uppercase tracking-wide font-medium mb-3 block">Synthesizer</label>
        <div className="grid grid-cols-2 gap-3">
          {SYNTHESIZERS.map((s) => (
            <button
              key={s.id}
              onClick={() => setSynthesizer(s.id)}
              className={`text-left p-4 rounded-xl border transition-colors ${
                synthesizer === s.id
                  ? "border-indigo-500 bg-indigo-950/40"
                  : "border-gray-700 bg-gray-900 hover:border-gray-500"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div className={`w-3 h-3 rounded-full border-2 ${synthesizer === s.id ? "border-indigo-400 bg-indigo-400" : "border-gray-600"}`} />
                <span className="font-medium text-sm text-white">{s.label}</span>
                {profile?.recommended_synthesizer === s.id && (
                  <span className="text-xs bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded-full">Recommended</span>
                )}
              </div>
              <p className="text-xs text-gray-400 ml-5">{s.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Row count */}
      <div className="mb-8">
        <label className="text-sm text-gray-400 uppercase tracking-wide font-medium mb-3 block">
  Rows to Generate — <span className="text-white">{numRows}</span>
  <span className="ml-2 normal-case text-gray-100 font-normal bold">
    (new synthetic rows learned from your {profile?.rows?.toLocaleString()} real rows)
  </span>
</label>
        <input
          type="range"
          min={50} max={5000} step={50}
          value={numRows}
          onChange={(e) => setNumRows(Number(e.target.value))}
          className="w-full accent-indigo-500"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>50</span><span>5,000</span>
        </div>
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-colors"
      >
        {loading ? "Generating... this may take a moment" : "Generate Synthetic Data"}
      </button>

      {error && <p className="text-red-400 text-sm mt-4">{error}</p>}

      {result && (
        <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center gap-6">
          <div className="text-4xl">✅</div>
          <div>
            <p className="font-semibold text-white">Generation complete</p>
            <p className="text-gray-400 text-sm mt-1">
              {result.rows_generated} rows generated using <span className="text-indigo-400">{result.synthesizer_used.replace("_", " ")}</span>
            </p>
            <p className="text-gray-500 text-xs mt-1">Redirecting to Quality Report...</p>
          </div>
        </div>
      )}
    </div>
  )
}