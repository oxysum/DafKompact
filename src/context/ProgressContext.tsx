import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  useEffect,
  type ReactNode,
} from 'react'
import type { ProgressState, ReviewItem, StepId, VocabItem } from '../types/lesson'
import {
  completeQuiz,
  defaultProgress,
  dueReviews,
  enrollVocab,
  exportProgress,
  importProgress,
  loadProgress,
  markStep,
  reviewStats,
  saveProgress,
  scheduleReview,
} from '../lib/progress'

interface ProgressContextValue {
  progress: ProgressState
  ready: boolean
  mark: (lessonId: string, step: StepId) => void
  enrollLessonVocab: (lessonId: string, vocab: VocabItem[]) => void
  finishQuiz: (
    lessonId: string,
    order: number,
    score: number,
    failed: ReviewItem[],
  ) => void
  answerReview: (id: string, correct: boolean) => void
  due: ReviewItem[]
  stats: { dueNow: number; dueToday: number; total: number }
  resetAll: () => void
  exportJson: () => string
  importJson: (json: string) => void
}

const ProgressContext = createContext<ProgressContextValue | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [progress, setProgress] = useState<ProgressState>(defaultProgress)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setProgress(loadProgress())
    setReady(true)
  }, [])

  useEffect(() => {
    if (!ready) return
    saveProgress(progress)
  }, [progress, ready])

  const mark = useCallback((lessonId: string, step: StepId) => {
    setProgress((p) => markStep(p, lessonId, step))
  }, [])

  const enrollLessonVocab = useCallback(
    (lessonId: string, vocab: VocabItem[]) => {
      setProgress((p) => enrollVocab(p, lessonId, vocab))
    },
    [],
  )

  const finishQuiz = useCallback(
    (lessonId: string, order: number, score: number, failed: ReviewItem[]) => {
      setProgress((p) => completeQuiz(p, lessonId, order, score, failed))
    },
    [],
  )

  const answerReview = useCallback((id: string, correct: boolean) => {
    setProgress((p) => ({
      ...p,
      review: p.review.map((r) =>
        r.id === id ? scheduleReview(r, correct) : r,
      ),
    }))
  }, [])

  const resetAll = useCallback(() => setProgress(defaultProgress()), [])

  const exportJson = useCallback(() => exportProgress(progress), [progress])

  const importJson = useCallback((json: string) => {
    setProgress(importProgress(json))
  }, [])

  const due = useMemo(() => dueReviews(progress), [progress])
  const stats = useMemo(() => reviewStats(progress), [progress])

  const value = useMemo(
    () => ({
      progress,
      ready,
      mark,
      enrollLessonVocab,
      finishQuiz,
      answerReview,
      due,
      stats,
      resetAll,
      exportJson,
      importJson,
    }),
    [
      progress,
      ready,
      mark,
      enrollLessonVocab,
      finishQuiz,
      answerReview,
      due,
      stats,
      resetAll,
      exportJson,
      importJson,
    ],
  )

  return (
    <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>
  )
}

export function useProgress() {
  const ctx = useContext(ProgressContext)
  if (!ctx) throw new Error('useProgress outside provider')
  return ctx
}
