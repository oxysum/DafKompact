import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import type { Lesson, ListeningTrack } from '../types/lesson'
import { fetchLesson, fetchListeningTrack } from '../lib/content'
import { useSettings } from '../context/SettingsContext'
import { helperLabel, isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'

export function ListeningPage() {
  const { lessonId = '' } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const { helperLanguage } = useSettings()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [active, setActive] = useState<ListeningTrack | null>(null)
  const [showTranscript, setShowTranscript] = useState(true)
  const [showTranslation, setShowTranslation] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const tracks = lesson?.listening ?? []
  const selectedId = searchParams.get('track') ?? tracks[0]?.id ?? null

  useEffect(() => {
    let cancelled = false
    fetchLesson(lessonId)
      .then((l) => {
        if (!cancelled) setLesson(l)
      })
      .catch((e) => !cancelled && setError(String(e)))
    return () => {
      cancelled = true
    }
  }, [lessonId])

  useEffect(() => {
    if (!selectedId) {
      setActive(null)
      return
    }
    let cancelled = false
    fetchListeningTrack(selectedId)
      .then((t) => {
        if (!cancelled) setActive(t)
      })
      .catch((e) => !cancelled && setError(String(e)))
    return () => {
      cancelled = true
    }
  }, [selectedId])

  if (error) {
    return (
      <Layout>
        <p className="feedback no">{error}</p>
      </Layout>
    )
  }

  if (!lesson) {
    return (
      <Layout>
        <p className="muted">Loading…</p>
      </Layout>
    )
  }

  if (tracks.length === 0) {
    return (
      <Layout>
        <div className="panel">
          <h1 style={{ marginTop: 0 }}>Listening</h1>
          <p className="muted">No audio tracks for this lesson yet.</p>
          <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
            Back to lesson
          </Link>
        </div>
      </Layout>
    )
  }

  const translation = active
    ? pickGloss(active.textEn, active.textFa, helperLanguage)
    : ''
  const hasTranslation = Boolean(translation && translation !== active?.text)

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Listening · {lesson.titleDe}
        </p>
        <h1 style={{ marginTop: 0 }}>Hörverstehen</h1>
        <p className="muted">
          Kursbuch CD audio with German transcript
          {hasTranslation
            ? ` and ${helperLabel(helperLanguage)} translation`
            : ''}
          . Does not unlock the next lesson.
        </p>

        <div className="listening-layout">
          <ul className="listening-track-list">
            {tracks.map((t) => {
              const selected = t.id === selectedId
              return (
                <li key={t.id}>
                  <button
                    type="button"
                    className={`listening-track-btn ${selected ? 'active' : ''}`}
                    onClick={() => setSearchParams({ track: t.id })}
                  >
                    <span className="listening-track-meta">
                      CD {t.cd} · Track {t.track}
                    </span>
                    <span className="listening-track-preview">{t.preview}</span>
                  </button>
                </li>
              )
            })}
          </ul>

          <div className="listening-player">
            {active ? (
              <>
                <h2 style={{ marginTop: 0 }}>
                  CD {active.cd} · Track {active.track}
                </h2>
                <audio
                  key={active.id}
                  className="listening-audio"
                  controls
                  src={active.audioUrl}
                  preload="metadata"
                />
                <div className="btn-row">
                  <button
                    type="button"
                    className="btn secondary"
                    onClick={() => setShowTranscript((v) => !v)}
                  >
                    {showTranscript ? 'Hide German' : 'Show German'}
                  </button>
                  {hasTranslation && (
                    <button
                      type="button"
                      className="btn secondary"
                      onClick={() => setShowTranslation((v) => !v)}
                    >
                      {showTranslation
                        ? `Hide ${helperLabel(helperLanguage)}`
                        : `Show ${helperLabel(helperLanguage)}`}
                    </button>
                  )}
                </div>
                {showTranscript && (
                  <pre className="listening-transcript">{active.text}</pre>
                )}
                {showTranslation && hasTranslation && (
                  <pre
                    className={`listening-transcript listening-translation ${
                      isRtl(helperLanguage) ? 'gloss-rtl' : ''
                    }`}
                  >
                    {translation}
                  </pre>
                )}
                {!hasTranslation && showTranscript && (
                  <p className="muted" style={{ marginTop: '0.75rem' }}>
                    Translation not available for this track yet.
                  </p>
                )}
              </>
            ) : (
              <p className="muted">Select a track to play.</p>
            )}
          </div>
        </div>

        <div className="btn-row">
          <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
            Back to lesson
          </Link>
        </div>
      </div>
    </Layout>
  )
}
