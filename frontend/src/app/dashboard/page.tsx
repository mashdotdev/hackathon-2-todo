"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { TaskList } from "@/components/TaskList";

export default function DashboardPage() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
            Todo App
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-zinc-600 dark:text-zinc-400">
              {user?.email}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-3xl px-4 py-8">
        <TaskList />
      </main>
    </div>
  );
}
