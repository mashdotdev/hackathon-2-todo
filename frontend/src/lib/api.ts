/**
 * API client for Todo backend
 */

import axios, { AxiosError, AxiosInstance } from "axios";
import Cookies from "js-cookie";
import type {
  AuthResponse,
  ErrorResponse,
  Task,
  TaskCreate,
  TaskListQuery,
  TaskListResponse,
  TaskUpdate,
  User,
  UserCreate,
  UserLogin,
  NotificationListResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = Cookies.get("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        if (error.response?.status === 401) {
          Cookies.remove("token");
          // Only redirect if not already on login/register pages to prevent loops
          if (typeof window !== "undefined") {
            const currentPath = window.location.pathname;
            if (currentPath !== "/login" && currentPath !== "/register") {
              window.location.href = "/login";
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: UserCreate): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>(
      "/api/auth/register",
      data
    );
    return response.data;
  }

  async login(data: UserLogin): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>(
      "/api/auth/login",
      data
    );
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post("/api/auth/logout");
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>("/api/auth/me");
    return response.data;
  }

  // Task endpoints
  async listTasks(query?: TaskListQuery | string): Promise<TaskListResponse> {
    // Support legacy string status filter and new query object
    let params: Record<string, string | undefined> = {};
    if (typeof query === "string") {
      params = { status: query };
    } else if (query) {
      params = {
        status: query.status,
        priority: query.priority,
        tags: query.tags,
        due_date_from: query.due_date_from,
        due_date_to: query.due_date_to,
        sort: query.sort,
        order: query.order,
      };
    }
    const response = await this.client.get<TaskListResponse>("/api/tasks", {
      params,
    });
    return response.data;
  }

  async searchTasks(q: string): Promise<TaskListResponse> {
    const response = await this.client.get<TaskListResponse>(
      "/api/tasks/search",
      { params: { q } }
    );
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await this.client.get<Task>(`/api/tasks/${taskId}`);
    return response.data;
  }

  async createTask(data: TaskCreate): Promise<Task> {
    const response = await this.client.post<Task>("/api/tasks", data);
    return response.data;
  }

  async updateTask(taskId: string, data: TaskUpdate): Promise<Task> {
    const response = await this.client.put<Task>(`/api/tasks/${taskId}`, data);
    return response.data;
  }

  async patchTask(taskId: string, data: TaskUpdate): Promise<Task> {
    const response = await this.client.patch<Task>(
      `/api/tasks/${taskId}`,
      data
    );
    return response.data;
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.client.delete(`/api/tasks/${taskId}`);
  }

  async toggleTaskComplete(taskId: string): Promise<Task> {
    const response = await this.client.patch<Task>(
      `/api/tasks/${taskId}/complete`
    );
    return response.data;
  }

  // Notification endpoints
  async listNotifications(
    unreadOnly: boolean = false
  ): Promise<NotificationListResponse> {
    const response = await this.client.get<NotificationListResponse>(
      "/api/notifications",
      { params: { unread_only: unreadOnly } }
    );
    return response.data;
  }

  async markNotificationRead(notificationId: string): Promise<void> {
    await this.client.patch(`/api/notifications/${notificationId}/mark_read`);
  }

  // Chat endpoints
  async getChatHistory(limit?: number): Promise<ChatHistoryResponse> {
    const params = limit ? { limit } : {};
    const response = await this.client.get<ChatHistoryResponse>(
      "/api/chat/history",
      { params }
    );
    return response.data;
  }

  async clearChatHistory(): Promise<void> {
    await this.client.delete("/api/chat/history");
  }
}

// Chat types
export interface StoredMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  conversation_id: string;
  messages: StoredMessage[];
}

export const api = new ApiClient();
