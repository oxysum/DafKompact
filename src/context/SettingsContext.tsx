import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  defaultSettings,
  loadSettings,
  saveSettings,
  type AppSettings,
  type HelperLanguage,
} from '../lib/settings'

interface SettingsContextValue {
  settings: AppSettings
  ready: boolean
  helperLanguage: HelperLanguage
  unlockAll: boolean
  setHelperLanguage: (lang: HelperLanguage) => void
  setUnlockAll: (value: boolean) => void
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setSettings(loadSettings())
    setReady(true)
  }, [])

  useEffect(() => {
    if (!ready) return
    saveSettings(settings)
  }, [settings, ready])

  const setHelperLanguage = useCallback((lang: HelperLanguage) => {
    setSettings((s) => ({ ...s, helperLanguage: lang }))
  }, [])

  const setUnlockAll = useCallback((value: boolean) => {
    setSettings((s) => ({ ...s, unlockAll: value }))
  }, [])

  const value = useMemo(
    () => ({
      settings,
      ready,
      helperLanguage: settings.helperLanguage,
      unlockAll: settings.unlockAll,
      setHelperLanguage,
      setUnlockAll,
    }),
    [settings, ready, setHelperLanguage, setUnlockAll],
  )

  return (
    <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>
  )
}

export function useSettings() {
  const ctx = useContext(SettingsContext)
  if (!ctx) throw new Error('useSettings outside provider')
  return ctx
}
