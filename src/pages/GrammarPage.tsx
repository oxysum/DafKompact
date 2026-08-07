import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type { DrillItem, Lesson } from '../types/lesson'
import { fetchLesson } from '../lib/content'
import { answersEqual } from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'

export function GrammarPage() {
  const { lessonId = '' } = useParams()
  const navigate = useNavigate()
  const { mark } = useProgress()
  const { helperLanguage } = useSettings()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [phase, setPhase] = useState<'learn' | 'drill'>('learn')
  const [drillIndex, setDrillIndex] = useState(0)
  const [input, setInput] = useState('')
  const [picked, setPicked] = useState<string | null>(null)
  const [reorder, setReorder] = useState<string[]>([])
  const [pool, setPool] = useState<string[]>([])
  const [feedback, setFeedback] = useState<string | null>(null)

  useEffect(() => {
    fetchLesson(lessonId).then(setLesson)
  }, [lessonId])

  const drills = lesson?.drills ?? []
  const drill: DrillItem | undefined = drills[drillIndex]

  useEffect(() => {
    if (!drill || drill.type !== 'reorder') return
    const words = drill.content.split('|').map((w) => w.trim()).filter(Boolean)
    setPool([...words].sort(() => Math.random() - 0.5))
    setReorder([])
    setFeedback(null)
    setInput('')
    setPicked(null)
  }, [drill])

  const progressLabel = useMemo(() => {
    if (!drills.length) return ''
    return `Drill ${drillIndex + 1}/${drills.length}`
  }, [drillIndex, drills.length])

  if (!lesson) {
    return (
      <Layout>
        <p className="muted">Loading…</p>
      </Layout>
    )
  }

  function finish() {
    mark(lesson!.id, 'grammar')
    navigate(`/lesson/${lesson!.id}/quiz`)
  }

  function checkAnswer(given: string) {
    if (!drill) return
    const ok = answersEqual(drill.answer, given)
    setFeedback(ok ? 'Correct!' : `Answer: ${Array.isArray(drill.answer) ? drill.answer.join(' / ') : drill.answer}`)
    if (ok) {
      setTimeout(() => {
        if (drillIndex < drills.length - 1) {
          setDrillIndex((i) => i + 1)
          setInput('')
          setPicked(null)
          setFeedback(null)
        } else {
          finish()
        }
      }, 650)
    }
  }

  if (lesson.grammar.length === 0 && drills.length === 0) {
    return (
      <Layout>
        <div className="panel">
          <h1>Grammar</h1>
          <p className="empty">No grammar content yet for this stub.</p>
          <div className="btn-row">
            <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
              Back
            </Link>
            <button type="button" className="btn" onClick={finish}>
              Continue to quiz
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Grammar · {lesson.titleDe}
        </p>
        <h1 style={{ marginTop: 0 }}>
          {phase === 'learn' ? 'Explanations' : progressLabel}
        </h1>

        <div className="tabs">
          <button
            type="button"
            className={`tab ${phase === 'learn' ? 'active' : ''}`}
            onClick={() => setPhase('learn')}
          >
            Learn
          </button>
          <button
            type="button"
            className={`tab ${phase === 'drill' ? 'active' : ''}`}
            onClick={() => setPhase('drill')}
            disabled={drills.length === 0}
          >
            Drills
          </button>
        </div>

        {phase === 'learn' && (
          <>
            {lesson.grammar.map((g) => (
              <div key={g.id} className="grammar-block">
                <h2 style={{ marginBottom: 0.25 }}>{g.titleDe}</h2>
                <p
                  className={`muted ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}
                  style={{ marginTop: 0 }}
                >
                  {pickGloss(g.titleEn, g.titleFa, helperLanguage)}
                </p>
                <p className={isRtl(helperLanguage) ? 'gloss-rtl' : undefined}>
                  {pickGloss(g.explanationEn, g.explanationFa, helperLanguage)}
                </p>
                <div className="patterns">
                  {g.patterns.map((p) => (
                    <div key={p}>{p}</div>
                  ))}
                </div>
                <ul>
                  {g.examples.map((ex) => (
                    <li key={ex.de}>
                      <strong>{ex.de}</strong>
                      <span
                        className={`muted ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}
                      >
                        {' '}
                        — {pickGloss(ex.en, ex.fa, helperLanguage)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            <div className="btn-row">
              <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
                Back
              </Link>
              {drills.length > 0 ? (
                <button
                  type="button"
                  className="btn"
                  onClick={() => setPhase('drill')}
                >
                  Practice drills
                </button>
              ) : (
                <button type="button" className="btn" onClick={finish}>
                  Continue to quiz
                </button>
              )}
            </div>
          </>
        )}

        {phase === 'drill' && drill && (
          <>
            <p>
              <strong>{drill.promptDe}</strong>
            </p>
            <p className={`muted ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}>
              {pickGloss(drill.promptEn, drill.promptFa, helperLanguage)}
            </p>
            <p style={{ fontSize: '1.15rem' }}>{drill.content}</p>

            {drill.type === 'multiple-choice' && drill.options && (
              <div className="options">
                {drill.options.map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    className={`option ${picked === opt ? (answersEqual(drill.answer, opt) ? 'correct' : 'wrong') : ''}`}
                    onClick={() => {
                      setPicked(opt)
                      checkAnswer(opt)
                    }}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            )}

            {(drill.type === 'cloze' ||
              drill.type === 'article-type' ||
              drill.type === 'conjugate' ||
              drill.type === 'formal-informal') && (
              <>
                <input
                  className="field"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your answer"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') checkAnswer(input)
                  }}
                />
                <div className="btn-row">
                  <button
                    type="button"
                    className="btn"
                    onClick={() => checkAnswer(input)}
                  >
                    Check
                  </button>
                </div>
              </>
            )}

            {drill.type === 'reorder' && (
              <>
                <div className="chip-row">
                  {reorder.map((w, i) => (
                    <button
                      key={`${w}-${i}`}
                      type="button"
                      className="chip"
                      onClick={() => {
                        setReorder((r) => r.filter((_, j) => j !== i))
                        setPool((p) => [...p, w])
                      }}
                    >
                      {w}
                    </button>
                  ))}
                </div>
                <div className="chip-row">
                  {pool.map((w, i) => (
                    <button
                      key={`${w}-${i}`}
                      type="button"
                      className="chip"
                      onClick={() => {
                        setPool((p) => p.filter((_, j) => j !== i))
                        setReorder((r) => [...r, w])
                      }}
                    >
                      {w}
                    </button>
                  ))}
                </div>
                <div className="btn-row">
                  <button
                    type="button"
                    className="btn"
                    onClick={() => checkAnswer(reorder.join(' '))}
                  >
                    Check order
                  </button>
                </div>
              </>
            )}

            {feedback && (
              <div
                className={`feedback ${feedback.startsWith('Correct') ? 'ok' : 'no'}`}
              >
                {feedback}
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
