import axios from 'axios'
import type { PlanResponse, ScheduleBlock, Task } from './types'

const client = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

export async function generatePlan(prompt: string): Promise<PlanResponse> {
  const res = await client.post<PlanResponse>('/api/generate-plan', { prompt })
  return res.data
}

export async function reschedule(
  unfinishedTask: string,
  remainingSchedule: ScheduleBlock[],
  currentTime?: string,
): Promise<ScheduleBlock[]> {
  const res = await client.post<ScheduleBlock[]>('/api/reschedule', {
    unfinished_task: unfinishedTask,
    remaining_schedule: remainingSchedule,
    current_time: currentTime,
  })
  return res.data
}

export async function getTasks(): Promise<Task[]> {
  const res = await client.get<Task[]>('/api/tasks')
  return res.data
}

export async function completeTask(id: number): Promise<Task> {
  const res = await client.patch<Task>(`/api/tasks/${id}/complete`)
  return res.data
}

export async function deleteTask(id: number): Promise<void> {
  await client.delete(`/api/tasks/${id}`)
}
// --------------------------------------------------
// ML PRODUCTIVITY PREDICTION
// --------------------------------------------------

export interface ProductivityPredictionRequest {
  day_of_week: string
  hour: number
  task_duration: number
  difficulty: number
  previous_completion_rate: number
  category: string
}

export interface ProductivityPredictionResponse {
  predicted_productivity: number
}

export async function predictProductivity(
  data: ProductivityPredictionRequest
): Promise<ProductivityPredictionResponse> {
  const res = await client.post<ProductivityPredictionResponse>(
    '/api/predict-productivity',
    data
  )

  return res.data
}