#!/usr/bin/env node
/**
 * Generates content/index.json and all 30 lesson JSON shells.
 * Lektionen 1–8 are fully authored; 9–30 are stubs with titles + goals.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')
const outDir = path.join(root, 'public', 'content', 'lektionen')
const indexPath = path.join(root, 'public', 'content', 'index.json')

fs.mkdirSync(outDir, { recursive: true })

const meta = [
  { id: 'a1-l01', level: 'A1', number: 1, titleDe: 'Ich und die anderen', titleEn: 'Me and the others' },
  { id: 'a1-l02', level: 'A1', number: 2, titleDe: 'Termine, Termine', titleEn: 'Appointments, appointments' },
  { id: 'a1-l03', level: 'A1', number: 3, titleDe: 'Unternehmen Familie', titleEn: 'Family enterprise' },
  { id: 'a1-l04', level: 'A1', number: 4, titleDe: 'Spiel und Spaß', titleEn: 'Play and fun' },
  { id: 'a1-l05', level: 'A1', number: 5, titleDe: 'Endlich ein Zimmer!', titleEn: 'Finally a room!' },
  { id: 'a1-l06', level: 'A1', number: 6, titleDe: 'Kleider machen Leute', titleEn: 'Clothes make the person' },
  { id: 'a1-l07', level: 'A1', number: 7, titleDe: 'Grüezi in der Schweiz', titleEn: 'Hello in Switzerland' },
  { id: 'a1-l08', level: 'A1', number: 8, titleDe: 'Hmmm, das schmeckt!', titleEn: 'Hmm, that tastes good!' },
  { id: 'a2-l09', level: 'A2', number: 9, titleDe: 'Feste feiern, wie sie fallen', titleEn: 'Celebrating festivals as they come' },
  { id: 'a2-l10', level: 'A2', number: 10, titleDe: 'Umziehen, ausziehen, einziehen', titleEn: 'Moving in and out' },
  { id: 'a2-l11', level: 'A2', number: 11, titleDe: 'Neu in Köln', titleEn: 'New in Cologne' },
  { id: 'a2-l12', level: 'A2', number: 12, titleDe: 'Bankgeschichten und andere', titleEn: 'Bank stories and more' },
  { id: 'a2-l13', level: 'A2', number: 13, titleDe: 'Die Gesundheit ist wie das Salz', titleEn: 'Health is like salt' },
  { id: 'a2-l14', level: 'A2', number: 14, titleDe: 'Herbst in München', titleEn: 'Autumn in Munich' },
  { id: 'a2-l15', level: 'A2', number: 15, titleDe: 'Eine Reise nach Wien', titleEn: 'A trip to Vienna' },
  { id: 'a2-l16', level: 'A2', number: 16, titleDe: 'Fünfhundert Berufe! Aber welcher?', titleEn: 'Five hundred jobs! But which one?' },
  { id: 'a2-l17', level: 'A2', number: 17, titleDe: 'Praktikum: Erfahrung, Lernen, Spaß', titleEn: 'Internship: experience, learning, fun' },
  { id: 'a2-l18', level: 'A2', number: 18, titleDe: 'Von den Alpen bis ans Meer', titleEn: 'From the Alps to the sea' },
  { id: 'b1-l19', level: 'B1', number: 19, titleDe: 'Trainee in Liechtenstein', titleEn: 'Trainee in Liechtenstein' },
  { id: 'b1-l20', level: 'B1', number: 20, titleDe: 'Verkehrsunfall in der Innenstadt', titleEn: 'Traffic accident downtown' },
  { id: 'b1-l21', level: 'B1', number: 21, titleDe: 'Kreativ in Hamburg', titleEn: 'Creative in Hamburg' },
  { id: 'b1-l22', level: 'B1', number: 22, titleDe: 'Ab die Post', titleEn: 'Off to the post office' },
  { id: 'b1-l23', level: 'B1', number: 23, titleDe: 'Studium in Deutschland', titleEn: 'Studying in Germany' },
  { id: 'b1-l24', level: 'B1', number: 24, titleDe: 'Mit der Natur arbeiten', titleEn: 'Working with nature' },
  { id: 'b1-l25', level: 'B1', number: 25, titleDe: 'Die Kunst, (keine) Fehler zu machen', titleEn: 'The art of (not) making mistakes' },
  { id: 'b1-l26', level: 'B1', number: 26, titleDe: 'Auf nach Dresden!', titleEn: 'Off to Dresden!' },
  { id: 'b1-l27', level: 'B1', number: 27, titleDe: 'Geschichten und Gesichter Berlins', titleEn: "Berlin's stories and faces" },
  { id: 'b1-l28', level: 'B1', number: 28, titleDe: 'Von hier nach dort – von dort nach hier', titleEn: 'From here to there – from there to here' },
  { id: 'b1-l29', level: 'B1', number: 29, titleDe: 'Interessieren Sie sich für Politik?', titleEn: 'Are you interested in politics?' },
  { id: 'b1-l30', level: 'B1', number: 30, titleDe: 'Hauptperson Deutsch', titleEn: 'German takes center stage' },
]

const stubGoals = {
  a1: [
    { de: 'Lernziele dieser Lektion im Kursbuch nachlesen', en: 'Review this lesson’s learning goals in the course book' },
    { de: 'Wichtige Wörter und Redemittel üben', en: 'Practice key words and useful phrases' },
  ],
  a2: [
    { de: 'Sprachhandlungen der Lektion verstehen und anwenden', en: 'Understand and apply this lesson’s language functions' },
    { de: 'Grammatik der Lektion üben', en: 'Practice this lesson’s grammar' },
  ],
  b1: [
    { de: 'Komplexere Texte und Gespräche der Lektion bearbeiten', en: 'Work with more complex texts and conversations from this lesson' },
    { de: 'Grammatik und Wortschatz vertiefen', en: 'Deepen grammar and vocabulary' },
  ],
}

function emptyLesson(m, goals, status = 'stub') {
  return {
    id: m.id,
    level: m.level,
    number: m.number,
    titleDe: m.titleDe,
    titleEn: m.titleEn,
    status,
    goals,
    vocab: [],
    grammar: [],
    drills: [],
    quiz: [],
  }
}

function mcDrill(id, promptDe, promptEn, content, options, answer, grammarId) {
  return { id, type: 'multiple-choice', promptDe, promptEn, content, options, answer, grammarId }
}

function clozeDrill(id, promptDe, promptEn, content, answer, grammarId) {
  return { id, type: 'cloze', promptDe, promptEn, content, answer, grammarId }
}

function reorderDrill(id, promptDe, promptEn, words, answer, grammarId) {
  return {
    id,
    type: 'reorder',
    promptDe,
    promptEn,
    content: words.join(' | '),
    answer,
    grammarId,
  }
}

/** @type {Record<string, object>} */
const fullLessons = {}

