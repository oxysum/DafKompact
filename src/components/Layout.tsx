import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useProgress } from '../context/ProgressContext'

export function Layout({ children }: { children: ReactNode }) {
  const { due } = useProgress()
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          DaF <span>kompakt</span>
        </Link>
        <nav className="nav-links">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Lessons
          </NavLink>
          <NavLink to="/review" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Review{due.length > 0 ? ` (${due.length})` : ''}
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Settings
          </NavLink>
        </nav>
      </header>
      {children}
    </div>
  )
}
