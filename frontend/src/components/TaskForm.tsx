"use client";

import { useState, type FormEvent } from "react";
import type { Task, TaskCreate, TaskUpdate, Priority, RecurrencePattern } from "@/types";
import { X, ChevronDown, ChevronUp } from "lucide-react";

interface TaskFormProps {
  task?: Task | null;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  onCancel?: () => void;
}

const PRIORITIES: Priority[] = ["High", "Medium", "Low"];
const RECURRENCE_PATTERNS: { value: RecurrencePattern; label: string }[] = [
  { value: "none", label: "No recurrence" },
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
];

export function TaskForm({ task, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || "");
  const [description, setDescription] = useState(task?.description || "");
  const [priority, setPriority] = useState<Priority>(task?.priority || "Medium");
  const [tagsInput, setTagsInput] = useState(task?.tags?.join(", ") || "");
  const [dueDate, setDueDate] = useState(
    task?.due_date ? task.due_date.slice(0, 16) : ""
  );
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern>(
    task?.recurrence_pattern || "none"
  );
  const [reminderLeadTime, setReminderLeadTime] = useState<string>(
    task?.reminder_lead_time?.toString() || ""
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(
    !!(task?.recurrence_pattern && task.recurrence_pattern !== "none") ||
    !!task?.reminder_lead_time
  );

  const isEditing = !!task;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    // Parse tags from comma-separated input
    const tags = tagsInput
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    if (tags.length > 10) {
      setError("Maximum 10 tags allowed");
      return;
    }

    setIsSubmitting(true);
    try {
      const data: TaskCreate | TaskUpdate = {
        title: title.trim(),
        description: description.trim() || null,
        priority,
        tags,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        recurrence_pattern: recurrencePattern,
        reminder_lead_time: reminderLeadTime
          ? parseInt(reminderLeadTime, 10)
          : null,
      };

      await onSubmit(data);
      if (!isEditing) {
        setTitle("");
        setDescription("");
        setPriority("Medium");
        setTagsInput("");
        setDueDate("");
        setRecurrencePattern("none");
        setReminderLeadTime("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600">
          <span>{error}</span>
        </div>
      )}

      {/* Title */}
      <div>
        <label
          htmlFor="title"
          className="mb-1.5 block text-sm font-medium text-zinc-700"
        >
          Title
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="What needs to be done?"
          required
        />
      </div>

      {/* Description */}
      <div>
        <label
          htmlFor="description"
          className="mb-1.5 block text-sm font-medium text-zinc-700"
        >
          Description <span className="text-zinc-400">(optional)</span>
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          rows={2}
          className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="Add more details..."
        />
      </div>

      {/* Priority and Due Date Row */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="priority"
            className="mb-1.5 block text-sm font-medium text-zinc-700"
          >
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
            className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="dueDate"
            className="mb-1.5 block text-sm font-medium text-zinc-700"
          >
            Due Date <span className="text-zinc-400">(optional)</span>
          </label>
          <input
            type="datetime-local"
            id="dueDate"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Tags */}
      <div>
        <label
          htmlFor="tags"
          className="mb-1.5 block text-sm font-medium text-zinc-700"
        >
          Tags <span className="text-zinc-400">(comma-separated, max 10)</span>
        </label>
        <input
          type="text"
          id="tags"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="work, urgent, project-x"
        />
      </div>

      {/* Advanced Options Toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700"
      >
        {showAdvanced ? (
          <>
            <ChevronUp className="h-4 w-4" />
            Hide advanced options
          </>
        ) : (
          <>
            <ChevronDown className="h-4 w-4" />
            Show advanced options
          </>
        )}
      </button>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="space-y-4 rounded-lg border border-zinc-100 bg-zinc-50 p-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="recurrence"
                className="mb-1.5 block text-sm font-medium text-zinc-700"
              >
                Recurrence
              </label>
              <select
                id="recurrence"
                value={recurrencePattern}
                onChange={(e) =>
                  setRecurrencePattern(e.target.value as RecurrencePattern)
                }
                className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {RECURRENCE_PATTERNS.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="reminder"
                className="mb-1.5 block text-sm font-medium text-zinc-700"
              >
                Reminder <span className="text-zinc-400">(minutes before)</span>
              </label>
              <input
                type="number"
                id="reminder"
                value={reminderLeadTime}
                onChange={(e) => setReminderLeadTime(e.target.value)}
                min="1"
                placeholder="e.g., 30"
                className="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-zinc-900 placeholder-zinc-400 transition-colors focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Submit Buttons */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Saving..." : isEditing ? "Update Task" : "Create Task"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-zinc-200 bg-white px-4 py-2.5 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
