import { useState } from "react"
import UploadPage from "./pages/UploadPage"
import GeneratePage from "./pages/GeneratePage"
import QualityPage from "./pages/QualityPage"
import PrivacyPage from "./pages/PrivacyPage"
import ExportPage from "./pages/ExportPage"

const TABS = ["Upload", "Generate", "Quality", "Privacy", "Export"]

export default function App() {
  const [activeTab, setActiveTab] = useState(0)
  const [fileId, setFileId] = useState(null)
  const [profile, setProfile] = useState(null)
  const [syntheticFileId, setSyntheticFileId] = useState(null)
  const [quality, setQuality] = useState(null)
  const [privacy, setPrivacy] = useState(null)

  const goTo = (index) => setActiveTab(index)

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 px-8 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">D</div>
        <span className="text-lg font-semibold tracking-tight">DataForge AI</span>
        <span className="ml-2 text-xs text-gray-500 font-medium uppercase tracking-widest">Synthetic Data Generator</span>
      </header>

      {/* Tabs */}
      <nav className="border-b border-gray-800 px-8 flex gap-1">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => goTo(i)}
            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === i
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
          >
            {i + 1}. {tab}
          </button>
        ))}
      </nav>

      {/* Pages */}
      <main className="px-8 py-8 max-w-5xl mx-auto">
        {activeTab === 0 && (
          <UploadPage
            onSuccess={(data) => { setFileId(data.file_id); setProfile(data); goTo(1) }}
          />
        )}
        {activeTab === 1 && (
          <GeneratePage
            fileId={fileId}
            profile={profile}
            onSuccess={(data) => { setSyntheticFileId(data.synthetic_file_id); goTo(2) }}
          />
        )}
        {activeTab === 2 && (
          <QualityPage
            fileId={fileId}
            quality={quality}
            onLoad={setQuality}
            onNext={() => goTo(3)}
          />
        )}
        {activeTab === 3 && (
          <PrivacyPage
            fileId={fileId}
            privacy={privacy}
            onLoad={setPrivacy}
            onNext={() => goTo(4)}
          />
        )}
        {activeTab === 4 && (
          <ExportPage fileId={fileId} />
        )}
      </main>
    </div>
  )
}