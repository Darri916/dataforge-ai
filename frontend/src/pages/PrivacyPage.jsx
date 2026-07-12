import { useEffect, useState } from "react"
import { getPrivacy } from "../services/api"

function RiskMeter({ label, value, invert = false, desc }) {
  // invert=true means higher value = safer (e.g. NN distance)
  const display = invert ? 1 - value : value
  const color = display < 0.3 ? "bg-green-500" : display < 0.6 ? "bg-yellow-500" : "bg-red-500"
  const textColor = display < 0.3 ? "text-green-400" : display < 0.6 ? "text-yellow-400" : "text-red-400"
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex justify-between items-start mb-2">
        <div>
          <p className="font-medium text-white text-sm">{label}</p>
          <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
        </div>
        <span className={`text-xl font-bold ${textColor}`}>{value.toFixed(3)}</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full mt-3">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${display * 100}%` }} />
      </div>
      <p className="text-xs text-gray-600 mt-1">{invert ? "higher = safer" : "lower = safer"}</p>
    </div>
  )
}

export default function PrivacyPage({ fileId, privacy, onLoad, onNext }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!fileId || privacy) return
    setLoading(true)
    getPrivacy(fileId)
      .then(res => onLoad(res.data))
      .catch(e => setError(e.response?.data?.detail || "Failed to load privacy metrics."))
      .finally(() => setLoading(false))
  }, [fileId, onLoad])

  if (!fileId) return <div className="text-center py-20 text-gray-500">Please upload and generate data first.</div>
  if (loading) return <div className="text-center py-20 text-indigo-400 animate-pulse">Evaluating privacy risks...</div>
  if (error) return <div className="text-center py-20 text-red-400">{error}</div>
  if (!privacy) return null

  const privacyColor = privacy.overall_privacy_score >= 75 ? "text-green-400" : privacy.overall_privacy_score >= 50 ? "text-yellow-400" : "text-red-400"

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Privacy Report</h2>
      <p className="text-gray-400 text-sm mb-6">How well does the synthetic data protect the privacy of individuals in the original dataset?</p>

      {/* Overall score */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center mb-8">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Overall Privacy Score</p>
        <p className={`text-6xl font-bold ${privacyColor}`}>
          {privacy.overall_privacy_score}<span className="text-2xl text-gray-500">/100</span>
        </p>
        <p className="text-gray-500 text-sm mt-2">
          {privacy.overall_privacy_score >= 75
            ? "✓ Low re-identification risk — synthetic data is safe to share."
            : privacy.overall_privacy_score >= 50
            ? "⚠ Moderate risk — review metrics below before sharing."
            : "✗ High risk — synthetic data may expose real records."}
        </p>
      </div>

      {/* Risk breakdown */}
      <h3 className="text-sm text-gray-400 uppercase tracking-wide font-medium mb-3">Risk Breakdown</h3>
      <div className="grid grid-cols-2 gap-4 mb-8">
        <RiskMeter
          label="Duplicate Rate"
          value={privacy.duplicate_rate}
          desc="Proportion of synthetic rows that are exact copies of real rows"
        />
        <RiskMeter
          label="Nearest Neighbor Distance"
          value={privacy.nearest_neighbor_distance}
          invert={true}
          desc="How far synthetic rows are from real ones — higher means more privacy"
        />
        <RiskMeter
          label="Attribute Disclosure Risk"
          value={privacy.attribute_disclosure_risk}
          desc="Risk that categorical attribute distributions reveal real values"
        />
        <RiskMeter
          label="Re-identification Score"
          value={privacy.reidentification_score}
          desc="Combined risk that a synthetic record can be linked to a real person"
        />
      </div>

      <button
        onClick={onNext}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl transition-colors"
      >
        Continue to Export →
      </button>
    </div>
  )
}