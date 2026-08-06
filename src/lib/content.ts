import type { ContentIndex, Lesson, ListeningTrack } from '../types/lesson'

export async function fetchIndex(): Promise<ContentIndex> {
  const res = await fetch('/content/index.json')
  if (!res.ok) throw new Error('Failed to load content index')
  return res.json()
}

export async function fetchLesson(id: string): Promise<Lesson> {
  const res = await fetch(`/content/lektionen/${id}.json`)
  if (!res.ok) throw new Error(`Failed to load lesson ${id}`)
  return res.json()
}

export async function fetchListeningTrack(id: string): Promise<ListeningTrack> {
  const res = await fetch(`/content/listening/${id}.json`)
  if (!res.ok) throw new Error(`Failed to load listening track ${id}`)
  return res.json()
}
