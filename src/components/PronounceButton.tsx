import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type MouseEvent,
} from 'react'

type Props = {
  src: string
  label?: string
}

export function PronounceButton({ src, label = 'Play pronunciation' }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [playing, setPlaying] = useState(false)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    return () => {
      const a = audioRef.current
      if (a) {
        a.pause()
        audioRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    const a = audioRef.current
    if (a) {
      a.pause()
      audioRef.current = null
      setPlaying(false)
    }
    setFailed(false)
  }, [src])

  function toggle(e: MouseEvent | KeyboardEvent) {
    e.stopPropagation()
    e.preventDefault()

    let a = audioRef.current
    if (a && playing) {
      a.pause()
      a.currentTime = 0
      setPlaying(false)
      return
    }

    if (!a) {
      a = new Audio(src)
      audioRef.current = a
      a.addEventListener('ended', () => setPlaying(false))
      a.addEventListener('error', () => {
        setPlaying(false)
        setFailed(true)
      })
    }

    void a.play().then(
      () => setPlaying(true),
      () => {
        setPlaying(false)
        setFailed(true)
      },
    )
  }

  if (failed) return null

  return (
    <button
      type="button"
      className={`pronounce-btn${playing ? ' playing' : ''}`}
      aria-label={label}
      title={label}
      onClick={toggle}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') toggle(e)
      }}
    >
      <svg
        width="22"
        height="22"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <path d="M11 5L6 9H3v6h3l5 4V5z" fill="currentColor" />
        <path
          d="M15.5 8.5a5 5 0 010 7"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M18 6a8.5 8.5 0 010 12"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
      </svg>
    </button>
  )
}
