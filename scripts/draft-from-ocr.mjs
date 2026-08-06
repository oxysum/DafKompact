#!/usr/bin/env node
/**
 * Draft lesson JSON from OCR PDF page ranges (personal study helper).
 *
 * Usage:
 *   node scripts/draft-from-ocr.mjs --pdf "../DaF-kompakt-A1-B1-KB-ocr.pdf" --from 10 --to 19 --id a1-l01
 *
 * Requires: npm i -D pdf-parse  (or pass --text file.txt with pre-extracted text)
 * Without pdf-parse, use --text to supply extracted OCR text.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.join(__dirname, '..')

function arg(name, fallback) {
  const i = process.argv.indexOf(name)
  if (i === -1) return fallback
  return process.argv[i + 1]
}

const pdfPath = arg('--pdf', path.join(root, '..', 'DaF-kompakt-A1-B1-KB-ocr.pdf'))
const textPath = arg('--text', null)
const fromPage = Number(arg('--from', '1'))
const toPage = Number(arg('--to', String(fromPage)))
const lessonId = arg('--id', 'draft-lesson')
const outPath = arg(
  '--out',
  path.join(root, 'public', 'content', 'lektionen', `${lessonId}.draft.json`),
)

function splitPages(raw) {
  // Vite/Read tool style markers: "-- N of M --"
  const parts = raw.split(/\n--\s*\d+\s+of\s+\d+\s*--\n/)
  return parts
}

function extractBulletGoals(text) {
  const lines = text.split(/\n/)
  const goals = []
  for (const line of lines) {
    const m = line.match(/^[•·\-*]\s*(.+)$/)
    if (m) {
      const de = m[1].replace(/\s+/g, ' ').trim()
      if (de.length > 8 && de.length < 180) {
        goals.push({ de, en: '[TODO: English translation]' })
      }
    }
  }
  return goals.slice(0, 12)
}

function extractCandidateVocab(text) {
  const words = new Set()
  const re = /\b([A-ZÄÖÜ][a-zäöüß]{2,})\b/g
  let m
  while ((m = re.exec(text))) {
    words.add(m[1])
  }
  return [...words].slice(0, 40).map((de, i) => ({
    id: `v${i + 1}`,
    de,
    en: '[TODO]',
    pos: 'other',
  }))
}

async function loadText() {
  if (textPath) {
    return fs.readFileSync(textPath, 'utf8')
  }
  try {
    const { default: pdfParse } = await import('pdf-parse')
    const data = await pdfParse(fs.readFileSync(pdfPath))
    return data.text
  } catch {
    console.error(
      'Could not parse PDF. Install pdf-parse (`npm i -D pdf-parse`) or pass --text extracted.txt',
    )
    console.error('PDF path:', pdfPath)
    process.exit(1)
  }
}

const raw = await loadText()
const pages = splitPages(raw)
// pages[0] may be pre-first marker; page 1 ≈ index 1 if markers present
const slice = pages.slice(fromPage, toPage + 1).join('\n\n')
const chunk = slice || raw

const draft = {
  id: lessonId,
  level: lessonId.startsWith('a2') ? 'A2' : lessonId.startsWith('b1') ? 'B1' : 'A1',
  number: Number(lessonId.match(/l(\d+)/)?.[1] ?? 0),
  titleDe: '[TODO title]',
  titleEn: '[TODO title]',
  status: 'stub',
  goals: extractBulletGoals(chunk),
  vocab: extractCandidateVocab(chunk),
  grammar: [],
  drills: [],
  quiz: [],
  _meta: {
    source: textPath || pdfPath,
    pages: `${fromPage}-${toPage}`,
    note: 'Auto-draft from OCR. Clean OCR errors, add English, grammar, drills, quiz manually.',
  },
}

fs.mkdirSync(path.dirname(outPath), { recursive: true })
fs.writeFileSync(outPath, JSON.stringify(draft, null, 2) + '\n')
console.log('Wrote draft:', outPath)
console.log(`Goals: ${draft.goals.length}, vocab candidates: ${draft.vocab.length}`)