// ——— Lektion 1 ———
fullLessons['a1-l01'] = {
  id: 'a1-l01',
  level: 'A1',
  number: 1,
  titleDe: 'Ich und die anderen',
  titleEn: 'Me and the others',
  status: 'complete',
  goals: [
    { de: 'Sich begrüßen (formell und informell)', en: 'Greet people (formal and informal)' },
    { de: 'Sich und andere vorstellen', en: 'Introduce yourself and others' },
    { de: 'Zahlen von 1 bis 1 Milliarde verstehen und sprechen', en: 'Understand and say numbers from 1 to 1 billion' },
    { de: 'Telefonnummern verstehen und sprechen', en: 'Understand and say phone numbers' },
    { de: 'Namen buchstabieren und notieren', en: 'Spell and note down names' },
    { de: 'Personalbogen ausfüllen', en: 'Fill in a personal data form' },
    { de: 'Sagen, woher man kommt (Adresse, Land, Kontinent)', en: 'Say where you come from (address, country, continent)' },
  ],
  vocab: [
    { id: 'v1', de: 'Guten Tag', en: 'Good day / Hello (formal)', pos: 'phrase', exampleDe: 'Guten Tag, Frau Meier!', exampleEn: 'Good day, Ms Meier!' },
    { id: 'v2', de: 'Hallo', en: 'Hello (informal)', pos: 'phrase', exampleDe: 'Hallo, wie geht’s?', exampleEn: "Hi, how's it going?" },
    { id: 'v3', de: 'Tschüss', en: 'Bye (informal)', pos: 'phrase' },
    { id: 'v4', de: 'Auf Wiedersehen', en: 'Goodbye (formal)', pos: 'phrase' },
    { id: 'v5', de: 'sich vorstellen', en: 'to introduce oneself', pos: 'verb', exampleDe: 'Darf ich mich vorstellen?', exampleEn: 'May I introduce myself?' },
    { id: 'v6', de: 'heißen', en: 'to be called / named', pos: 'verb', exampleDe: 'Ich heiße Anna.', exampleEn: 'My name is Anna.' },
    { id: 'v7', de: 'kommen', en: 'to come', pos: 'verb', exampleDe: 'Ich komme aus Spanien.', exampleEn: 'I come from Spain.' },
    { id: 'v8', de: 'wohnen', en: 'to live (reside)', pos: 'verb', exampleDe: 'Ich wohne in Berlin.', exampleEn: 'I live in Berlin.' },
    { id: 'v9', de: 'Name', en: 'name', article: 'der', pos: 'noun', exampleDe: 'Wie ist Ihr Name?', exampleEn: 'What is your name?' },
    { id: 'v10', de: 'Vorname', en: 'first name', article: 'der', pos: 'noun' },
    { id: 'v11', de: 'Nachname', en: 'last name / surname', article: 'der', pos: 'noun' },
    { id: 'v12', de: 'Adresse', en: 'address', article: 'die', pos: 'noun' },
    { id: 'v13', de: 'Telefonnummer', en: 'phone number', article: 'die', pos: 'noun' },
    { id: 'v14', de: 'E-Mail-Adresse', en: 'email address', article: 'die', pos: 'noun' },
    { id: 'v15', de: 'Land', en: 'country', article: 'das', pos: 'noun', exampleDe: 'Welches Land?', exampleEn: 'Which country?' },
    { id: 'v16', de: 'Stadt', en: 'city', article: 'die', pos: 'noun' },
    { id: 'v17', de: 'Praktikum', en: 'internship', article: 'das', pos: 'noun' },
    { id: 'v18', de: 'Student', en: 'student (male)', article: 'der', pos: 'noun' },
    { id: 'v19', de: 'Studentin', en: 'student (female)', article: 'die', pos: 'noun' },
    { id: 'v20', de: 'Freut mich!', en: 'Nice to meet you!', pos: 'phrase' },
    { id: 'v21', de: 'Wie geht es Ihnen?', en: 'How are you? (formal)', pos: 'phrase' },
    { id: 'v22', de: 'Wie geht’s?', en: "How's it going? (informal)", pos: 'phrase' },
    { id: 'v23', de: 'Danke, gut.', en: 'Thanks, fine.', pos: 'phrase' },
    { id: 'v24', de: 'buchstabieren', en: 'to spell', pos: 'verb', exampleDe: 'Können Sie Ihren Namen buchstabieren?', exampleEn: 'Can you spell your name?' },
    { id: 'v25', de: 'Personalbogen', en: 'personal data form', article: 'der', pos: 'noun' },
    { id: 'v26', de: 'ausfüllen', en: 'to fill out', pos: 'verb' },
    { id: 'v27', de: 'null', en: 'zero', pos: 'other' },
    { id: 'v28', de: 'eins', en: 'one', pos: 'other' },
    { id: 'v29', de: 'zehn', en: 'ten', pos: 'other' },
    { id: 'v30', de: 'hundert', en: 'hundred', pos: 'other' },
    { id: 'v31', de: 'tausend', en: 'thousand', pos: 'other' },
    { id: 'v32', de: 'Million', en: 'million', article: 'die', pos: 'noun' },
    { id: 'v33', de: 'woher', en: 'from where', pos: 'adverb', exampleDe: 'Woher kommen Sie?', exampleEn: 'Where do you come from?' },
    { id: 'v34', de: 'wo', en: 'where', pos: 'adverb', exampleDe: 'Wo wohnen Sie?', exampleEn: 'Where do you live?' },
    { id: 'v35', de: 'wie', en: 'how / what (name)', pos: 'adverb', exampleDe: 'Wie heißen Sie?', exampleEn: 'What is your name?' },
    { id: 'v36', de: 'sein', en: 'to be', pos: 'verb', exampleDe: 'Ich bin Student.', exampleEn: 'I am a student.' },
    { id: 'v37', de: 'Herr', en: 'Mr', article: 'der', pos: 'noun' },
    { id: 'v38', de: 'Frau', en: 'Ms / Mrs / woman', article: 'die', pos: 'noun' },
    { id: 'v39', de: 'Alphabet', en: 'alphabet', article: 'das', pos: 'noun' },
    { id: 'v40', de: 'Nummer', en: 'number', article: 'die', pos: 'noun' },
  ],
  grammar: [
    {
      id: 'g1',
      titleDe: 'Regelmäßige Verben und „sein“ im Präsens',
      titleEn: 'Regular verbs and sein in the present',
      explanationEn:
        'German present tense (Präsens) uses one stem for most persons. Regular verbs add -e, -st, -t, -en, -t, -en. The verb sein (to be) is irregular: ich bin, du bist, er/sie/es ist, wir sind, ihr seid, sie/Sie sind.',
      patterns: [
        'ich wohne / du wohnst / er wohnt / wir wohnen',
        'ich bin / du bist / er ist / wir sind',
        'ich heiße / du heißt / sie heißt',
      ],
      examples: [
        { de: 'Ich heiße Marco.', en: 'My name is Marco.' },
        { de: 'Sie kommt aus Italien.', en: 'She comes from Italy.' },
        { de: 'Wir sind Studenten.', en: 'We are students.' },
      ],
    },
    {
      id: 'g2',
      titleDe: 'Personalpronomen und Wortstellung (Aussage, W-Frage, Ja/Nein-Frage)',
      titleEn: 'Personal pronouns and word order',
      explanationEn:
        'Nominative pronouns: ich, du, er/sie/es, wir, ihr, sie/Sie. In statements the verb is in position 2. W-questions start with Wie/Wo/Woher… then verb. Yes/No questions start with the verb.',
      patterns: [
        'Aussage: Ich komme aus Spanien.',
        'W-Frage: Woher kommen Sie?',
        'Ja/Nein-Frage: Wohnen Sie in Berlin?',
      ],
      examples: [
        { de: 'Wo wohnst du?', en: 'Where do you live?' },
        { de: 'Heißt er Paul?', en: 'Is his name Paul?' },
        { de: 'Ich bin aus Brasilien.', en: 'I am from Brazil.' },
      ],
    },
  ],
  drills: [
    mcDrill('d1', 'Wähle die richtige Form.', 'Choose the correct form.', 'Ich ___ Studentin.', ['bin', 'bist', 'ist', 'sind'], 'bin', 'g1'),
    mcDrill('d2', 'Wähle die richtige Form.', 'Choose the correct form.', 'Woher ___ Sie?', ['komme', 'kommst', 'kommt', 'kommen'], 'kommen', 'g1'),
    clozeDrill('d3', 'Ergänze „sein“.', 'Fill in sein.', 'Du ___ Anna.', 'bist', 'g1'),
    clozeDrill('d4', 'Ergänze das Verb.', 'Fill in the verb.', 'Er ___ in München. (wohnen)', 'wohnt', 'g1'),
    reorderDrill('d5', 'Bringe die Wörter in die richtige Reihenfolge.', 'Put the words in the correct order.', ['kommen', 'Sie', 'Woher', '?'], 'Woher kommen Sie?', 'g2'),
    mcDrill('d6', 'Welche Frage ist korrekt?', 'Which question is correct?', 'Ask formally where someone lives.', ['Wo wohnen Sie?', 'Wo Sie wohnen?', 'Wohnen wo Sie?'], 'Wo wohnen Sie?', 'g2'),
    clozeDrill('d7', 'Ergänze.', 'Fill in.', '___ heißen Sie?', 'Wie', 'g2'),
    mcDrill('d8', 'Wähle die richtige Form.', 'Choose the correct form.', 'Wir ___ aus Deutschland.', ['bin', 'bist', 'ist', 'sind'], 'sind', 'g1'),
  ],
  quiz: [
    { id: 'q1', type: 'vocab-de-en', prompt: 'Was bedeutet „heißen“?', options: ['to be called', 'to live', 'to come', 'to spell'], answer: 'to be called', vocabId: 'v6' },
    { id: 'q2', type: 'vocab-en-de', prompt: 'How do you say “Nice to meet you!” in German?', options: ['Freut mich!', 'Guten Tag!', 'Auf Wiedersehen!', 'Danke, gut.'], answer: 'Freut mich!', vocabId: 'v20' },
    { id: 'q3', type: 'vocab-de-en', prompt: 'Was bedeutet „buchstabieren“?', options: ['to spell', 'to fill out', 'to greet', 'to count'], answer: 'to spell', vocabId: 'v24' },
    { id: 'q4', type: 'grammar-mc', prompt: 'Ich ___ aus Japan. (kommen)', options: ['komme', 'kommst', 'kommt', 'kommen'], answer: 'komme', grammarId: 'g1' },
    { id: 'q5', type: 'grammar-mc', prompt: '___ wohnen Sie?', options: ['Wo', 'Wie', 'Wer', 'Was'], answer: 'Wo', grammarId: 'g2' },
    { id: 'q6', type: 'cloze', prompt: 'Complete: Sie ___ Frau Berger. (sein)', answer: 'ist', grammarId: 'g1' },
    { id: 'q7', type: 'vocab-de-en', prompt: '„die Telefonnummer“ means…', options: ['phone number', 'email address', 'first name', 'form'], answer: 'phone number', vocabId: 'v13' },
    { id: 'q8', type: 'grammar-mc', prompt: 'Correct yes/no question:', options: ['Heißt du Maria?', 'Du heißt Maria?', 'Heißt Maria du?'], answer: 'Heißt du Maria?', grammarId: 'g2' },
    { id: 'q9', type: 'vocab-en-de', prompt: '“internship” in German is…', options: ['das Praktikum', 'der Student', 'die Adresse', 'das Land'], answer: 'das Praktikum', vocabId: 'v17' },
    { id: 'q10', type: 'cloze', prompt: 'Complete: Woher ___ ihr?', answer: 'kommt', grammarId: 'g1' },
  ],
}

