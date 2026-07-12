import { useEffect, useState } from "react"
import { getQuality } from "../services/api"
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts"

function ScoreCard({ label, value, suffix = "" }) {
  const color = value >= 75 ? "text-green-400" : value >= 50 ? "text-yellow-400" : "text-red-400"
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-4xl font-bold ${color}`}>{value}<span className="text-lg text-gray-500">{suffix}</span></p>
    </div>
  )
}

function ColumnCard({ metric }) {
  const isNum = metric.type === "numerical"
  const chartData = isNum ? [
    { name: "Mean", real: metric.real_mean, synthetic: metric.synthetic_mean },
    { name: "Std Dev", real: metric.real_std, synthetic: metric.synthetic_std },
  ] : [
    { name: "Similarity", real: metric.categorical_similarity * 100, synthetic: null }
  ]

  const jsdColor = metric.jsd < 0.1 ? "text-green-400" : metric.jsd < 0.3 ? "text-yellow-400" : "text-red-400"
  const ksColor = metric.ks_p_value > 0.05 ? "text-green-400" : "text-red-400"

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-medium text-white">{metric.column}</h4>
        <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">{metric.type}</span>
      </div>

      {isNum ? (
        <>
          <div className="grid grid-cols-3 gap-3 mb-4 text-center">
            <div>
              <p className="text-xs text-gray-500 mb-0.5">JSD</p>
              <p className={`text-lg font-semibold ${jsdColor}`}>{metric.jsd?.toFixed(3)}</p>
              <p className="text-xs text-gray-600">lower = better</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-0.5">KS Stat</p>
              <p className="text-lg font-semibold text-white">{metric.ks_statistic?.toFixed(3)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-0.5">p-value</p>
              <p className={`text-lg font-semibold ${ksColor}`}>{metric.ks_p_value?.toFixed(3)}</p>
              <p className="text-xs text-gray-600">{metric.ks_p_value > 0.05 ? "✓ same dist." : "✗ differs"}</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={chartData} barSize={24}>
              <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 11 }} />
              <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="real" name="Real" fill="#6366f1" radius={[4,4,0,0]} />
              <Bar dataKey="synthetic" name="Synthetic" fill="#f59e0b" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </>
      ) : (
        <div className="text-center py-4">
          <p className="text-xs text-gray-500 mb-1">Categorical Similarity</p>
          <p className="text-3xl font-bold text-indigo-400">{(metric.categorical_similarity * 100).toFixed(1)}%</p>
          <div className="mt-3 h-2 bg-gray-800 rounded-full">
            <div className="h-2 bg-indigo-500 rounded-full" style={{ width: `${metric.categorical_similarity * 100}%` }} />
          </div>
        </div>
      )}
    </div>
  )
}

export default function QualityPage({ fileId, quality, onLoad, onNext }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!fileId || quality) return
    setLoading(true)
    getQuality(fileId)
      .then(res => onLoad(res.data))
      .catch(e => setError(e.response?.data?.detail || "Failed to load quality metrics."))
      .finally(() => setLoading(false))
  }, [fileId])

  if (!fileId) return <div className="text-center py-20 text-gray-500">Please upload and generate data first.</div>
  if (loading) return <div className="text-center py-20 text-indigo-400 animate-pulse">Loading quality metrics...</div>
  if (error) return <div className="text-center py-20 text-red-400">{error}</div>
  if (!quality) return null

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Quality Report</h2>
      <p className="text-gray-400 text-sm mb-6">How closely does the synthetic data match the real data statistically?</p>

      {/* Score cards */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <ScoreCard label="Overall Quality Score" value={quality.overall_score} suffix="/100" />
        <ScoreCard label="Correlation Similarity" value={(quality.correlation_similarity * 100).toFixed(1)} suffix="%" />
      </div>

      {/* Per-column breakdown */}
      <h3 className="text-sm text-gray-400 uppercase tracking-wide font-medium mb-3">Column Breakdown</h3>
      <div className="grid grid-cols-2 gap-4 mb-8">
        {quality.column_metrics.map(m => <ColumnCard key={m.column} metric={m} />)}
      </div>

      <button
        onClick={onNext}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-colors"
      >
        Continue to Privacy Report →
      </button>
    </div>
  )
}