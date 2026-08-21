import { useState } from 'react'
import { reschedule } from '../api'
import type { PlanResponse, ScheduleBlock } from '../types'

interface Props {
  plan: PlanResponse
  onPlanUpdated: (plan: PlanResponse) => void
}

function currentTimeHHMM() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(
    now.getMinutes(),
  ).padStart(2, '0')}`
}

export default function Schedule({ plan, onPlanUpdated }: Props) {
  const [loadingBlock, setLoadingBlock] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleReschedule = async (block: ScheduleBlock) => {
    setLoadingBlock(block.task)
    setError(null)
    try {
      const index = plan.schedule.findIndex((b) => b === block)
      const remaining = plan.schedule.slice(index + 1)
      const newSchedule = await reschedule(block.task, remaining, currentTimeHHMM())
      const updatedSchedule = [...plan.schedule.slice(0, index), ...newSchedule]
      onPlanUpdated({ ...plan, schedule: updatedSchedule })
    } catch (e: any) {
      setError(
        e?.response?.data?.detail ?? 'Could not reschedule. Try again.',
      )
    } finally {
      setLoadingBlock(null)
    }
  }

  return (
    <div className="screen">
      <header className="screen-header">
        <p className="eyebrow">Your smart schedule</p>
        <h1>Today's timeline</h1>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="timeline">
        {plan.schedule.map((block, i) => (
          <div key={i} className={`timeline-block ${block.type}`}>
            <div className="timeline-time">
              <span>{block.start}</span>
              <span className="timeline-time-end">{block.end}</span>
            </div>
            <div className="timeline-card">
              <span className="timeline-task-name">
                {block.type === 'break' ? '☕ ' : '📘 '}
                {block.task}
              </span>
              {block.type === 'task' && (
                <button
                  className="btn-tiny"
                  onClick={() => handleReschedule(block)}
                  disabled={loadingBlock === block.task}
                >
                  {loadingBlock === block.task ? 'Rescheduling…' : '🔄 Reschedule'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
