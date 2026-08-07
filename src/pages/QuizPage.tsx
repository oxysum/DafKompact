import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type {
  Lesson,
  LessonIndexEntry,
  QuizItem,
  ReviewItem,
  VocabItem,
} from '../types/lesson'
import { fetchIndex, fetchLesson } from '../lib/content'
import { QUIZ_PASS, answersEqual } from '../lib/progress'
import { useProgress } from '../context/ProgressContext'
import { useSettings } from '../context/SettingsContext'
import { isRtl, pickGloss } from '../lib/gloss'
import type { HelperLanguage } from '../lib/settings'
import { Layout } from '../components/Layout'

function findVocab(lesson: Lesson, item: QuizItem): VocabItem | undefined {
  if (item.vocabId) {
    return lesson.vocab.find((v) => v.id === item.vocabId)
  }
  if (item.type === 'vocab-de-en') {
    return lesson.vocab.find(
      (v) => answersEqual(v.en, item.answer) || item.prompt.includes(v.de),
    )
  }
  if (item.type === 'vocab-en-de') {
    return lesson.vocab.find(
      (v) =>
        item.prompt.includes(v.en) ||
        answersEqual(v.article ? `${v.article} ${v.de}` : v.de, item.answer),
    )
  }
  return undefined
}

function resolveQuiz(
  lesson: Lesson,
  item: QuizItem,
  lang: HelperLanguage,
): { prompt: string; answer: string; rtlPrompt: boolean; rtlAnswer: boolean } {
  const v = findVocab(lesson, item)
  if (item.type === 'vocab-de-en' && v) {
    const answer = pickGloss(v.en, v.fa, lang)
    return {
      prompt: item.prompt,
      answer,
      rtlPrompt: false,
      rtlAnswer: lang === 'fa' && !!v.fa,
    }
  }
  if (item.type === 'vocab-en-de' && v) {
    const gloss = pickGloss(v.en, v.fa, lang)
    const prompt =
      lang === 'fa' && v.fa
        ? `«${v.fa}» را به آلمانی چگونه می‌گویید؟`
        : item.prompt.includes(v.en)
          ? item.prompt.replace(v.en, gloss)
          : `How do you say “${gloss}” in German?`
    return {
      prompt,
      answer: item.answer,
      rtlPrompt: lang === 'fa' && !!v.fa,
      rtlAnswer: false,
    }
  }
  return {
    prompt: item.prompt,
    answer: item.answer,
    rtlPrompt: false,
    rtlAnswer: false,
  }
}

function toReview(
  lessonId: string,
  item: QuizItem,
  resolved: { prompt: string; answer: string },
): ReviewItem {
  return {
    id: `${lessonId}:${item.id}`,
    lessonId,
    kind: item.type.startsWith('vocab') ? 'vocab' : 'grammar',
    prompt: resolved.prompt,
    answer: resolved.answer,
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
  const { helperLanguage } = useSettings()
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

  function record(
    item: QuizItem,
    ok: boolean,
    resolved: { prompt: string; answer: string },
  ) {
    if (!ok) failedRef.current.push(toReview(lesson!.id, item, resolved))
    const nextCorrect = correctCount + (ok ? 1 : 0)
    setCorrectCount(nextCorrect)
    setFeedback(ok ? 'Correct!' : `Answer: ${resolved.answer}`)

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
    const q = quiz[index]!
    const resolved = resolveQuiz(lesson!, q, helperLanguage)
    record(q, answersEqual(resolved.answer, given), resolved)
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
  const resolved = resolveQuiz(lesson, item, helperLanguage)

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Quiz · {index + 1}/{quiz.length}
        </p>
        <h1
          className={resolved.rtlPrompt ? 'gloss-rtl' : undefined}
          style={{ marginTop: 0 }}
        >
          {resolved.prompt}
        </h1>

        {item.options && (
          <div className="options">
            {item.options.map((opt) => (
              <button
                key={opt}
                type="button"
                className={`option ${
                  resolved.rtlAnswer && isRtl(helperLanguage) ? 'gloss-rtl' : ''
                }`}
                disabled={!!feedback}
                onClick={() => submit(opt)}
              >
                {item.type === 'vocab-de-en' && opt === item.answer
                  ? resolved.answer
                  : opt}
              </button>
            ))}
          </div>
        )}

        {!item.options && (
          <>
            <input
              className={`field ${resolved.rtlAnswer ? 'gloss-rtl' : ''}`}
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
