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
  TaskListResponse,
  TaskUpdate,
  User,
  UserCreate,
  UserLogin,
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
          if (typeof window !== "undefined") {
            window.location.href = "/login";
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
  async listTasks(status?: string): Promise<TaskListResponse> {
    const params = status ? { status_filter: status } : {};
    const response = await this.client.get<TaskListResponse>("/api/tasks", {
      params,
    });
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

  async deleteTask(taskId: string): Promise<void> {
    await this.client.delete(`/api/tasks/${taskId}`);
  }

  async toggleTaskComplete(taskId: string): Promise<Task> {
    const response = await this.client.patch<Task>(
      `/api/tasks/${taskId}/complete`
    );
    return response.data;
  }
}

export const api = new ApiClient();
