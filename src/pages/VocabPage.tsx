import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type { Lesson, VocabItem } from '../types/lesson'
import { fetchLesson } from '../lib/content'
import { answersEqual } from '../lib/progress'
import {
  canConjugate,
  conjugatePresent,
  extractInfinitive,
  pickPerson,
  type Person,
} from '../lib/conjugate'
import { pickRegisterPair, type RegisterPair } from '../lib/register'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { helperLabel, isRtl, pickGloss } from '../lib/gloss'
import { Layout } from '../components/Layout'
import { PronounceButton } from '../components/PronounceButton'

type Mode = 'cards' | 'match' | 'type-article' | 'conjugate' | 'register'

export function VocabPage() {
  const { lessonId = '' } = useParams()
  const navigate = useNavigate()
  const { mark, enrollLessonVocab } = useProgress()
  const { helperLanguage } = useSettings()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [mode, setMode] = useState<Mode>('cards')
  const [matchPrompt, setMatchPrompt] = useState<VocabItem | null>(null)
  const [options, setOptions] = useState<string[]>([])
  const [feedback, setFeedback] = useState<string | null>(null)
  const [round, setRound] = useState(0)
  const [typed, setTyped] = useState('')
  const [conj, setConj] = useState<{
    verb: string
    person: Person
    answer: string
  } | null>(null)
  const [reg, setReg] = useState<{
    pair: RegisterPair
    askFormal: boolean
  } | null>(null)

  useEffect(() => {
    fetchLesson(lessonId).then(setLesson)
  }, [lessonId])

  const vocab = lesson?.vocab ?? []
  const card = vocab[index]

  const articleItems = useMemo(
    () => vocab.filter((v) => v.article),
    [vocab],
  )

  const verbItems = useMemo(
    () =>
      vocab.filter(
        (v) =>
          v.pos === 'verb' && canConjugate(extractInfinitive(v.de)),
      ),
    [vocab],
  )

  useEffect(() => {
    if (!lesson) return
    setFeedback(null)
    setTyped('')

    if (mode === 'match' || mode === 'type-article') {
      if (articleItems.length === 0) return
      const item =
        articleItems[Math.floor(Math.random() * articleItems.length)]!
      setMatchPrompt(item)
      setOptions(['der', 'die', 'das'].sort(() => Math.random() - 0.5))
    }

    if (mode === 'conjugate') {
      if (verbItems.length === 0) return
      const v = verbItems[Math.floor(Math.random() * verbItems.length)]!
      const inf = extractInfinitive(v.de)
      const person = pickPerson()
      const answer = conjugatePresent(inf, person)
      if (!answer) return
      setConj({ verb: inf, person, answer })
    }

    if (mode === 'register') {
      const pair = pickRegisterPair()
      setReg({ pair, askFormal: Math.random() > 0.5 })
    }
  }, [mode, round, lesson, articleItems, verbItems])

  if (!lesson) {
    return (
      <Layout>
        <p className="muted">Loading…</p>
      </Layout>
    )
  }

  function finish() {
    enrollLessonVocab(lesson!.id, lesson!.vocab)
    mark(lesson!.id, 'vocab')
    navigate(`/lesson/${lesson!.id}/grammar`)
  }

  if (vocab.length === 0) {
    return (
      <Layout>
        <div className="panel">
          <h1>Vocabulary</h1>
          <p className="empty">
            No vocabulary cards yet for this stub lesson. You can continue the
            path.
          </p>
          <div className="btn-row">
            <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
              Back
            </Link>
            <button type="button" className="btn" onClick={finish}>
              Continue to grammar
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
          Vocabulary · {index + 1}/{vocab.length}
        </p>
        <h1 style={{ marginTop: 0 }}>{lesson.titleDe}</h1>
        <p className="muted">
          Practice below, or enroll the full list into spaced review and
          continue. DE↔EN
          {articleItems.length ? ' + articles' : ''}.
        </p>
        <p className="muted pronounce-attr">
          Pronunciations: Wikimedia Commons / de.wiktionary (CC BY-SA), when
          available.
        </p>

        <div className="tabs" style={{ flexWrap: 'wrap', marginTop: '1rem' }}>
          {(
            [
              ['cards', 'Flashcards'],
              ['match', 'Articles'],
              ['type-article', 'Type article'],
              ['conjugate', 'Conjugate'],
              ['register', 'Sie / du'],
            ] as const
          ).map(([id, label]) => (
            <button
              key={id}
              type="button"
              className={`tab ${mode === id ? 'active' : ''}`}
              onClick={() => setMode(id)}
              disabled={
                (id === 'match' || id === 'type-article') &&
                articleItems.length === 0
                  ? true
                  : id === 'conjugate' && verbItems.length === 0
              }
            >
              {label}
            </button>
          ))}
        </div>

        <div className="btn-row" style={{ marginTop: '0.35rem', marginBottom: '1rem' }}>
          <button type="button" className="btn secondary" onClick={finish}>
            Enroll all ({vocab.length}) & continue
          </button>
        </div>

        {mode === 'cards' && card && (
          <>
            <div
              className="flash-card"
              onClick={() => {
                // Don't flip when the user is selecting/copying text
                const sel = window.getSelection()?.toString()
                if (sel) return
                setFlipped((f) => !f)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') setFlipped((f) => !f)
              }}
              role="button"
              tabIndex={0}
            >
              {!flipped ? (
                <div>
                  <div className="flash-card-word">
                    <div className="de">
                      {card.article ? `${card.article} ` : ''}
                      {card.de}
                    </div>
                    {card.audioUrl ? (
                      <PronounceButton src={card.audioUrl} />
                    ) : null}
                  </div>
                  <div className="meta">
                    {card.pos ?? 'word'} · tap for{' '}
                    {helperLabel(helperLanguage)}
                  </div>
                </div>
              ) : (
                <div>
                  <div
                    className={`de ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}
                  >
                    {pickGloss(card.en, card.fa, helperLanguage)}
                  </div>
                  {card.exampleDe && (
                    <div className="meta">
                      {card.exampleDe}
                      {(() => {
                        const ex = pickGloss(
                          card.exampleEn,
                          card.exampleFa,
                          helperLanguage,
                        )
                        return ex ? ` — ${ex}` : ''
                      })()}
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="btn-row">
              <button
                type="button"
                className="btn secondary"
                disabled={index === 0}
                onClick={() => {
                  setIndex((i) => i - 1)
                  setFlipped(false)
                }}
              >
                Previous
              </button>
              {index < vocab.length - 1 ? (
                <button
                  type="button"
                  className="btn"
                  onClick={() => {
                    setIndex((i) => i + 1)
                    setFlipped(false)
                  }}
                >
                  Next card
                </button>
              ) : (
                <button type="button" className="btn" onClick={finish}>
                  Finish vocabulary
                </button>
              )}
            </div>
          </>
        )}

        {mode === 'match' && matchPrompt && (
          <>
            <p>
              Which article belongs with <strong>{matchPrompt.de}</strong>?
            </p>
            <div className="options">
              {options.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  className="option"
                  onClick={() => {
                    const ok = answersEqual(matchPrompt.article!, opt)
                    setFeedback(
                      ok
                        ? 'Correct!'
                        : `Not quite — ${matchPrompt.article} ${matchPrompt.de}`,
                    )
                    if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
            {feedback && (
              <div
                className={`feedback ${feedback.startsWith('Correct') ? 'ok' : 'no'}`}
              >
                {feedback}
              </div>
            )}
            <div className="btn-row">
              <button type="button" className="btn" onClick={finish}>
                Finish vocabulary
              </button>
            </div>
          </>
        )}

        {mode === 'type-article' && matchPrompt && (
          <>
            <p>
              Type the article for <strong>{matchPrompt.de}</strong>
            </p>
            <input
              className="field"
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              placeholder="der / die / das"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const ok = answersEqual(matchPrompt.article!, typed)
                  setFeedback(
                    ok
                      ? 'Correct!'
                      : `Answer: ${matchPrompt.article} ${matchPrompt.de}`,
                  )
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }
              }}
            />
            <div className="btn-row">
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const ok = answersEqual(matchPrompt.article!, typed)
                  setFeedback(
                    ok
                      ? 'Correct!'
                      : `Answer: ${matchPrompt.article} ${matchPrompt.de}`,
                  )
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }}
              >
                Check
              </button>
              <button type="button" className="btn secondary" onClick={finish}>
                Finish vocabulary
              </button>
            </div>
            {feedback && (
              <div
                className={`feedback ${feedback.startsWith('Correct') ? 'ok' : 'no'}`}
              >
                {feedback}
              </div>
            )}
          </>
        )}

        {mode === 'conjugate' && conj && (
          <>
            <p>
              Präsens: <strong>{conj.person}</strong> +{' '}
              <strong>{conj.verb}</strong>
            </p>
            <input
              className="field"
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              placeholder={`${conj.person} …`}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const ok = answersEqual(conj.answer, typed.trim())
                  setFeedback(ok ? 'Correct!' : `Answer: ${conj.answer}`)
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }
              }}
            />
            <div className="btn-row">
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const ok = answersEqual(conj.answer, typed.trim())
                  setFeedback(ok ? 'Correct!' : `Answer: ${conj.answer}`)
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }}
              >
                Check
              </button>
              <button type="button" className="btn secondary" onClick={finish}>
                Finish vocabulary
              </button>
            </div>
            {feedback && (
              <div
                className={`feedback ${feedback.startsWith('Correct') ? 'ok' : 'no'}`}
              >
                {feedback}
              </div>
            )}
          </>
        )}

        {mode === 'register' && reg && (
          <>
            <p
              className={`muted ${isRtl(helperLanguage) ? 'gloss-rtl' : ''}`}
            >
              {pickGloss(reg.pair.en, reg.pair.fa, helperLanguage)}
            </p>
            <p>
              {reg.askFormal ? (
                <>
                  Make it <strong>formal (Sie)</strong>:{' '}
                  <em>{reg.pair.informal}</em>
                </>
              ) : (
                <>
                  Make it <strong>informal (du)</strong>:{' '}
                  <em>{reg.pair.formal}</em>
                </>
              )}
            </p>
            <input
              className="field"
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              placeholder="Type the other form"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const answer = reg.askFormal
                    ? reg.pair.formal
                    : reg.pair.informal
                  const ok = answersEqual(answer, typed)
                  setFeedback(ok ? 'Correct!' : `Answer: ${answer}`)
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }
              }}
            />
            <div className="btn-row">
              <button
                type="button"
                className="btn"
                onClick={() => {
                  const answer = reg.askFormal
                    ? reg.pair.formal
                    : reg.pair.informal
                  const ok = answersEqual(answer, typed)
                  setFeedback(ok ? 'Correct!' : `Answer: ${answer}`)
                  if (ok) setTimeout(() => setRound((n) => n + 1), 450)
                }}
              >
                Check
              </button>
              <button type="button" className="btn secondary" onClick={finish}>
                Finish vocabulary
              </button>
            </div>
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
