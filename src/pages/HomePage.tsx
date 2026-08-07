import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import type { ContentIndex, Level } from '../types/lesson'
import { fetchIndex } from '../lib/content'
import {
  getLessonProgress,
  isLessonUnlocked,
  lessonPercent,
} from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'

export function HomePage() {
  const [index, setIndex] = useState<ContentIndex | null>(null)
  const [level, setLevel] = useState<Level | 'ALL'>('A1')
  const [error, setError] = useState<string | null>(null)
  const { progress, ready, stats } = useProgress()
  const { helperLanguage, unlockAll } = useSettings()

  useEffect(() => {
    fetchIndex()
      .then(setIndex)
      .catch((e) => setError(String(e)))
  }, [])

  const lessons = useMemo(() => {
    if (!index) return []
    return index.lessons.filter((l) => level === 'ALL' || l.level === level)
  }, [index, level])

  if (error) {
    return (
      <Layout>
        <p className="feedback no">{error}</p>
      </Layout>
    )
  }

  if (!index || !ready) {
    return (
      <Layout>
        <p className="muted">Loading lessons…</p>
      </Layout>
    )
  }

  return (
    <Layout>
      <section className="hero-block">
        <h1>Learn German with DaF kompakt</h1>
        <p>
          Full lesson path for A1–B1: goals → vocabulary → grammar drills →
          quiz. German ↔ English, personal study companion.
        </p>
      </section>

      {stats.dueToday > 0 && (
        <Link to="/review" className="due-banner">
          <div>
            <strong>
              {stats.dueNow > 0
                ? `${stats.dueNow} card${stats.dueNow === 1 ? '' : 's'} due now`
                : 'Review ready'}
            </strong>
            <span className="muted">
              {' '}
              · {stats.dueToday} due today
              {stats.total > 0 ? ` · ${stats.total} in deck` : ''}
            </span>
          </div>
          <span className="due-cta">Practice →</span>
        </Link>
      )}

      <div className="tabs">
        {(['A1', 'A2', 'B1', 'ALL'] as const).map((t) => (
          <button
            key={t}
            type="button"
            className={`tab ${level === t ? 'active' : ''}`}
            onClick={() => setLevel(t)}
          >
            {t === 'ALL' ? 'All' : t}
          </button>
        ))}
      </div>

      <div className="lesson-list">
        {lessons.map((lesson) => {
          const unlocked =
            unlockAll || isLessonUnlocked(progress, lesson.order)
          const lp = getLessonProgress(progress, lesson.id)
          const pct = lessonPercent(lp)
          const inner = (
            <>
              <div className="lesson-num">{lesson.number}</div>
              <div>
                <h2>{lesson.titleDe}</h2>
                <div
                  className={`sub ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}
                >
                  {pickGloss(lesson.titleEn, lesson.titleFa, helperLanguage)}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div
                  className={`badge ${lesson.status === 'complete' ? 'complete' : 'stub'}`}
                >
                  {lesson.status === 'complete' ? 'Full' : 'Stub'}
                </div>
                <div className="progress-pill" style={{ marginTop: 6 }}>
                  {unlocked ? `${pct}%` : 'Locked'}
                </div>
              </div>
            </>
          )

          if (!unlocked) {
            return (
              <div key={lesson.id} className="lesson-card locked">
                {inner}
              </div>
            )
          }

          return (
            <Link
              key={lesson.id}
              to={`/lesson/${lesson.id}`}
              className="lesson-card"
            >
              {inner}
            </Link>
          )
        })}
      </div>
    </Layout>
  )
}
