import { useState } from "react"
import { downloadCSV, downloadReport } from "../services/api"

function DownloadCard({ icon, title, desc, buttonLabel, onClick, loading }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col gap-4">
      <div className="text-4xl">{icon}</div>
      <div>
        <h3 className="font-semibold text-white">{title}</h3>
        <p className="text-gray-400 text-sm mt-1">{desc}</p>
      </div>
      <button
        onClick={onClick}
        disabled={loading}
        className="mt-auto py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
      >
        {loading ? "Preparing..." : buttonLabel}
      </button>
    </div>
  )
}

function triggerDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

export default function ExportPage({ fileId }) {
  const [csvLoading, setCsvLoading] = useState(false)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [csvDone, setCsvDone] = useState(false)
  const [pdfDone, setPdfDone] = useState(false)
  const [error, setError] = useState(null)

  const handleCSV = async () => {
    setCsvLoading(true)
    setError(null)
    try {
      const res = await downloadCSV(fileId)
      triggerDownload(res.data, `synthetic_${fileId}.csv`)
      setCsvDone(true)
    } catch {
      setError("Failed to download CSV.")
    } finally {
      setCsvLoading(false)
    }
  }

  const handleReport = async () => {
    setPdfLoading(true)
    setError(null)
    try {
      const res = await downloadReport(fileId)
      triggerDownload(res.data, `dataforge_report_${fileId}.pdf`)
      setPdfDone(true)
    } catch {
      setError("Failed to generate PDF report.")
    } finally {
      setPdfLoading(false)
    }
  }

  if (!fileId) return (
    <div className="text-center py-20 text-gray-500">Please complete all steps first.</div>
  )

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Export</h2>
      <p className="text-gray-400 text-sm mb-8">Download your synthetic dataset and a full PDF summary report.</p>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <DownloadCard
          icon="📄"
          title="Synthetic Dataset"
          desc="Download the generated synthetic data as a CSV file ready for use in your ML pipeline."
          buttonLabel={csvDone ? "✓ Downloaded" : "Download CSV"}
          onClick={handleCSV}
          loading={csvLoading}
        />
        <DownloadCard
          icon="📊"
          title="PDF Summary Report"
          desc="A full report including dataset overview, synthesizer choice, quality metrics, privacy scores, and column distribution charts."
          buttonLabel={pdfDone ? "✓ Downloaded" : "Download PDF Report"}
          onClick={handleReport}
          loading={pdfLoading}
        />
      </div>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {(csvDone || pdfDone) && (
        <div className="bg-green-950/40 border border-green-800 rounded-xl p-5 text-center">
          <p className="text-green-400 font-medium">🎉 Done! Your synthetic data is ready.</p>
          <p className="text-gray-400 text-sm mt-1">You can re-run with different synthesizers or row counts from the Generate tab.</p>
        </div>
      )}
    </div>
  )
}