import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type { Lesson, LessonIndexEntry, QuizItem, ReviewItem } from '../types/lesson'
import { fetchIndex, fetchLesson } from '../lib/content'
import { QUIZ_PASS, answersEqual } from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { Layout } from '../components/Layout'

function toReview(lessonId: string, item: QuizItem): ReviewItem {
  return {
    id: `${lessonId}:${item.id}`,
    lessonId,
    kind: item.type.startsWith('vocab') ? 'vocab' : 'grammar',
    prompt: item.prompt,
    answer: item.answer,
    ease: 2.5,
    interval: 0,
    due: Date.now(),
    reps: 0,
  }
}

export function QuizPage() {
  const { lessonId = '' } = useParams()
  const navigate = useNavigate()
  const { finishQuiz } = useProgress()
  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [meta, setMeta] = useState<LessonIndexEntry | null>(null)
  const [index, setIndex] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const failedRef = useRef<ReviewItem[]>([])
  const [input, setInput] = useState('')
  const [feedback, setFeedback] = useState<string | null>(null)
  const [done, setDone] = useState(false)
  const [score, setScore] = useState(0)

  useEffect(() => {
    Promise.all([fetchLesson(lessonId), fetchIndex()]).then(([l, idx]) => {
      setLesson(l)
      setMeta(idx.lessons.find((x) => x.id === lessonId) ?? null)
    })
  }, [lessonId])

  if (!lesson || !meta) {
    return (
      <Layout>
        <p className="muted">Loading…</p>
      </Layout>
    )
  }

  const quiz = lesson.quiz

  function record(item: QuizItem, ok: boolean) {
    if (!ok) failedRef.current.push(toReview(lesson!.id, item))
    const nextCorrect = correctCount + (ok ? 1 : 0)
    setCorrectCount(nextCorrect)
    setFeedback(ok ? 'Correct!' : `Answer: ${item.answer}`)

    setTimeout(() => {
      if (index < quiz.length - 1) {
        setIndex((i) => i + 1)
        setInput('')
        setFeedback(null)
      } else {
        const finalScore = nextCorrect / quiz.length
        setScore(finalScore)
        setDone(true)
        finishQuiz(lesson!.id, meta!.order, finalScore, failedRef.current)
      }
    }, 700)
  }

  function submit(given: string) {
    const item = quiz[index]!
    record(item, answersEqual(item.answer, given))
  }

  if (quiz.length === 0) {
    return (
      <Layout>
        <div className="panel">
          <h1>Quiz</h1>
          <p className="empty">No quiz items yet. Marking this lesson complete.</p>
          <div className="btn-row">
            <button
              type="button"
              className="btn"
              onClick={() => {
                finishQuiz(lesson.id, meta.order, 1, [])
                navigate(`/lesson/${lesson.id}`)
              }}
            >
              Complete lesson
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  if (done) {
    const passed = score >= QUIZ_PASS
    return (
      <Layout>
        <div className="panel" style={{ textAlign: 'center' }}>
          <p className="muted">Quiz result</p>
          <div className="score-ring">{Math.round(score * 100)}%</div>
          <p>
            {passed
              ? 'Passed! The next lesson is unlocked.'
              : `Need ${Math.round(QUIZ_PASS * 100)}% to unlock the next lesson. Try again.`}
          </p>
          <div className="btn-row" style={{ justifyContent: 'center' }}>
            <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
              Lesson hub
            </Link>
            {!passed && (
              <button
                type="button"
                className="btn"
                onClick={() => {
                  setIndex(0)
                  setCorrectCount(0)
                  failedRef.current = []
                  setDone(false)
                  setFeedback(null)
                  setInput('')
                }}
              >
                Retry quiz
              </button>
            )}
            {passed && (
              <Link className="btn" to="/">
                All lessons
              </Link>
            )}
          </div>
        </div>
      </Layout>
    )
  }

  const item = quiz[index]!

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Quiz · {index + 1}/{quiz.length}
        </p>
        <h1 style={{ marginTop: 0 }}>{item.prompt}</h1>

        {item.options && (
          <div className="options">
            {item.options.map((opt) => (
              <button
                key={opt}
                type="button"
                className="option"
                disabled={!!feedback}
                onClick={() => submit(opt)}
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {!item.options && (
          <>
            <input
              className="field"
              value={input}
              disabled={!!feedback}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && input.trim()) submit(input)
              }}
              placeholder="Type your answer"
            />
            <div className="btn-row">
              <button
                type="button"
                className="btn"
                disabled={!input.trim() || !!feedback}
                onClick={() => submit(input)}
              >
                Submit
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
      </div>
    </Layout>
  )
}
