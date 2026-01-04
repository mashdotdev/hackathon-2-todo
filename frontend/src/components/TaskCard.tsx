"use client";

import type { Task, Priority } from "@/types";
import { Check, Pencil, Trash2, Calendar, RotateCcw } from "lucide-react";

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

const priorityColors: Record<Priority, string> = {
  High: "bg-red-100 text-red-700",
  Medium: "bg-amber-100 text-amber-700",
  Low: "bg-emerald-100 text-emerald-700",
};

function isOverdue(dueDate: string | null): boolean {
  if (!dueDate) return false;
  return new Date(dueDate) < new Date();
}

function formatDueDate(dueDate: string): string {
  const date = new Date(dueDate);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return `Overdue by ${Math.abs(diffDays)} day(s)`;
  } else if (diffDays === 0) {
    return "Due today";
  } else if (diffDays === 1) {
    return "Due tomorrow";
  } else if (diffDays <= 7) {
    return `Due in ${diffDays} days`;
  } else {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  }
}

export function TaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskCardProps) {
  const isCompleted = task.status === "completed";
  const overdue = !isCompleted && isOverdue(task.due_date);
  const priorityStyle = priorityColors[task.priority] || priorityColors.Medium;

  return (
    <div
      className={`group flex items-start gap-4 rounded-xl border p-4 transition-all hover:shadow-md ${
        isCompleted
          ? "border-zinc-100 bg-zinc-50"
          : "border-zinc-200 bg-white hover:border-indigo-200"
      }`}
    >
      {/* Checkbox */}
      <button
        onClick={() => onToggleComplete(task.id)}
        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-all ${
          isCompleted
            ? "border-indigo-600 bg-indigo-600 text-white"
            : "border-zinc-300 hover:border-indigo-500"
        }`}
        aria-label={isCompleted ? "Mark incomplete" : "Mark complete"}
      >
        {isCompleted && <Check className="h-3 w-3" strokeWidth={3} />}
      </button>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h3
            className={`font-medium ${
              isCompleted ? "text-zinc-400 line-through" : "text-zinc-900"
            }`}
          >
            {task.title}
          </h3>
          {task.priority && (
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${priorityStyle}`}
            >
              {task.priority}
            </span>
          )}
        </div>

        {task.description && (
          <p
            className={`mt-1 text-sm ${
              isCompleted ? "text-zinc-400" : "text-zinc-600"
            }`}
          >
            {task.description}
          </p>
        )}

        {/* Meta info row */}
        <div className="mt-3 flex flex-wrap items-center gap-3">
          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {task.tags.map((tag, index) => (
                <span
                  key={index}
                  className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-600"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Due Date */}
          {task.due_date && (
            <span
              className={`flex items-center gap-1 text-xs ${
                overdue ? "font-medium text-red-600" : "text-zinc-500"
              }`}
            >
              <Calendar className="h-3 w-3" />
              {formatDueDate(task.due_date)}
            </span>
          )}

          {/* Recurrence */}
          {task.recurrence_pattern && task.recurrence_pattern !== "none" && (
            <span className="flex items-center gap-1 text-xs text-purple-600">
              <RotateCcw className="h-3 w-3" />
              {task.recurrence_pattern.charAt(0).toUpperCase() +
                task.recurrence_pattern.slice(1)}
            </span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <button
          onClick={() => onEdit(task)}
          className="rounded-lg p-2 text-zinc-400 transition-colors hover:bg-zinc-100 hover:text-zinc-600"
          aria-label="Edit task"
        >
          <Pencil className="h-4 w-4" />
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="rounded-lg p-2 text-zinc-400 transition-colors hover:bg-red-50 hover:text-red-600"
          aria-label="Delete task"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
