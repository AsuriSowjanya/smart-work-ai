import { useState } from 'react'
import { generatePlan } from '../api'
import type { PlanResponse } from '../types'

interface Props {
  onPlanGenerated: (plan: PlanResponse) => void
}

const PLACEHOLDER = `I have an exam tomorrow. I need to study DBMS for 2 hours and Java for 1 hour. I'm free from 5 PM to 10 PM.`

export default function Planner({ onPlanGenerated }: Props) {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setError(null)
    try {
      const plan = await generatePlan(prompt)
      onPlanGenerated(plan)
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ??
          'Could not generate a plan. Check that the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screen">
      <header className="screen-header">
        <p className="eyebrow">AI Smart Planner</p>
        <h1>Tell it what you need to accomplish</h1>
      </header>

      <textarea
        className="planner-input"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder={PLACEHOLDER}
        rows={6}
      />

      {error && <div className="error-banner">{error}</div>}

      <button className="btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating…' : 'Generate plan'}
      </button>
    </div>
  )
}
