import type {
  LessonProgress,
  ProgressState,
  ReviewItem,
  StepId,
  VocabItem,
} from '../types/lesson'
import { vocabToReviewItems } from './srs'

const KEY = 'daf-kompakt-progress-v1'
export const QUIZ_PASS = 0.7

export function defaultProgress(): ProgressState {
  return {
    version: 1,
    lessons: {},
    unlockedThrough: 1,
    review: [],
  }
}

export function loadProgress(): ProgressState {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return defaultProgress()
    const parsed = JSON.parse(raw) as ProgressState
    if (parsed.version !== 1) return defaultProgress()
    return parsed
  } catch {
    return defaultProgress()
  }
}

export function saveProgress(state: ProgressState): void {
  localStorage.setItem(KEY, JSON.stringify(state))
}

export function getLessonProgress(
  state: ProgressState,
  lessonId: string,
): LessonProgress {
  return (
    state.lessons[lessonId] ?? {
      goalsDone: false,
      vocabDone: false,
      grammarDone: false,
      quizDone: false,
      quizAttempts: 0,
    }
  )
}

export function isLessonUnlocked(state: ProgressState, order: number): boolean {
  return order <= state.unlockedThrough
}

export function lessonPercent(p: LessonProgress): number {
  const steps = [p.goalsDone, p.vocabDone, p.grammarDone, p.quizDone]
  return Math.round((steps.filter(Boolean).length / steps.length) * 100)
}

export function markStep(
  state: ProgressState,
  lessonId: string,
  step: StepId,
): ProgressState {
  const current = getLessonProgress(state, lessonId)
  const next: LessonProgress = { ...current }
  if (step === 'goals') next.goalsDone = true
  if (step === 'vocab') next.vocabDone = true
  if (step === 'grammar') next.grammarDone = true
  return {
    ...state,
    lessons: { ...state.lessons, [lessonId]: next },
  }
}

/** Enroll lesson vocab into SRS (does not overwrite existing cards’ scheduling). */
export function enrollVocab(
  state: ProgressState,
  lessonId: string,
  vocab: VocabItem[],
): ProgressState {
  const map = new Map(state.review.map((r) => [r.id, r]))
  for (const item of vocabToReviewItems(lessonId, vocab)) {
    const existing = map.get(item.id)
    if (!existing) {
      map.set(item.id, item)
      continue
    }
    // Refresh FA fields when re-enrolling without resetting schedule
    map.set(item.id, {
      ...existing,
      answerFa: item.answerFa ?? existing.answerFa,
      promptFa: item.promptFa ?? existing.promptFa,
    })
  }
  return { ...state, review: [...map.values()] }
}

export function completeQuiz(
  state: ProgressState,
  lessonId: string,
  order: number,
  score: number,
  failed: ReviewItem[],
): ProgressState {
  const current = getLessonProgress(state, lessonId)
  const passed = score >= QUIZ_PASS
  const next: LessonProgress = {
    ...current,
    quizAttempts: current.quizAttempts + 1,
    quizScore: score,
    quizDone: passed || current.quizDone,
  }
  const unlockedThrough = passed
    ? Math.max(state.unlockedThrough, order + 1)
    : state.unlockedThrough

  const reviewMap = new Map(state.review.map((r) => [r.id, r]))
  for (const item of failed) {
    const existing = reviewMap.get(item.id)
    if (existing) {
      reviewMap.set(item.id, scheduleReview(existing, false))
    } else {
      reviewMap.set(item.id, scheduleReview(item, false))
    }
  }

  return {
    ...state,
    lessons: { ...state.lessons, [lessonId]: next },
    unlockedThrough: Math.min(unlockedThrough, 30),
    review: [...reviewMap.values()],
  }
}

/** Lightweight SM-2 style interval update */
export function scheduleReview(item: ReviewItem, correct: boolean): ReviewItem {
  const now = Date.now()
  if (correct) {
    const reps = item.reps + 1
    const ease = Math.min(3, item.ease + 0.1)
    const interval =
      reps === 1
        ? 1
        : reps === 2
          ? 3
          : Math.max(1, Math.round((item.interval || 1) * ease))
    return {
      ...item,
      reps,
      ease,
      interval,
      due: now + interval * 24 * 60 * 60 * 1000,
    }
  }
  return {
    ...item,
    reps: 0,
    ease: Math.max(1.3, item.ease - 0.2),
    interval: 1,
    due: now + 60 * 60 * 1000,
  }
}

export function dueReviews(state: ProgressState): ReviewItem[] {
  const now = Date.now()
  return state.review
    .filter((r) => r.due <= now)
    .sort((a, b) => a.due - b.due)
}

export function reviewStats(state: ProgressState): {
  dueNow: number
  dueToday: number
  total: number
} {
  const now = Date.now()
  const end = new Date()
  end.setHours(23, 59, 59, 999)
  const today = end.getTime()
  return {
    dueNow: state.review.filter((r) => r.due <= now).length,
    dueToday: state.review.filter((r) => r.due <= today).length,
    total: state.review.length,
  }
}

export function exportProgress(state: ProgressState): string {
  return JSON.stringify(state, null, 2)
}

export function importProgress(json: string): ProgressState {
  const parsed = JSON.parse(json) as ProgressState
  if (parsed.version !== 1) throw new Error('Unsupported progress version')
  return parsed
}

export function answersEqual(
  expected: string | string[],
  given: string,
): boolean {
  const norm = (s: string) =>
    s
      .trim()
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/\s+([?!.,;:…])/g, '$1')
      .replace(/[.…]/g, '.')
  const g = norm(given)
  if (Array.isArray(expected)) return expected.some((e) => norm(e) === g)
  if (norm(expected) === g) return true
  if (expected.includes('/')) {
    return expected.split('/').some((part) => norm(part) === g)
  }
  return false
}
