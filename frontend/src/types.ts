export type Priority = 'HIGH' | 'MEDIUM' | 'LOW'
export type BlockType = 'task' | 'break'

export interface Task {
  id: number
  title: string
  duration: number
  priority: Priority
  completed: boolean
}

export interface ScheduleBlock {
  task: string
  start: string
  end: string
  type: BlockType
}

export interface PlanResponse {
  tasks: Task[]
  schedule: ScheduleBlock[]
}
