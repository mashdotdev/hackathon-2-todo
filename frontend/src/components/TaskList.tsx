"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Task, TaskCreate, TaskUpdate } from "@/types";
import { TaskCard } from "./TaskCard";
import { TaskForm } from "./TaskForm";

type FilterStatus = "all" | "pending" | "completed";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const loadTasks = async () => {
    try {
      setError(null);
      const statusFilter = filter === "all" ? undefined : filter;
      const response = await api.listTasks(statusFilter);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [filter]);

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

  const pendingCount = tasks.filter((t) => t.status === "pending").length;
  const completedCount = tasks.filter((t) => t.status === "completed").length;

  return (
    <div className="space-y-6">
      {/* Add Task Form */}
      <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          {editingTask ? "Edit Task" : "Add New Task"}
        </h2>
        <TaskForm
          task={editingTask}
          onSubmit={handleSubmitTask}
          onCancel={editingTask ? () => setEditingTask(null) : undefined}
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(["all", "pending", "completed"] as FilterStatus[]).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === status
                ? "bg-blue-600 text-white"
                : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
            {status === "all" && ` (${tasks.length})`}
            {status === "pending" && ` (${pendingCount})`}
            {status === "completed" && ` (${completedCount})`}
          </button>
        ))}
      </div>

      {/* Task List */}
      {isLoading ? (
        <div className="py-8 text-center text-zinc-500">Loading tasks...</div>
      ) : error ? (
        <div className="rounded-lg bg-red-50 p-4 text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
          <button
            onClick={loadTasks}
            className="ml-2 underline hover:no-underline"
          >
            Retry
          </button>
        </div>
      ) : tasks.length === 0 ? (
        <div className="py-8 text-center text-zinc-500 dark:text-zinc-400">
          {filter === "all"
            ? "No tasks yet. Add one above!"
            : `No ${filter} tasks.`}
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onEdit={setEditingTask}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      )}
    </div>
  );
}
