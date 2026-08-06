import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import type { Lesson } from '../types/lesson'
import { fetchLesson } from '../lib/content'
import { useProgress } from '../context/ProgressContext'
import { Layout } from '../components/Layout'

export function GoalsPage() {
  const { lessonId = '' } = useParams()
  const navigate = useNavigate()
  const { mark } = useProgress()
  const [lesson, setLesson] = useState<Lesson | null>(null)

  useEffect(() => {
    fetchLesson(lessonId).then(setLesson)
  }, [lessonId])

  if (!lesson) {
    return (
      <Layout>
        <p className="muted">Loading…</p>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="panel">
        <p className="muted" style={{ marginTop: 0 }}>
          Goals · {lesson.titleDe}
        </p>
        <h1 style={{ marginTop: 0 }}>What you will learn</h1>
        <ul className="goal-list">
          {lesson.goals.map((g, i) => (
            <li key={i}>
              <div>{g.de}</div>
              <div className="en">{g.en}</div>
            </li>
          ))}
        </ul>
        <div className="btn-row">
          <Link className="btn secondary" to={`/lesson/${lesson.id}`}>
            Back
          </Link>
          <button
            type="button"
            className="btn"
            onClick={() => {
              mark(lesson.id, 'goals')
              navigate(`/lesson/${lesson.id}/vocab`)
            }}
          >
            Continue to vocabulary
          </button>
        </div>
      </div>
    </Layout>
  )
}
