import { useRef, useState } from 'react'
import { useProgress } from '../context/ProgressContext'
import { Layout } from '../components/Layout'

export function SettingsPage() {
  const { exportJson, importJson, resetAll, progress, stats } = useProgress()
  const fileRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState<string | null>(null)

  return (
    <Layout>
      <div className="panel">
        <h1 style={{ marginTop: 0 }}>Settings</h1>
        <p className="muted">
          Progress is stored in this browser (localStorage). Unlocked through
          lesson order {progress.unlockedThrough}. Review deck: {stats.total}{' '}
          cards ({stats.dueNow} due now, {stats.dueToday} due today).
        </p>

        <div className="btn-row">
          <button
            type="button"
            className="btn"
            onClick={() => {
              const blob = new Blob([exportJson()], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = 'daf-kompakt-progress.json'
              a.click()
              URL.revokeObjectURL(url)
              setMessage('Progress exported.')
            }}
          >
            Export progress
          </button>
          <button
            type="button"
            className="btn secondary"
            onClick={() => fileRef.current?.click()}
          >
            Import progress
          </button>
          <button
            type="button"
            className="btn secondary"
            onClick={() => {
              if (confirm('Reset all progress?')) {
                resetAll()
                setMessage('Progress reset.')
              }
            }}
          >
            Reset
          </button>
        </div>

        <input
          ref={fileRef}
          type="file"
          accept="application/json"
          hidden
          onChange={async (e) => {
            const file = e.target.files?.[0]
            if (!file) return
            try {
              const text = await file.text()
              importJson(text)
              setMessage('Progress imported.')
            } catch {
              setMessage('Import failed.')
            }
          }}
        />

        {message && <p className="feedback ok">{message}</p>}

        <p className="muted" style={{ marginTop: '1.5rem' }}>
          Personal study app based on DaF kompakt A1–B1. Do not redistribute
          copyrighted book text.
        </p>
      </div>
    </Layout>
  )
}
