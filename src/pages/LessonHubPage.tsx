import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type { Lesson, LessonIndexEntry, StepId } from '../types/lesson'
import { fetchIndex, fetchLesson } from '../lib/content'
import {
  getLessonProgress,
  isLessonUnlocked,
  lessonPercent,
} from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'

const STEPS: { id: StepId; label: string; title: string }[] = [
  { id: 'goals', label: 'Step 1', title: 'Goals' },
  { id: 'vocab', label: 'Step 2', title: 'Vocabulary' },
  { id: 'grammar', label: 'Step 3', title: 'Grammar' },
  { id: 'quiz', label: 'Step 4', title: 'Quiz' },
]

export function LessonHubPage() {
  const { lessonId = '' } = useParams()
  const navigate = useNavigate()
  const { progress, ready } = useProgress()
  const { helperLanguage, unlockAll } = useSettings()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [meta, setMeta] = useState<LessonIndexEntry | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([fetchLesson(lessonId), fetchIndex()])
      .then(([l, index]) => {
        if (cancelled) return
        setLesson(l)
        setMeta(index.lessons.find((x) => x.id === lessonId) ?? null)
      })
      .catch((e) => !cancelled && setError(String(e)))
    return () => {
      cancelled = true
    }
  }, [lessonId])

  if (error) {
    return (
      <Layout>
        <p className="feedback no">{error}</p>
      </Layout>
    )
  }

  if (!lesson || !meta || !ready) {
    return (
      <Layout>
        <p className="muted">Loading lesson…</p>
      </Layout>
    )
  }

  if (!unlockAll && !isLessonUnlocked(progress, meta.order)) {
    return (
      <Layout>
        <div className="panel">
          <h1>Lesson locked</h1>
          <p className="muted">
            Finish the previous lesson quiz (≥70%) to unlock this one. Or turn on
            Free access in Settings.
          </p>
          <div className="btn-row">
            <Link className="btn secondary" to="/">
              Back to lessons
            </Link>
            <Link className="btn" to="/settings">
              Settings
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  const lp = getLessonProgress(progress, lesson.id)
  const done: Record<StepId, boolean> = {
    goals: lp.goalsDone,
    vocab: lp.vocabDone,
    grammar: lp.grammarDone,
    quiz: lp.quizDone,
  }

  function canOpen(step: StepId): boolean {
    if (unlockAll) return true
    if (step === 'goals') return true
    if (step === 'vocab') return done.goals
    if (step === 'grammar') return done.vocab
    if (step === 'quiz') return done.grammar
    return false
  }

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          {lesson.level} · Lektion {lesson.number} · {lessonPercent(lp)}%
        </p>
        <h1 style={{ marginTop: 0 }}>{lesson.titleDe}</h1>
        <p className={`muted ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}>
          {pickGloss(lesson.titleEn, lesson.titleFa, helperLanguage)}
        </p>

        {lesson.status === 'stub' && (
          <p className="feedback" style={{ color: 'var(--accent-soft)' }}>
            This lesson is a stub: titles and goals are ready; vocab, grammar,
            and quiz will be filled next. You can still mark goals done to
            explore the path.
          </p>
        )}

        <div className="path-steps">
          {STEPS.map((step) => {
            const open = canOpen(step.id)
            return (
              <button
                key={step.id}
                type="button"
                className={`path-step ${done[step.id] ? 'done' : ''}`}
                disabled={!open}
                onClick={() => navigate(`/lesson/${lesson.id}/${step.id}`)}
              >
                <span className="label">{step.label}</span>
                <strong>{step.title}</strong>
                <span className="muted" style={{ fontSize: '0.85rem' }}>
                  {done[step.id] ? 'Done' : open ? 'Start' : 'Locked'}
                </span>
              </button>
            )
          })}
        </div>

        {(lesson.listening?.length ?? 0) > 0 && (
          <div className="listening-hub">
            <h2>Listening</h2>
            <p className="muted">
              {lesson.listening!.length} Kursbuch track
              {lesson.listening!.length === 1 ? '' : 's'} with transcript — optional,
              does not gate unlock.
            </p>
            <button
              type="button"
              className="btn"
              onClick={() => navigate(`/lesson/${lesson.id}/listening`)}
            >
              Open listening
            </button>
          </div>
        )}

        <div className="btn-row">
          <Link className="btn secondary" to="/">
            All lessons
          </Link>
        </div>
      </div>
    </Layout>
  )
}
