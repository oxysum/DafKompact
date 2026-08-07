import type { HelperLanguage } from './settings'

/** Pick helper gloss; fall back to English when Farsi is missing. */
export function pickGloss(
  en: string | undefined | null,
  fa: string | undefined | null,
  lang: HelperLanguage,
): string {
  if (lang === 'fa' && fa?.trim()) return fa.trim()
  return (en ?? '').trim()
}

export function helperLabel(lang: HelperLanguage): string {
  return lang === 'fa' ? 'فارسی' : 'English'
}

export function isRtl(lang: HelperLanguage): boolean {
  return lang === 'fa'
}
