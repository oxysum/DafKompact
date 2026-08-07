import { useRef, useState } from 'react'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { Layout } from '../components/Layout'
import type { HelperLanguage } from '../lib/settings'

export function SettingsPage() {
  const { exportJson, importJson, resetAll, progress, stats } = useProgress()
  const { helperLanguage, setHelperLanguage, unlockAll, setUnlockAll } =
    useSettings()
  const fileRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState<string | null>(null)

  function chooseLang(lang: HelperLanguage) {
    setHelperLanguage(lang)
    setMessage(
      lang === 'fa'
        ? 'Helper language set to فارسی. Missing Farsi glosses fall back to English.'
        : 'Helper language set to English.',
    )
  }

  function chooseAccess(allOpen: boolean) {
    setUnlockAll(allOpen)
    setMessage(
      allOpen
        ? 'Free access on: all lessons and steps are open. Progress is still tracked.'
        : 'Progress mode on: finish each quiz (≥70%) to unlock the next lesson.',
    )
  }

  return (
    <Layout>
      <div className="panel">
        <h1 style={{ marginTop: 0 }}>Settings</h1>
        <p className="muted">
          Progress is stored in this browser (localStorage).
          {unlockAll
            ? ' Free access is on — all lessons are open.'
            : ` Unlocked through lesson order ${progress.unlockedThrough}.`}{' '}
          Review deck: {stats.total} cards ({stats.dueNow} due now,{' '}
          {stats.dueToday} due today).
        </p>

        <h2>Helper language</h2>
        <p className="muted">
          German stays the learning language. Choose English or Farsi for
          meanings, titles, and explanations. Default is English.
        </p>
        <div className="lang-toggle" role="radiogroup" aria-label="Helper language">
          <button
            type="button"
            role="radio"
            aria-checked={helperLanguage === 'en'}
            className={`lang-option ${helperLanguage === 'en' ? 'active' : ''}`}
            onClick={() => chooseLang('en')}
          >
            English
          </button>
          <button
            type="button"
            role="radio"
            aria-checked={helperLanguage === 'fa'}
            className={`lang-option ${helperLanguage === 'fa' ? 'active' : ''}`}
            onClick={() => chooseLang('fa')}
          >
            فارسی
          </button>
        </div>

        <h2>Lesson access</h2>
        <p className="muted">
          Choose locked progress (quiz unlocks the next lesson) or open access to
          every lesson and step.
        </p>
        <div className="lang-toggle" role="radiogroup" aria-label="Lesson access">
          <button
            type="button"
            role="radio"
            aria-checked={!unlockAll}
            className={`lang-option ${!unlockAll ? 'active' : ''}`}
            onClick={() => chooseAccess(false)}
          >
            Progress mode
          </button>
          <button
            type="button"
            role="radio"
            aria-checked={unlockAll}
            className={`lang-option ${unlockAll ? 'active' : ''}`}
            onClick={() => chooseAccess(true)}
          >
            Free access (all open)
          </button>
        </div>

        <h2>Progress data</h2>
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