// ——— Lektion 2 ———
fullLessons['a1-l02'] = {
  id: 'a1-l02',
  level: 'A1',
  number: 2,
  titleDe: 'Termine, Termine',
  titleEn: 'Appointments, appointments',
  status: 'complete',
  goals: [
    { de: 'Uhrzeiten verstehen und sagen (formell/informell)', en: 'Understand and tell the time (formal/informal)' },
    { de: 'Tageszeiten verstehen und sagen', en: 'Understand and name times of day' },
    { de: 'Über Termine sprechen', en: 'Talk about appointments' },
    { de: 'Kulturangebote verstehen', en: 'Understand cultural event information' },
    { de: 'Verabredungen verstehen', en: 'Understand arrangements to meet' },
    { de: 'Monate, Datum, Jahreszeiten und Jahreszahlen nennen', en: 'Name months, dates, seasons and years' },
    { de: 'Eine Urlaubsmail verstehen und schreiben', en: 'Understand and write a holiday email' },
  ],
  vocab: [
    { id: 'v1', de: 'Termin', en: 'appointment', article: 'der', pos: 'noun' },
    { id: 'v2', de: 'Terminkalender', en: 'appointment calendar', article: 'der', pos: 'noun' },
    { id: 'v3', de: 'Uhrzeit', en: 'time of day (clock time)', article: 'die', pos: 'noun' },
    { id: 'v4', de: 'Stunde', en: 'hour', article: 'die', pos: 'noun' },
    { id: 'v5', de: 'Minute', en: 'minute', article: 'die', pos: 'noun' },
    { id: 'v6', de: 'Vormittag', en: 'morning (before noon)', article: 'der', pos: 'noun' },
    { id: 'v7', de: 'Mittag', en: 'noon / midday', article: 'der', pos: 'noun' },
    { id: 'v8', de: 'Nachmittag', en: 'afternoon', article: 'der', pos: 'noun' },
    { id: 'v9', de: 'Abend', en: 'evening', article: 'der', pos: 'noun' },
    { id: 'v10', de: 'Nacht', en: 'night', article: 'die', pos: 'noun' },
    { id: 'v11', de: 'Montag', en: 'Monday', article: 'der', pos: 'noun' },
    { id: 'v12', de: 'Dienstag', en: 'Tuesday', article: 'der', pos: 'noun' },
    { id: 'v13', de: 'Mittwoch', en: 'Wednesday', article: 'der', pos: 'noun' },
    { id: 'v14', de: 'Donnerstag', en: 'Thursday', article: 'der', pos: 'noun' },
    { id: 'v15', de: 'Freitag', en: 'Friday', article: 'der', pos: 'noun' },
    { id: 'v16', de: 'Samstag', en: 'Saturday', article: 'der', pos: 'noun' },
    { id: 'v17', de: 'Sonntag', en: 'Sunday', article: 'der', pos: 'noun' },
    { id: 'v18', de: 'Januar', en: 'January', article: 'der', pos: 'noun' },
    { id: 'v19', de: 'Frühling', en: 'spring', article: 'der', pos: 'noun' },
    { id: 'v20', de: 'Sommer', en: 'summer', article: 'der', pos: 'noun' },
    { id: 'v21', de: 'Herbst', en: 'autumn / fall', article: 'der', pos: 'noun' },
    { id: 'v22', de: 'Winter', en: 'winter', article: 'der', pos: 'noun' },
    { id: 'v23', de: 'Urlaub', en: 'vacation / holiday', article: 'der', pos: 'noun' },
    { id: 'v24', de: 'Feiertag', en: 'public holiday', article: 'der', pos: 'noun' },
    { id: 'v25', de: 'verabreden', en: 'to arrange to meet', pos: 'verb' },
    { id: 'v26', de: 'treffen', en: 'to meet', pos: 'verb' },
    { id: 'v27', de: 'beginnen', en: 'to begin', pos: 'verb' },
    { id: 'v28', de: 'enden', en: 'to end', pos: 'verb' },
    { id: 'v29', de: 'Wann?', en: 'When?', pos: 'phrase' },
    { id: 'v30', de: 'um acht Uhr', en: 'at eight o’clock', pos: 'phrase' },
    { id: 'v31', de: 'halb neun', en: 'half past eight (8:30)', pos: 'phrase' },
    { id: 'v32', de: 'Viertel nach', en: 'quarter past', pos: 'phrase' },
    { id: 'v33', de: 'Viertel vor', en: 'quarter to', pos: 'phrase' },
    { id: 'v34', de: 'Kino', en: 'cinema', article: 'das', pos: 'noun' },
    { id: 'v35', de: 'Konzert', en: 'concert', article: 'das', pos: 'noun' },
    { id: 'v36', de: 'Theater', en: 'theater', article: 'das', pos: 'noun' },
    { id: 'v37', de: 'nicht', en: 'not', pos: 'adverb' },
    { id: 'v38', de: 'kein', en: 'no / not a', pos: 'other' },
    { id: 'v39', de: 'Datum', en: 'date', article: 'das', pos: 'noun' },
    { id: 'v40', de: 'freihaben', en: 'to have time off', pos: 'verb' },
  ],
  grammar: [
    {
      id: 'g1',
      titleDe: 'Verneinung: „nicht“ und „kein-“',
      titleEn: 'Negation with nicht and kein-',
      explanationEn:
        'Use kein- before a noun without a definite article (kein Termin, keine Zeit). Use nicht to negate verbs, adjectives, adverbs, or a whole clause (Ich habe nicht Zeit → better: Ich habe keine Zeit; Der Film beginnt nicht um acht).',
      patterns: ['kein / keine / keinen + Nomen', 'Verb … nicht', 'Ich habe keinen Termin.'],
      examples: [
        { de: 'Ich habe keinen Termin.', en: 'I do not have an appointment.' },
        { de: 'Das Konzert beginnt nicht um sieben.', en: 'The concert does not start at seven.' },
        { de: 'Am Sonntag habe ich keine Zeit.', en: 'I have no time on Sunday.' },
      ],
    },
    {
      id: 'g2',
      titleDe: 'Bestimmter und unbestimmter Artikel (Nom./Akk.)',
      titleEn: 'Definite and indefinite articles (nom./acc.)',
      explanationEn:
        'Nominative: der/die/das, ein/eine/ein. Accusative changes only masculine: den / einen. Feminine and neuter stay die/eine and das/ein.',
      patterns: ['Nom.: der Termin, ein Konzert', 'Akk.: Ich habe den Termin. / einen Termin.'],
      examples: [
        { de: 'Der Termin ist am Montag.', en: 'The appointment is on Monday.' },
        { de: 'Ich brauche einen Terminkalender.', en: 'I need an appointment calendar.' },
      ],
    },
  ],
  drills: [
    mcDrill('d1', 'Wähle die Verneinung.', 'Choose the negation.', 'Ich habe ___ Termin.', ['kein', 'keinen', 'keine', 'nicht'], 'keinen', 'g1'),
    clozeDrill('d2', 'Ergänze „nicht“ oder „kein-“.', 'Fill in nicht or kein-.', 'Der Film beginnt ___ um acht.', 'nicht', 'g1'),
    mcDrill('d3', 'Akkusativ wählen.', 'Choose accusative.', 'Ich treffe ___ Freund.', ['der', 'den', 'dem', 'des'], 'den', 'g2'),
    reorderDrill('d4', 'Satz ordnen.', 'Order the sentence.', ['habe', 'keine', 'Ich', 'Zeit', '.'], 'Ich habe keine Zeit.', 'g1'),
    clozeDrill('d5', 'Artikel.', 'Article.', '___ Konzert ist am Freitag. (das)', 'Das', 'g2'),
    mcDrill('d6', 'Wann?', 'When?', '„halb zehn“ means…', ['9:30', '10:30', '10:00', '9:00'], '9:30', 'g1'),
  ],
  quiz: [
    { id: 'q1', type: 'vocab-de-en', prompt: '„der Termin“ means…', options: ['appointment', 'calendar', 'holiday', 'evening'], answer: 'appointment', vocabId: 'v1' },
    { id: 'q2', type: 'vocab-en-de', prompt: '“afternoon” in German:', options: ['der Nachmittag', 'der Vormittag', 'die Nacht', 'der Mittag'], answer: 'der Nachmittag', vocabId: 'v8' },
    { id: 'q3', type: 'grammar-mc', prompt: 'Ich habe ___ Zeit.', options: ['keine', 'keinen', 'kein', 'nicht'], answer: 'keine', grammarId: 'g1' },
    { id: 'q4', type: 'cloze', prompt: 'Complete: Wir treffen ___ Freunde. (die)', answer: 'die', grammarId: 'g2' },
    { id: 'q5', type: 'vocab-de-en', prompt: '„der Feiertag“ means…', options: ['public holiday', 'vacation', 'appointment', 'concert'], answer: 'public holiday', vocabId: 'v24' },
    { id: 'q6', type: 'grammar-mc', prompt: 'Negate correctly: Ich ___ am Montag ___ Termin.', options: ['habe / keinen', 'habe / nicht', 'bin / kein', 'habe / keine'], answer: 'habe / keinen', grammarId: 'g1' },
    { id: 'q7', type: 'vocab-en-de', prompt: '“cinema”:', options: ['das Kino', 'das Theater', 'das Konzert', 'der Urlaub'], answer: 'das Kino', vocabId: 'v34' },
    { id: 'q8', type: 'cloze', prompt: 'Complete: Am ___ habe ich frei. (Sonntag)', answer: 'Sonntag', vocabId: 'v17' },
    { id: 'q9', type: 'vocab-de-en', prompt: '„verabreden“ means…', options: ['to arrange to meet', 'to begin', 'to end', 'to travel'], answer: 'to arrange to meet', vocabId: 'v25' },
    { id: 'q10', type: 'grammar-mc', prompt: 'Masculine accusative of „ein“:', options: ['einen', 'einem', 'eines', 'eine'], answer: 'einen', grammarId: 'g2' },
  ],
}

