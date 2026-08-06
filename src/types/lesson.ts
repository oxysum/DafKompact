export type Level = 'A1' | 'A2' | 'B1'

export type PartOfSpeech =
  | 'noun'
  | 'verb'
  | 'adjective'
  | 'adverb'
  | 'phrase'
  | 'other'

export interface Goal {
  de: string
  en: string
}

export interface VocabItem {
  id: string
  de: string
  en: string
  article?: 'der' | 'die' | 'das'
  pos?: PartOfSpeech
  exampleDe?: string
  exampleEn?: string
  tags?: string[]
}

export interface GrammarExample {
  de: string
  en: string
}

export interface GrammarTopic {
  id: string
  titleDe: string
  titleEn: string
  explanationEn: string
  patterns: string[]
  examples: GrammarExample[]
}

export type DrillType =
  | 'cloze'
  | 'multiple-choice'
  | 'reorder'
  | 'article-type'
  | 'conjugate'
  | 'formal-informal'

export interface DrillItem {
  id: string
  type: DrillType
  promptDe: string
  promptEn: string
  /** For cloze: sentence with ___ ; for MC: question; for reorder: words joined later */
  content: string
  options?: string[]
  answer: string | string[]
  grammarId?: string
}

export type QuizType = 'vocab-de-en' | 'vocab-en-de' | 'grammar-mc' | 'cloze'

export interface QuizItem {
  id: string
  type: QuizType
  prompt: string
  options?: string[]
  answer: string
  vocabId?: string
  grammarId?: string
}

export interface ListeningTrackRef {
  id: string
  cd: number
  track: number
  audioUrl: string
  preview: string
}

export interface ListeningTrack extends ListeningTrackRef {
  lessonNumber: number | null
  text: string
}

export interface Lesson {
  id: string
  level: Level
  number: number
  titleDe: string
  titleEn: string
  status: 'complete' | 'stub'
  goals: Goal[]
  vocab: VocabItem[]
  grammar: GrammarTopic[]
  drills: DrillItem[]
  quiz: QuizItem[]
  listening?: ListeningTrackRef[]
}

export interface LessonIndexEntry {
  id: string
  level: Level
  number: number
  titleDe: string
  titleEn: string
  status: 'complete' | 'stub'
  order: number
}

export interface ContentIndex {
  book: string
  languagePair: string
  lessons: LessonIndexEntry[]
}

export type StepId = 'goals' | 'vocab' | 'grammar' | 'quiz'

export interface LessonProgress {
  goalsDone: boolean
  vocabDone: boolean
  grammarDone: boolean
  quizDone: boolean
  quizScore?: number
  quizAttempts: number
}

export interface ReviewItem {
  id: string
  lessonId: string
  kind: 'vocab' | 'grammar'
  mode?: 'recall' | 'de-en' | 'en-de' | 'article'
  prompt: string
  answer: string
  ease: number
  interval: number
  due: number
  reps: number
}

export interface ProgressState {
  version: 1
  lessons: Record<string, LessonProgress>
  unlockedThrough: number
  review: ReviewItem[]
}
