"use client";

import { useState } from "react";
import type { Priority, TaskStatus } from "@/types";

export interface FilterState {
  status?: TaskStatus;
  priority?: Priority;
  tags?: string;
  due_date_from?: string;
  due_date_to?: string;
  sort: "priority" | "due_date" | "created_at";
  order: "asc" | "desc";
}

interface FilterControlsProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  availableTags?: string[];
}

const PRIORITIES: (Priority | "")[] = ["", "High", "Medium", "Low"];
const STATUSES: (TaskStatus | "")[] = ["", "pending", "in_progress", "completed"];
const SORT_OPTIONS: { value: FilterState["sort"]; label: string }[] = [
  { value: "created_at", label: "Created Date" },
  { value: "due_date", label: "Due Date" },
  { value: "priority", label: "Priority" },
];

export function FilterControls({
  filters,
  onFiltersChange,
  availableTags = [],
}: FilterControlsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleChange = (key: keyof FilterState, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
    });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      sort: "created_at",
      order: "desc",
    });
  };

  const hasActiveFilters =
    filters.status ||
    filters.priority ||
    filters.tags ||
    filters.due_date_from ||
    filters.due_date_to;

  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      {/* Toggle and Sort Row */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-sm font-medium text-zinc-700 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-100"
        >
          <svg
            className={`h-4 w-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
          Filters
          {hasActiveFilters && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              Active
            </span>
          )}
        </button>

        <div className="flex items-center gap-3">
          {/* Sort By */}
          <div className="flex items-center gap-2">
            <label
              htmlFor="sort"
              className="text-sm text-zinc-500 dark:text-zinc-400"
            >
              Sort by:
            </label>
            <select
              id="sort"
              value={filters.sort}
              onChange={(e) =>
                handleChange("sort", e.target.value as FilterState["sort"])
              }
              className="rounded-md border border-zinc-300 bg-white px-2 py-1 text-sm text-zinc-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Order Toggle */}
          <button
            type="button"
            onClick={() =>
              handleChange("order", filters.order === "asc" ? "desc" : "asc")
            }
            className="rounded-md border border-zinc-300 p-1 text-zinc-500 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800"
            title={filters.order === "asc" ? "Ascending" : "Descending"}
          >
            <svg
              className={`h-4 w-4 transition-transform ${
                filters.order === "asc" ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4h13M3 8h9m-9 4h6m4 0l4 4m0 0l4-4m-4 4V4"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="mt-4 space-y-4 border-t border-zinc-200 pt-4 dark:border-zinc-700">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Status Filter */}
            <div>
              <label
                htmlFor="status-filter"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Status
              </label>
              <select
                id="status-filter"
                value={filters.status || ""}
                onChange={(e) => handleChange("status", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="">All statuses</option>
                {STATUSES.filter(Boolean).map((s) => (
                  <option key={s} value={s}>
                    {s === "in_progress"
                      ? "In Progress"
                      : s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label
                htmlFor="priority-filter"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Priority
              </label>
              <select
                id="priority-filter"
                value={filters.priority || ""}
                onChange={(e) => handleChange("priority", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              >
                <option value="">All priorities</option>
                {PRIORITIES.filter(Boolean).map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            {/* Due Date From */}
            <div>
              <label
                htmlFor="due-from"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Due Date From
              </label>
              <input
                type="date"
                id="due-from"
                value={filters.due_date_from || ""}
                onChange={(e) => handleChange("due_date_from", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>

            {/* Due Date To */}
            <div>
              <label
                htmlFor="due-to"
                className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
              >
                Due Date To
              </label>
              <input
                type="date"
                id="due-to"
                value={filters.due_date_to || ""}
                onChange={(e) => handleChange("due_date_to", e.target.value)}
                className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100"
              />
            </div>
          </div>

          {/* Tags Filter */}
          <div>
            <label
              htmlFor="tags-filter"
              className="block text-sm font-medium text-zinc-700 dark:text-zinc-300"
            >
              Tags (comma-separated)
            </label>
            <input
              type="text"
              id="tags-filter"
              value={filters.tags || ""}
              onChange={(e) => handleChange("tags", e.target.value)}
              placeholder="e.g., work, urgent"
              className="mt-1 block w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 placeholder-zinc-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder-zinc-500"
            />
            {availableTags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {availableTags.slice(0, 10).map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => {
                      const currentTags = filters.tags
                        ? filters.tags.split(",").map((t) => t.trim())
                        : [];
                      if (!currentTags.includes(tag)) {
                        handleChange(
                          "tags",
                          [...currentTags, tag].filter(Boolean).join(", ")
                        );
                      }
                    }}
                    className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
                  >
                    + {tag}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Clear Filters Button */}
          {hasActiveFilters && (
            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleClearFilters}
                className="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
