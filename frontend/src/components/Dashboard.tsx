import { useEffect, useState } from 'react'
import type { PlanResponse } from '../types'
import { completeTask, deleteTask, predictProductivity } from '../api'

interface Props {
  plan: PlanResponse | null
  onPlanUpdated: (plan: PlanResponse) => void
  onGoToPlanner: () => void
}

export default function Dashboard({
  plan,
  onPlanUpdated,
  onGoToPlanner,
}: Props) {
  const tasks = plan?.tasks ?? []

  const [prediction, setPrediction] = useState<number | null>(null)
  const [predictionLoading, setPredictionLoading] = useState(false)

  const completed = tasks.filter((t) => t.completed).length

  const rate = tasks.length
    ? Math.round((completed / tasks.length) * 100)
    : 0
  useEffect(() => {
  if (tasks.length === 0) {
    setPrediction(null)
    return
  }

  const predict = async () => {
    try {
      setPredictionLoading(true)

      const firstTask = tasks[0]

      const hour = firstTask.start
        ? parseInt(firstTask.start.split(':')[0], 10)
        : 17

      const result = await predictProductivity({
        day_of_week: new Date().toLocaleDateString('en-US', {
          weekday: 'long',
        }),
        hour: hour,
        task_duration: firstTask.duration,
        difficulty:
          firstTask.priority === 'HIGH'
            ? 3
            : firstTask.priority === 'MEDIUM'
              ? 2
              : 1,
        previous_completion_rate: rate,
        category: firstTask.title,
      })

      setPrediction(Math.round(result.predicted_productivity))
    } catch (error) {
      console.error('Failed to predict productivity:', error)
    } finally {
      setPredictionLoading(false)
    }
  }

  predict()
}, [tasks, rate])

  // COMPLETE TASK
  const handleComplete = async (id: number) => {
    try {
      console.log('CHECKBOX CLICKED:', id)

      const updatedTask = await completeTask(id)

      console.log('Task completed:', updatedTask)

      if (!plan) return

      const updatedPlan: PlanResponse = {
        ...plan,
        tasks: plan.tasks.map((task) =>
          task.id === id
            ? { ...task, completed: true }
            : task
        ),
      }

      onPlanUpdated(updatedPlan)
    } catch (error) {
      console.error('Failed to complete task:', error)
    }
  }

  // DELETE TASK
  const handleDelete = async (id: number) => {
    try {
      await deleteTask(id)

      console.log('Task deleted:', id)

      if (!plan) return

      const updatedPlan: PlanResponse = {
        ...plan,
        tasks: plan.tasks.filter((task) => task.id !== id),
      }

      onPlanUpdated(updatedPlan)
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  return (
    <div className="screen">
      <header className="screen-header">
        <p className="eyebrow">Good afternoon</p>
        <h1>Here's where today stands</h1>
      </header>

      {tasks.length === 0 ? (
        <div className="empty-state">
          <p>No plan yet. Tell the AI planner what you need to get done.</p>

          <button
            type="button"
            className="btn-primary"
            onClick={onGoToPlanner}
          >
            Generate a plan
          </button>
        </div>
      ) : (
        <>
          <div className="stat-row">
            <div className="stat-card">
              <span className="stat-value">
                {tasks.length}
              </span>
              <span className="stat-label">
                Tasks today
              </span>
            </div>

            <div className="stat-card">
              <span className="stat-value">
                {completed}
              </span>
              <span className="stat-label">
                Completed
              </span>
            </div>

            <div className="stat-card">
              <span className="stat-value">
                {rate}%
              </span>
              <span className="stat-label">
                Completion rate
              </span>
            </div>
          </div>
          <div className="stat-card">
  <span className="stat-value">
    {predictionLoading
      ? '...'
      : prediction !== null
        ? `${prediction}%`
        : '--'}
  </span>

  <span className="stat-label">
    🧠 Predicted productivity
  </span>
</div>
{prediction !== null && (
  <div className="prediction-message">
    <strong>
      {prediction >= 80
        ? '🚀 High productivity expected'
        : prediction >= 60
          ? '🙂 Moderate productivity expected'
          : '⚠️ Low productivity expected'}
    </strong>

    <p>
      {prediction >= 80
        ? 'You are in a good position to complete your planned tasks.'
        : prediction >= 60
          ? 'Stay focused and take a short break between longer tasks.'
          : 'Your productivity may be lower than usual. Consider shorter work sessions and regular breaks.'}
    </p>

    <p>
      <strong>💡 SmartWork AI Suggestion:</strong>{' '}
      {prediction >= 80
        ? 'Use this productive period for your most important task.'
        : prediction >= 60
          ? 'Keep your current schedule and avoid unnecessary distractions.'
          : 'Break long tasks into smaller sessions and take a 10-minute break before the next task.'}
    </p>
  </div>
)}

          <div className="task-list">
            {tasks.map((t) => (
              <div
                key={t.id}
                className={`task-row priority-${t.priority.toLowerCase()}`}
              >
                {/* COMPLETE */}
                <button
                  type="button"
                  className={`checkbox ${
                    t.completed ? 'checked' : ''
                  }`}
                  onClick={() => handleComplete(t.id)}
                  disabled={t.completed}
                  aria-label={`Complete ${t.title}`}
                >
                  {t.completed ? '✓' : ''}
                </button>

                <span className="task-title">
                  {t.title}
                </span>

                <span className="task-duration">
                  {t.duration}m
                </span>

                <span
                  className={`priority-tag ${t.priority.toLowerCase()}`}
                >
                  {t.priority}
                </span>

                {/* DELETE */}
                <button
                  type="button"
                  className="delete-task"
                  onClick={() => handleDelete(t.id)}
                  aria-label={`Delete ${t.title}`}
                >
                  🗑
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-secondary"
            onClick={onGoToPlanner}
          >
            + Generate new plan
          </button>
        </>
      )}
    </div>
  )
}