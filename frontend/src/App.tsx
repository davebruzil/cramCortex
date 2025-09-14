import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Home } from './pages/Home'
import { AnalysisResults } from './pages/AnalysisResults'
import { QuestionPracticeView } from './pages/QuestionPracticeView'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<AnalysisResults />} />
        <Route path="/practice/:questionType" element={<QuestionPracticeView />} />
      </Routes>
    </Router>
  )
}

export default App
