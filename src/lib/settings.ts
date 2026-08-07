export type HelperLanguage = 'en' | 'fa'

const KEY = 'daf-kompakt-settings-v1'

export interface AppSettings {
  helperLanguage: HelperLanguage
  /** When true, all lessons and lesson steps are open (no quiz unlock path). */
  unlockAll: boolean
}

export function defaultSettings(): AppSettings {
  return { helperLanguage: 'en', unlockAll: false }
}

export function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return defaultSettings()
    const parsed = JSON.parse(raw) as Partial<AppSettings>
    const lang = parsed.helperLanguage
    return {
      helperLanguage: lang === 'fa' ? 'fa' : 'en',
      unlockAll: Boolean(parsed.unlockAll),
    }
  } catch {
    return defaultSettings()
  }
}

export function saveSettings(settings: AppSettings): void {
  localStorage.setItem(KEY, JSON.stringify(settings))
}