function writeLesson(lesson) {
  fs.writeFileSync(path.join(outDir, `${lesson.id}.json`), JSON.stringify(lesson, null, 2) + '\n')
}

// Continue with L3-L8 in a second write by importing from another file — keep this file manageable
// by defining them below.

fullLessons['a1-l03'] = {
  id: 'a1-l03', level: 'A1', number: 3, titleDe: 'Unternehmen Familie', titleEn: 'Family enterprise', status: 'complete',
  goals: [
    { de: 'Aufgaben im Haushalt verstehen', en: 'Understand household tasks' },
    { de: 'Sich austauschen, was man kann, muss und möchte', en: 'Talk about what you can, must and would like to do' },
    { de: 'Lebensmittel, Mengen und Verpackungen verstehen', en: 'Understand food, quantities and packaging' },
    { de: 'Preise verstehen und sagen', en: 'Understand and say prices' },
    { de: 'Einkaufszettel schreiben', en: 'Write a shopping list' },
    { de: 'Über die Familie und Berufe sprechen', en: 'Talk about family and jobs' },
  ],
  vocab: [
    { id: 'v1', de: 'Familie', en: 'family', article: 'die', pos: 'noun' },
    { id: 'v2', de: 'Mutter', en: 'mother', article: 'die', pos: 'noun' },
    { id: 'v3', de: 'Vater', en: 'father', article: 'der', pos: 'noun' },
    { id: 'v4', de: 'Geschwister', en: 'siblings', pos: 'noun' },
    { id: 'v5', de: 'Bruder', en: 'brother', article: 'der', pos: 'noun' },
    { id: 'v6', de: 'Schwester', en: 'sister', article: 'die', pos: 'noun' },
    { id: 'v7', de: 'kochen', en: 'to cook', pos: 'verb' },
    { id: 'v8', de: 'einkaufen', en: 'to shop / buy groceries', pos: 'verb' },
    { id: 'v9', de: 'aufräumen', en: 'to tidy up', pos: 'verb' },
    { id: 'v10', de: 'waschen', en: 'to wash', pos: 'verb' },
    { id: 'v11', de: 'Supermarkt', en: 'supermarket', article: 'der', pos: 'noun' },
    { id: 'v12', de: 'Lebensmittel', en: 'groceries / foodstuffs', pos: 'noun' },
    { id: 'v13', de: 'Brot', en: 'bread', article: 'das', pos: 'noun' },
    { id: 'v14', de: 'Milch', en: 'milk', article: 'die', pos: 'noun' },
    { id: 'v15', de: 'Käse', en: 'cheese', article: 'der', pos: 'noun' },
    { id: 'v16', de: 'Obst', en: 'fruit', article: 'das', pos: 'noun' },
    { id: 'v17', de: 'Gemüse', en: 'vegetables', article: 'das', pos: 'noun' },
    { id: 'v18', de: 'Preis', en: 'price', article: 'der', pos: 'noun' },
    { id: 'v19', de: 'Euro', en: 'euro', article: 'der', pos: 'noun' },
    { id: 'v20', de: 'kosten', en: 'to cost', pos: 'verb' },
    { id: 'v21', de: 'können', en: 'can / to be able to', pos: 'verb' },
    { id: 'v22', de: 'müssen', en: 'must / to have to', pos: 'verb' },
    { id: 'v23', de: 'möchten', en: 'would like to', pos: 'verb' },
    { id: 'v24', de: 'Beruf', en: 'profession / job', article: 'der', pos: 'noun' },
    { id: 'v25', de: 'Au-pair', en: 'au pair', article: 'das', pos: 'noun' },
    { id: 'v26', de: 'Hausarbeit', en: 'housework', article: 'die', pos: 'noun' },
    { id: 'v27', de: 'Einkaufszettel', en: 'shopping list', article: 'der', pos: 'noun' },
    { id: 'v28', de: 'Packung', en: 'pack / package', article: 'die', pos: 'noun' },
    { id: 'v29', de: 'Kilo', en: 'kilo', article: 'das', pos: 'noun' },
    { id: 'v30', de: 'Liter', en: 'liter', article: 'der', pos: 'noun' },
    { id: 'v31', de: 'wie viel', en: 'how much', pos: 'phrase' },
    { id: 'v32', de: 'wie viele', en: 'how many', pos: 'phrase' },
    { id: 'v33', de: 'helfen', en: 'to help', pos: 'verb' },
    { id: 'v34', de: 'brauchen', en: 'to need', pos: 'verb' },
    { id: 'v35', de: 'mein', en: 'my', pos: 'other' },
    { id: 'v36', de: 'dein', en: 'your (informal)', pos: 'other' },
    { id: 'v37', de: 'und', en: 'and', pos: 'other' },
    { id: 'v38', de: 'noch', en: 'still / another', pos: 'adverb' },
    { id: 'v39', de: 'kein … mehr', en: 'no more / not any more', pos: 'phrase' },
    { id: 'v40', de: 'Familie', en: 'family', article: 'die', pos: 'noun', tags: ['repeat'] },
  ],
  grammar: [
    {
      id: 'g1',
      titleDe: 'Modalverben: können, müssen, möcht-',
      titleEn: 'Modal verbs: können, müssen, möchten',
      explanationEn:
        'Modal verbs are conjugated and the main verb stays in the infinitive at the end: Ich kann kochen. Ich muss einkaufen. Ich möchte helfen.',
      patterns: ['ich kann / du kannst / er kann', 'ich muss / du musst / er muss', 'ich möchte / du möchtest'],
      examples: [
        { de: 'Kannst du kochen?', en: 'Can you cook?' },
        { de: 'Ich muss heute aufräumen.', en: 'I have to tidy up today.' },
        { de: 'Wir möchten Käse kaufen.', en: 'We would like to buy cheese.' },
      ],
    },
    {
      id: 'g2',
      titleDe: 'Possessivartikel im Nominativ; W-Fragen mit Wie viel/Wie viele',
      titleEn: 'Possessive articles; How much / How many',
      explanationEn:
        'mein/dein/sein/ihr/unser… agree with the noun: mein Bruder, meine Schwester, mein Brot. Wie viel? for uncountable; Wie viele? for countable plurals.',
      patterns: ['mein Vater / meine Mutter', 'Wie viel kostet …?', 'Wie viele Äpfel?'],
      examples: [
        { de: 'Das ist meine Familie.', en: 'That is my family.' },
        { de: 'Wie viel kostet das Brot?', en: 'How much does the bread cost?' },
      ],
    },
  ],
  drills: [
    mcDrill('d1', 'Modalverb.', 'Modal verb.', 'Ich ___ heute kochen.', ['kann', 'kannst', 'können', 'könnt'], 'kann', 'g1'),
    clozeDrill('d2', 'Infinitiv ans Ende.', 'Infinitive at the end.', 'Sie muss Milch ___. (kaufen)', 'kaufen', 'g1'),
    mcDrill('d3', 'Possessiv.', 'Possessive.', '___ Schwester heißt Lea. (mein)', ['Mein', 'Meine', 'Meinen', 'Meinem'], 'Meine', 'g2'),
    clozeDrill('d4', 'Wie viel / Wie viele', 'How much / How many', '___ Liter Milch brauchst du?', 'Wie viel', 'g2'),
    reorderDrill('d5', 'Satz ordnen.', 'Order.', ['möchte', 'Ich', 'helfen', '.'], 'Ich möchte helfen.', 'g1'),
    mcDrill('d6', 'Preis.', 'Price.', 'Das Brot kostet zwei ___.', ['Euro', 'Liter', 'Kilo', 'Packung'], 'Euro', 'g2'),
  ],
  quiz: [
    { id: 'q1', type: 'vocab-de-en', prompt: '„einkaufen“ means…', options: ['to shop', 'to cook', 'to wash', 'to help'], answer: 'to shop', vocabId: 'v8' },
    { id: 'q2', type: 'grammar-mc', prompt: 'Du ___ aufräumen.', options: ['musst', 'muss', 'müssen', 'möchte'], answer: 'musst', grammarId: 'g1' },
    { id: 'q3', type: 'vocab-en-de', prompt: '“cheese”:', options: ['der Käse', 'die Milch', 'das Brot', 'das Obst'], answer: 'der Käse', vocabId: 'v15' },
    { id: 'q4', type: 'cloze', prompt: 'Complete: Wir ___ Gemüse kaufen. (möchten)', answer: 'möchten', grammarId: 'g1' },
    { id: 'q5', type: 'vocab-de-en', prompt: '„der Einkaufszettel“ means…', options: ['shopping list', 'supermarket', 'price', 'family'], answer: 'shopping list', vocabId: 'v27' },
    { id: 'q6', type: 'grammar-mc', prompt: '___ Äpfel möchtest du?', options: ['Wie viele', 'Wie viel', 'Was', 'Wo'], answer: 'Wie viele', grammarId: 'g2' },
    { id: 'q7', type: 'vocab-en-de', prompt: '“housework”:', options: ['die Hausarbeit', 'die Familie', 'der Beruf', 'das Au-pair'], answer: 'die Hausarbeit', vocabId: 'v26' },
    { id: 'q8', type: 'cloze', prompt: 'Complete: Das ist ___ Vater. (mein)', answer: 'mein', grammarId: 'g2' },
    { id: 'q9', type: 'grammar-mc', prompt: 'Correct word order:', options: ['Ich kann gut kochen.', 'Ich gut kann kochen.', 'Kann ich kochen gut.'], answer: 'Ich kann gut kochen.', grammarId: 'g1' },
    { id: 'q10', type: 'vocab-de-en', prompt: '„müssen“ means…', options: ['must / have to', 'can', 'would like', 'need'], answer: 'must / have to', vocabId: 'v22' },
  ],
}

console.log('Writing base lessons L1–L3…')
for (const m of meta) {
  if (fullLessons[m.id]) {
    writeLesson(fullLessons[m.id])
  } else {
    const gkey = m.level === 'A1' ? 'a1' : m.level === 'A2' ? 'a2' : 'b1'
    writeLesson(emptyLesson(m, stubGoals[gkey]))
  }
}

const index = {
  book: 'DaF kompakt A1–B1 Kursbuch',
  languagePair: 'de-en',
  lessons: meta.map((m, i) => ({
    id: m.id,
    level: m.level,
    number: m.number,
    titleDe: m.titleDe,
    titleEn: m.titleEn,
    status: fullLessons[m.id] ? 'complete' : 'stub',
    order: i + 1,
  })),
}
fs.writeFileSync(indexPath, JSON.stringify(index, null, 2) + '\n')
console.log('Wrote index + shells. Full L1–L3 done in this pass.')
