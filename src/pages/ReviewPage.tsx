import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { answersEqual } from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'
import type { ReviewItem } from '../types/lesson'

function reviewPrompt(item: ReviewItem, lang: 'en' | 'fa'): string {
  if (lang === 'fa' && item.mode === 'en-de' && item.promptFa) {
    return item.promptFa
  }
  return item.prompt
}

function reviewAnswer(item: ReviewItem, lang: 'en' | 'fa'): string {
  if (item.mode === 'de-en') {
    return pickGloss(item.answer, item.answerFa, lang)
  }
  return item.answer
}

export function ReviewPage() {
  const { due, answerReview, stats } = useProgress()
  const { helperLanguage } = useSettings()
  const [queue, setQueue] = useState(due)
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [input, setInput] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  useEffect(() => {
    setQueue(due)
    setIndex(0)
    setRevealed(false)
    setInput('')
    setMsg(null)
  }, [due])

  const item = queue[index]

  if (queue.length === 0) {
    return (
      <Layout>
        <div className="panel">
          <h1>Review</h1>
          <p className="empty">
            Nothing due right now.
            {stats.total > 0
              ? ` You have ${stats.total} cards in your deck — finish a vocabulary step to add more, or come back when cards are due.`
              : ' Finish a vocabulary step in any lesson to enroll words into spaced review.'}
          </p>
          <div className="btn-row">
            <Link className="btn" to="/">
              Back to lessons
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  if (!item) {
    return (
      <Layout>
        <div className="panel">
          <h1>Session complete</h1>
          <p className="muted">
            Nice work.{' '}
            {stats.dueToday > 0
              ? `${stats.dueToday} still marked due later today.`
              : 'No more cards due today.'}
          </p>
          <div className="btn-row">
            <Link className="btn" to="/">
              Home
            </Link>
          </div>
        </div>
      </Layout>
    )
  }

  function advance() {
    setIndex((i) => i + 1)
    setInput('')
    setRevealed(false)
    setMsg(null)
  }

  const expected = reviewAnswer(item, helperLanguage)
  const prompt = reviewPrompt(item, helperLanguage)
  const rtlPrompt =
    helperLanguage === 'fa' && item.mode === 'en-de' && !!item.promptFa
  const rtlAnswer = helperLanguage === 'fa' && item.mode === 'de-en'

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Due now {index + 1}/{queue.length}
          {item.mode ? ` · ${item.mode}` : ` · ${item.kind}`}
          {stats.dueToday > queue.length
            ? ` · ${stats.dueToday} due today`
            : ''}
        </p>
        <h1
          className={rtlPrompt ? 'gloss-rtl' : undefined}
          style={{ marginTop: 0 }}
        >
          {prompt}
        </h1>

        {!revealed ? (
          <>
            <input
              className={`field ${rtlAnswer ? 'gloss-rtl' : ''}`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Your answer"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && input.trim()) {
                  const ok = answersEqual(expected, input)
                  setMsg(ok ? 'Correct!' : `Answer: ${expected}`)
                  answerReview(item.id, ok)
                  setTimeout(advance, 550)
                }
              }}
            />
            <div className="btn-row">
              <button
                type="button"
                className="btn secondary"
                onClick={() => setRevealed(true)}
              >
                Show answer
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const ok = answersEqual(expected, input)
                  setMsg(ok ? 'Correct!' : `Answer: ${expected}`)
                  answerReview(item.id, ok)
                  setTimeout(advance, 550)
                }}
              >
                Check
              </button>
            </div>
          </>
        ) : (
          <>
            <p className={rtlAnswer || isRtl(helperLanguage) ? 'gloss-rtl' : undefined}>
              <strong>{expected}</strong>
            </p>
            <div className="btn-row">
              <button
                type="button"
                className="btn secondary"
                onClick={() => {
                  answerReview(item.id, false)
                  advance()
                }}
              >
                Still hard
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  answerReview(item.id, true)
                  advance()
                }}
              >
                Got it
              </button>
            </div>
          </>
        )}
        {msg && (
          <div className={`feedback ${msg.startsWith('Correct') ? 'ok' : 'no'}`}>
            {msg}
          </div>
        )}
      </div>
    </Layout>
  )
}
