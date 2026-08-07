import type { ReviewItem, VocabItem } from '../types/lesson'

export function newReviewItem(partial: Omit<ReviewItem, 'ease' | 'interval' | 'due' | 'reps'> & Partial<Pick<ReviewItem, 'ease' | 'interval' | 'due' | 'reps'>>): ReviewItem {
  return {
    ease: 2.5,
    interval: 0,
    due: Date.now(),
    reps: 0,
    mode: 'recall',
    ...partial,
  }
}

export function vocabToReviewItems(lessonId: string, vocab: VocabItem[]): ReviewItem[] {
  const items: ReviewItem[] = []
  for (const v of vocab) {
    const label = v.article ? `${v.article} ${v.de}` : v.de
    // DE → helper language
    items.push(
      newReviewItem({
        id: `${lessonId}:vocab:${v.id}:de-en`,
        lessonId,
        kind: 'vocab',
        mode: 'de-en',
        prompt: `What does “${label}” mean?`,
        answer: v.en,
        answerFa: v.fa,
      }),
    )
    // Helper language → DE
    items.push(
      newReviewItem({
        id: `${lessonId}:vocab:${v.id}:en-de`,
        lessonId,
        kind: 'vocab',
        mode: 'en-de',
        prompt: `How do you say “${v.en}” in German?`,
        promptFa: v.fa
          ? `«${v.fa}» را به آلمانی چگونه می‌گویید؟`
          : undefined,
        answer: label,
      }),
    )
    if (v.article) {
      items.push(
        newReviewItem({
          id: `${lessonId}:vocab:${v.id}:article`,
          lessonId,
          kind: 'vocab',
          mode: 'article',
          prompt: `Which article? ${v.de}`,
          answer: v.article,
        }),
      )
    }
  }
  return items
}
