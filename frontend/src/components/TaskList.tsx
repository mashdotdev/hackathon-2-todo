"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Task, TaskCreate, TaskUpdate, TaskListQuery } from "@/types";
import { TaskCard } from "./TaskCard";
import { TaskForm } from "./TaskForm";
import { SearchBar } from "./SearchBar";
import { FilterControls, type FilterState } from "./FilterControls";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    sort: "created_at",
    order: "desc",
  });

  // Collect available tags from tasks for filter suggestions
  const availableTags = Array.from(
    new Set(tasks.flatMap((t) => t.tags || []))
  ).slice(0, 20);

  const loadTasks = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);

      // If there's a search query, use search endpoint
      if (searchQuery) {
        setIsSearching(true);
        const response = await api.searchTasks(searchQuery);
        setTasks(response.tasks);
        setIsSearching(false);
      } else {
        // Build query from filters
        const query: TaskListQuery = {
          status: filters.status,
          priority: filters.priority,
          tags: filters.tags,
          due_date_from: filters.due_date_from,
          due_date_to: filters.due_date_to,
          sort: filters.sort,
          order: filters.order,
        };
        const response = await api.listTasks(query);
        setTasks(response.tasks);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
      setIsSearching(false);
    }
  }, [
    searchQuery,
    filters.status,
    filters.priority,
    filters.tags,
    filters.due_date_from,
    filters.due_date_to,
    filters.sort,
    filters.order,
  ]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleFiltersChange = (newFilters: FilterState) => {
    // Clear search when applying filters
    if (searchQuery) {
      setSearchQuery("");
    }
    setFilters(newFilters);
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
  const inProgressCount = tasks.filter((t) => t.status === "in_progress").length;

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

      {/* Search Bar */}
      <SearchBar
        onSearch={handleSearch}
        placeholder="Search tasks by title or description..."
      />

      {/* Filter Controls */}
      <FilterControls
        filters={filters}
        onFiltersChange={handleFiltersChange}
        availableTags={availableTags}
      />

      {/* Status Summary */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-600 dark:text-zinc-400">
        <span className="font-medium text-zinc-900 dark:text-zinc-100">
          {tasks.length} task{tasks.length !== 1 ? "s" : ""}
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-yellow-500" />
          {pendingCount} pending
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-blue-500" />
          {inProgressCount} in progress
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-green-500" />
          {completedCount} completed
        </span>
        {searchQuery && (
          <span className="ml-auto text-blue-600 dark:text-blue-400">
            Search results for: "{searchQuery}"
            <button
              onClick={() => setSearchQuery("")}
              className="ml-2 underline hover:no-underline"
            >
              Clear
            </button>
          </span>
        )}
      </div>

      {/* Task List */}
      {isLoading || isSearching ? (
        <div className="py-8 text-center text-zinc-500">
          {isSearching ? "Searching..." : "Loading tasks..."}
        </div>
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
          {searchQuery
            ? `No tasks found for "${searchQuery}"`
            : filters.status || filters.priority || filters.tags
            ? "No tasks match the current filters."
            : "No tasks yet. Add one above!"}
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
