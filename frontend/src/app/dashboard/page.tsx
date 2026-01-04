"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import type { Task, TaskCreate, TaskUpdate, TaskListQuery } from "@/types";
import { TaskCard } from "@/components/TaskCard";
import { TaskForm } from "@/components/TaskForm";
import {
  Check,
  Plus,
  Inbox,
  Calendar,
  Clock,
  MessageSquare,
  Settings,
  LogOut,
  Search,
  ChevronDown,
  Folder,
  Tag,
} from "lucide-react";

type ViewType = "inbox" | "today" | "upcoming";

export default function DashboardPage() {
  const { user, isLoading: authLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [activeView, setActiveView] = useState<ViewType>("inbox");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const loadTasks = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);

      if (searchQuery) {
        const response = await api.searchTasks(searchQuery);
        setTasks(response.tasks);
      } else {
        const query: TaskListQuery = {
          status: statusFilter as TaskListQuery["status"],
          sort: "created_at",
          order: "desc",
        };
        const response = await api.listTasks(query);
        setTasks(response.tasks);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, statusFilter]);

  useEffect(() => {
    if (isAuthenticated) {
      loadTasks();
    }
  }, [loadTasks, isAuthenticated]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const handleSubmitTask = async (data: TaskCreate | TaskUpdate) => {
    if (editingTask) {
      const updatedTask = await api.updateTask(editingTask.id, data as TaskUpdate);
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
      );
      setEditingTask(null);
    } else {
      const newTask = await api.createTask(data as TaskCreate);
      setTasks((prev) => [newTask, ...prev]);
    }
    setShowTaskForm(false);
  };

  const handleToggleComplete = async (taskId: string) => {
    const updatedTask = await api.toggleTaskComplete(taskId);
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    await api.deleteTask(taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const pendingTasks = tasks.filter((t) => t.status === "pending");
  const completedTasks = tasks.filter((t) => t.status === "completed");
  const inProgressTasks = tasks.filter((t) => t.status === "in_progress");

  // Get unique tags from tasks
  const allTags = Array.from(new Set(tasks.flatMap((t) => t.tags || [])));

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const today = new Date();
  const formattedDate = today.toLocaleDateString("en-US", {
    weekday: "short",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="flex min-h-screen bg-zinc-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-zinc-200 bg-white">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-zinc-100 px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
            <Check className="h-5 w-5 text-white" strokeWidth={3} />
          </div>
          <span className="text-xl font-bold text-zinc-900">TODO</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <div className="mb-6">
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Workspace
            </p>
            <div className="space-y-1">
              <button
                onClick={() => {
                  setActiveView("inbox");
                  setStatusFilter(undefined);
                  setSearchQuery("");
                }}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  activeView === "inbox"
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-zinc-600 hover:bg-zinc-100"
                }`}
              >
                <Inbox className="h-4 w-4" />
                Inbox
                {pendingTasks.length > 0 && (
                  <span className="ml-auto rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
                    {pendingTasks.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => {
                  setActiveView("today");
                  setStatusFilter("pending");
                  setSearchQuery("");
                }}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  activeView === "today"
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-zinc-600 hover:bg-zinc-100"
                }`}
              >
                <Calendar className="h-4 w-4" />
                Today
              </button>

              <button
                onClick={() => {
                  setActiveView("upcoming");
                  setStatusFilter(undefined);
                  setSearchQuery("");
                }}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  activeView === "upcoming"
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-zinc-600 hover:bg-zinc-100"
                }`}
              >
                <Clock className="h-4 w-4" />
                Upcoming
              </button>
            </div>
          </div>

          {/* Tags */}
          {allTags.length > 0 && (
            <div className="mb-6">
              <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Tags
              </p>
              <div className="space-y-1">
                {allTags.slice(0, 5).map((tag) => (
                  <button
                    key={tag}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100"
                  >
                    <div className="h-2 w-2 rounded-full bg-indigo-500" />
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="rounded-xl bg-zinc-50 p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Overview
            </p>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-600">Pending</span>
                <span className="font-medium text-zinc-900">{pendingTasks.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-600">In Progress</span>
                <span className="font-medium text-zinc-900">{inProgressTasks.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-600">Completed</span>
                <span className="font-medium text-zinc-900">{completedTasks.length}</span>
              </div>
            </div>
          </div>
        </nav>

        {/* Bottom Actions */}
        <div className="border-t border-zinc-100 p-4">
          <Link
            href="/chat"
            className="flex w-full items-center gap-3 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
          >
            <MessageSquare className="h-4 w-4" />
            AI Assistant
          </Link>

          <div className="mt-3 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-medium text-indigo-700">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 truncate">
              <p className="truncate text-sm font-medium text-zinc-900">
                {user?.email?.split("@")[0]}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg p-2 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-zinc-200 bg-white/80 backdrop-blur-sm">
          <div className="flex h-16 items-center justify-between px-8">
            <div>
              <h1 className="text-xl font-semibold text-zinc-900">
                {activeView === "inbox" && "Inbox"}
                {activeView === "today" && "Today"}
                {activeView === "upcoming" && "Upcoming"}
              </h1>
              <p className="text-sm text-zinc-500">{formattedDate}</p>
            </div>

            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 rounded-lg border border-zinc-200 bg-zinc-50 py-2 pl-10 pr-4 text-sm text-zinc-900 placeholder-zinc-400 focus:border-indigo-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              {/* Add Task Button */}
              <button
                onClick={() => {
                  setEditingTask(null);
                  setShowTaskForm(true);
                }}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
              >
                <Plus className="h-4 w-4" />
                Add Task
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-8">
          {/* Task Form Modal */}
          {(showTaskForm || editingTask) && (
            <div className="mb-8 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-zinc-900">
                {editingTask ? "Edit Task" : "Create New Task"}
              </h2>
              <TaskForm
                task={editingTask}
                onSubmit={handleSubmitTask}
                onCancel={() => {
                  setShowTaskForm(false);
                  setEditingTask(null);
                }}
              />
            </div>
          )}

          {/* Task List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-zinc-500">Loading tasks...</div>
            </div>
          ) : error ? (
            <div className="rounded-xl bg-red-50 p-4 text-red-600">
              {error}
              <button
                onClick={loadTasks}
                className="ml-2 underline hover:no-underline"
              >
                Retry
              </button>
            </div>
          ) : tasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-zinc-100">
                <Inbox className="h-8 w-8 text-zinc-400" />
              </div>
              <h3 className="mb-2 text-lg font-medium text-zinc-900">No tasks yet</h3>
              <p className="mb-6 text-zinc-500">
                Get started by creating your first task
              </p>
              <button
                onClick={() => setShowTaskForm(true)}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
              >
                <Plus className="h-4 w-4" />
                Add Task
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onEdit={(t) => {
                    setEditingTask(t);
                    setShowTaskForm(false);
                  }}
                  onDelete={handleDeleteTask}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
