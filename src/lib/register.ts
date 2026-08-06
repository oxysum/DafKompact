/** Formal (Sie) ↔ informal (du) register pairs for practice. */

export interface RegisterPair {
  id: string
  formal: string
  informal: string
  en: string
}

export const REGISTER_PAIRS: RegisterPair[] = [
  { id: 'r1', formal: 'Wie geht es Ihnen?', informal: 'Wie geht’s?', en: 'How are you?' },
  { id: 'r2', formal: 'Guten Tag!', informal: 'Hallo!', en: 'Hello' },
  { id: 'r3', formal: 'Auf Wiedersehen!', informal: 'Tschüss!', en: 'Goodbye' },
  { id: 'r4', formal: 'Wie heißen Sie?', informal: 'Wie heißt du?', en: 'What is your name?' },
  { id: 'r5', formal: 'Wo wohnen Sie?', informal: 'Wo wohnst du?', en: 'Where do you live?' },
  { id: 'r6', formal: 'Woher kommen Sie?', informal: 'Woher kommst du?', en: 'Where are you from?' },
  { id: 'r7', formal: 'Können Sie mir helfen?', informal: 'Kannst du mir helfen?', en: 'Can you help me?' },
  { id: 'r8', formal: 'Haben Sie Zeit?', informal: 'Hast du Zeit?', en: 'Do you have time?' },
  { id: 'r9', formal: 'Möchten Sie etwas trinken?', informal: 'Möchtest du etwas trinken?', en: 'Would you like something to drink?' },
  { id: 'r10', formal: 'Entschuldigen Sie!', informal: 'Entschuldigung!', en: 'Excuse me' },
  { id: 'r11', formal: 'Sprechen Sie Deutsch?', informal: 'Sprichst du Deutsch?', en: 'Do you speak German?' },
  { id: 'r12', formal: 'Was machen Sie beruflich?', informal: 'Was machst du beruflich?', en: 'What do you do for work?' },
  { id: 'r13', formal: 'Darf ich Sie etwas fragen?', informal: 'Darf ich dich etwas fragen?', en: 'May I ask you something?' },
  { id: 'r14', formal: 'Könnten Sie das bitte wiederholen?', informal: 'Kannst du das bitte wiederholen?', en: 'Could you please repeat that?' },
  { id: 'r15', formal: 'Ich danke Ihnen.', informal: 'Danke / Ich danke dir.', en: 'Thank you' },
]

export function pickRegisterPair(): RegisterPair {
  return REGISTER_PAIRS[Math.floor(Math.random() * REGISTER_PAIRS.length)]!
}
