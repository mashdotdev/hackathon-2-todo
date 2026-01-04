/**
 * API types for Todo application
 * Phase V: Extended with priority, tags, due_date, recurrence
 */

export type TaskStatus = "pending" | "in_progress" | "completed";
export type Priority = "High" | "Medium" | "Low";
export type RecurrencePattern = "none" | "daily" | "weekly" | "monthly";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: Priority;
  tags: string[];
  due_date: string | null;
  recurrence_pattern: RecurrencePattern;
  reminder_lead_time: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  recurrence_pattern?: RecurrencePattern;
  reminder_lead_time?: number | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: Priority;
  tags?: string[];
  due_date?: string | null;
  recurrence_pattern?: RecurrencePattern;
  reminder_lead_time?: number | null;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface TaskListQuery {
  status?: TaskStatus;
  priority?: Priority;
  tags?: string;
  due_date_from?: string;
  due_date_to?: string;
  sort?: "priority" | "due_date" | "created_at";
  order?: "asc" | "desc";
}

export interface Notification {
  notification_id: string;
  user_id: string;
  task_id: string | null;
  notification_type: string;
  message: string;
  sent_at: string;
  delivery_status: "sent" | "read" | "failed";
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  unread_count: number;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface ErrorResponse {
  detail: string;
}
