/** Lightweight Präsens conjugator for practice drills. */

export type Person = 'ich' | 'du' | 'er' | 'wir' | 'ihr' | 'Sie'

const PERSONS: Person[] = ['ich', 'du', 'er', 'wir', 'ihr', 'Sie']

const IRREGULAR: Record<string, Partial<Record<Person, string>> & { stem?: string }> = {
  sein: { ich: 'bin', du: 'bist', er: 'ist', wir: 'sind', ihr: 'seid', Sie: 'sind' },
  haben: { ich: 'habe', du: 'hast', er: 'hat', wir: 'haben', ihr: 'habt', Sie: 'haben' },
  werden: { ich: 'werde', du: 'wirst', er: 'wird', wir: 'werden', ihr: 'werdet', Sie: 'werden' },
  können: { ich: 'kann', du: 'kannst', er: 'kann', wir: 'können', ihr: 'könnt', Sie: 'können' },
  müssen: { ich: 'muss', du: 'musst', er: 'muss', wir: 'müssen', ihr: 'müsst', Sie: 'müssen' },
  wollen: { ich: 'will', du: 'willst', er: 'will', wir: 'wollen', ihr: 'wollt', Sie: 'wollen' },
  dürfen: { ich: 'darf', du: 'darfst', er: 'darf', wir: 'dürfen', ihr: 'dürft', Sie: 'dürfen' },
  sollen: { ich: 'soll', du: 'sollst', er: 'soll', wir: 'sollen', ihr: 'sollt', Sie: 'sollen' },
  mögen: { ich: 'mag', du: 'magst', er: 'mag', wir: 'mögen', ihr: 'mögt', Sie: 'mögen' },
  wissen: { ich: 'weiß', du: 'weißt', er: 'weiß', wir: 'wissen', ihr: 'wisst', Sie: 'wissen' },
  gehen: { ich: 'gehe', du: 'gehst', er: 'geht', wir: 'gehen', ihr: 'geht', Sie: 'gehen' },
  kommen: { ich: 'komme', du: 'kommst', er: 'kommt', wir: 'kommen', ihr: 'kommt', Sie: 'kommen' },
  sprechen: { ich: 'spreche', du: 'sprichst', er: 'spricht', wir: 'sprechen', ihr: 'sprecht', Sie: 'sprechen' },
  lesen: { ich: 'lese', du: 'liest', er: 'liest', wir: 'lesen', ihr: 'lest', Sie: 'lesen' },
  fahren: { ich: 'fahre', du: 'fährst', er: 'fährt', wir: 'fahren', ihr: 'fahrt', Sie: 'fahren' },
  schlafen: { ich: 'schlafe', du: 'schläfst', er: 'schläft', wir: 'schlafen', ihr: 'schlaft', Sie: 'schlafen' },
  nehmen: { ich: 'nehme', du: 'nimmst', er: 'nimmt', wir: 'nehmen', ihr: 'nehmt', Sie: 'nehmen' },
  geben: { ich: 'gebe', du: 'gibst', er: 'gibt', wir: 'geben', ihr: 'gebt', Sie: 'geben' },
  sehen: { ich: 'sehe', du: 'siehst', er: 'sieht', wir: 'sehen', ihr: 'seht', Sie: 'sehen' },
  essen: { ich: 'esse', du: 'isst', er: 'isst', wir: 'essen', ihr: 'esst', Sie: 'essen' },
  helfen: { ich: 'helfe', du: 'hilfst', er: 'hilft', wir: 'helfen', ihr: 'helft', Sie: 'helfen' },
  laufen: { ich: 'laufe', du: 'läufst', er: 'läuft', wir: 'laufen', ihr: 'lauft', Sie: 'laufen' },
  heißen: { ich: 'heiße', du: 'heißt', er: 'heißt', wir: 'heißen', ihr: 'heißt', Sie: 'heißen' },
  wohnen: {},
  lernen: {},
  machen: {},
  spielen: {},
  arbeiten: {},
  suchen: {},
  kaufen: {},
  brauchen: {},
  fragen: {},
  sagen: {},
  hören: {},
  öffnen: { ich: 'öffne', du: 'öffnest', er: 'öffnet', wir: 'öffnen', ihr: 'öffnet', Sie: 'öffnen' },
  finden: {},
  bleiben: { ich: 'bleibe', du: 'bleibst', er: 'bleibt', wir: 'bleiben', ihr: 'bleibt', Sie: 'bleiben' },
}

function regularPresent(infinitive: string, person: Person): string | null {
  if (!infinitive.endsWith('en') && !infinitive.endsWith('n')) return null
  let stem = infinitive.endsWith('en') ? infinitive.slice(0, -2) : infinitive.slice(0, -1)
  // -eln / -ern handled lightly
  const needsE = /[td]$/.test(stem) || /[mn]$/.test(stem)
  switch (person) {
    case 'ich':
      return stem + 'e'
    case 'du':
      return stem + (needsE ? 'est' : 'st')
    case 'er':
      return stem + (needsE ? 'et' : 't')
    case 'wir':
      return infinitive
    case 'ihr':
      return stem + (needsE ? 'et' : 't')
    case 'Sie':
      return infinitive
  }
}

export function conjugatePresent(infinitive: string, person: Person): string | null {
  const key = infinitive.toLowerCase().trim()
  const irr = IRREGULAR[key]
  if (irr && irr[person]) return irr[person]!
  if (irr) return regularPresent(key, person)
  return regularPresent(key, person)
}

export function canConjugate(infinitive: string): boolean {
  const key = infinitive.toLowerCase().trim()
  if (IRREGULAR[key]) return true
  return /en$/.test(key) && !key.includes(' ')
}

export function pickPerson(): Person {
  return PERSONS[Math.floor(Math.random() * PERSONS.length)]!
}

export function extractInfinitive(de: string): string {
  // "sich freuen" → freuen for display we keep sich; conjugator uses base
  return de.replace(/^sich\s+/, '').split(/[/(]/)[0]!.trim()
}

export { PERSONS }
