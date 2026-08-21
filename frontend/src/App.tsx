import { useState } from 'react'
import type { PlanResponse } from './types'
import Dashboard from './components/Dashboard'
import Planner from './components/Planner'
import Schedule from './components/Schedule'

type View = 'dashboard' | 'planner' | 'schedule'

function App() {
  const [view, setView] = useState<View>('dashboard')
  const [plan, setPlan] = useState<PlanResponse | null>(null)

  const handlePlanGenerated = (newPlan: PlanResponse) => {
    setPlan(newPlan)
    setView('schedule')
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">SW</span>
          <span className="brand-name">SmartWork AI</span>
        </div>
        <nav className="nav">
          <button
            className={view === 'dashboard' ? 'nav-item active' : 'nav-item'}
            onClick={() => setView('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={view === 'planner' ? 'nav-item active' : 'nav-item'}
            onClick={() => setView('planner')}
          >
            AI Planner
          </button>
          <button
            className={view === 'schedule' ? 'nav-item active' : 'nav-item'}
            onClick={() => setView('schedule')}
            disabled={!plan}
          >
            Schedule
          </button>
        </nav>
      </aside>

      <main className="main">
        {view === 'dashboard' && (
        
          <Dashboard
  plan={plan}
  onPlanUpdated={setPlan}
  onGoToPlanner={() => setView('planner')}
/>
        )}
        {view === 'planner' && <Planner onPlanGenerated={handlePlanGenerated} />}
        {view === 'schedule' && plan && (
          <Schedule plan={plan} onPlanUpdated={setPlan} />
        )}
      </main>
    </div>
  )
}

export default App
