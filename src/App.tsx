import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ProgressProvider } from './context/ProgressContext'
import { HomePage } from './pages/HomePage'
import { LessonHubPage } from './pages/LessonHubPage'
import { GoalsPage } from './pages/GoalsPage'
import { VocabPage } from './pages/VocabPage'
import { GrammarPage } from './pages/GrammarPage'
import { QuizPage } from './pages/QuizPage'
import { ListeningPage } from './pages/ListeningPage'
import { ReviewPage } from './pages/ReviewPage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  return (
    <ProgressProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/lesson/:lessonId" element={<LessonHubPage />} />
          <Route path="/lesson/:lessonId/goals" element={<GoalsPage />} />
          <Route path="/lesson/:lessonId/vocab" element={<VocabPage />} />
          <Route path="/lesson/:lessonId/grammar" element={<GrammarPage />} />
          <Route path="/lesson/:lessonId/quiz" element={<QuizPage />} />
          <Route path="/lesson/:lessonId/listening" element={<ListeningPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </BrowserRouter>
    </ProgressProvider>
  )
}
