"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import {
  CheckCircle,
  Play,
  RefreshCw,
  Bell,
  Users,
  Keyboard,
  Moon,
  Wifi,
  Check,
  ArrowRight,
} from "lucide-react";

export default function LandingPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const hasRedirected = useRef(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated && !hasRedirected.current) {
      hasRedirected.current = true;
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-zinc-100 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <Check className="h-5 w-5 text-white" strokeWidth={3} />
            </div>
            <span className="text-xl font-bold text-zinc-900">TODO</span>
          </div>

          <nav className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-zinc-600 hover:text-zinc-900">
              Features
            </a>
            <a href="#about" className="text-sm text-zinc-600 hover:text-zinc-900">
              About
            </a>
          </nav>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium text-zinc-600 hover:text-zinc-900"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50/50 to-white px-4 pb-20 pt-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-indigo-100 px-4 py-1.5 text-sm text-indigo-700">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500"></span>
              </span>
              v2.0 is now live
            </div>

            <h1 className="mb-6 text-4xl font-bold tracking-tight text-zinc-900 sm:text-5xl md:text-6xl">
              Focus on what{" "}
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                matters
              </span>
              .
            </h1>

            <p className="mx-auto mb-10 max-w-2xl text-lg text-zinc-600">
              The minimalist to-do list designed to help you organize your life without
              the clutter. No distractions, just done.
            </p>

            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link
                href="/register"
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-indigo-200 transition-all hover:bg-indigo-700 hover:shadow-xl hover:shadow-indigo-200"
              >
                Start for free
              </Link>
              <button className="flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-6 py-3 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-50">
                <Play className="h-4 w-4" />
                Watch Video
              </button>
            </div>
          </div>

          {/* App Mockup */}
          <div className="mt-16">
            <div className="mx-auto max-w-4xl overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-2xl shadow-zinc-200/50">
              {/* Browser Chrome */}
              <div className="flex items-center gap-2 border-b border-zinc-100 bg-zinc-50 px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-400"></div>
                  <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                  <div className="h-3 w-3 rounded-full bg-green-400"></div>
                </div>
                <div className="mx-auto rounded-md bg-white px-4 py-1 text-xs text-zinc-400">
                  app.todo.com
                </div>
              </div>

              {/* App Content */}
              <div className="flex">
                {/* Sidebar */}
                <div className="w-48 border-r border-zinc-100 bg-zinc-50/50 p-4">
                  <div className="mb-4 text-sm font-semibold text-zinc-900">Workspace</div>
                  <nav className="space-y-1">
                    <a className="flex items-center gap-2 rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700">
                      <div className="h-1.5 w-1.5 rounded-full bg-indigo-500"></div>
                      Inbox
                      <span className="ml-auto rounded bg-indigo-100 px-1.5 py-0.5 text-xs">
                        4
                      </span>
                    </a>
                    <a className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100">
                      <div className="h-1.5 w-1.5 rounded-full bg-zinc-300"></div>
                      Today
                    </a>
                    <a className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100">
                      <div className="h-1.5 w-1.5 rounded-full bg-zinc-300"></div>
                      Upcoming
                    </a>
                  </nav>

                  <div className="mt-6 text-xs font-medium uppercase tracking-wider text-zinc-400">
                    Projects
                  </div>
                  <nav className="mt-2 space-y-1">
                    <a className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100">
                      <div className="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
                      Personal
                    </a>
                    <a className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-zinc-600 hover:bg-zinc-100">
                      <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                      Work
                    </a>
                  </nav>
                </div>

                {/* Main Content */}
                <div className="flex-1 p-6">
                  <div className="mb-6 flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-semibold text-zinc-900">Today</h2>
                      <p className="text-sm text-zinc-500">Tue, October 24</p>
                    </div>
                    <button className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600">
                      <span className="text-xl">+</span>
                    </button>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-3 rounded-lg bg-zinc-50 p-3">
                      <div className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600">
                        <Check className="h-3 w-3 text-white" />
                      </div>
                      <span className="text-sm text-zinc-400 line-through">
                        Design system review
                      </span>
                    </div>

                    <div className="flex items-center gap-3 rounded-lg border border-zinc-100 p-3 hover:border-zinc-200">
                      <div className="h-5 w-5 rounded-full border-2 border-zinc-300"></div>
                      <div className="flex-1">
                        <span className="text-sm text-zinc-900">Call with investors</span>
                        <span className="ml-2 text-xs text-red-500">Due at 3:00 PM</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 rounded-lg border border-zinc-100 p-3 hover:border-zinc-200">
                      <div className="h-5 w-5 rounded-full border-2 border-zinc-300"></div>
                      <span className="text-sm text-zinc-900">Gym at 5pm</span>
                      <span className="ml-auto rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                        Personal
                      </span>
                    </div>

                    <div className="flex items-center gap-3 rounded-lg border border-zinc-100 p-3 hover:border-zinc-200">
                      <div className="h-5 w-5 rounded-full border-2 border-zinc-300"></div>
                      <span className="text-sm text-zinc-900">Weekly Grocery Shop</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="border-y border-zinc-100 bg-zinc-50/50 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="mb-8 text-center text-xs font-medium uppercase tracking-wider text-zinc-400">
            Trusted by productive teams everywhere
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 opacity-50 grayscale">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-8 w-24 rounded bg-zinc-300"></div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-zinc-900 sm:text-4xl">
              Minimalist Features
            </h2>
            <p className="text-lg text-zinc-600">
              Everything you need to stay organized, nothing you don&apos;t.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <div className="rounded-2xl border border-zinc-100 bg-white p-8 transition-shadow hover:shadow-lg">
              <div className="mb-4 inline-flex rounded-xl bg-indigo-100 p-3">
                <RefreshCw className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900">Sync Everywhere</h3>
              <p className="text-zinc-600">
                Seamlessly sync your tasks across all your devices in real-time. Start on
                your phone, finish on your desktop.
              </p>
            </div>

            <div className="rounded-2xl border border-zinc-100 bg-white p-8 transition-shadow hover:shadow-lg">
              <div className="mb-4 inline-flex rounded-xl bg-purple-100 p-3">
                <Bell className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900">Smart Reminders</h3>
              <p className="text-zinc-600">
                Context-aware notifications ensure you never miss a deadline. Set
                recurring tasks with natural language.
              </p>
            </div>

            <div className="rounded-2xl border border-zinc-100 bg-white p-8 transition-shadow hover:shadow-lg">
              <div className="mb-4 inline-flex rounded-xl bg-blue-100 p-3">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-zinc-900">
                Collaborative Lists
              </h3>
              <p className="text-zinc-600">
                Share lists with friends, family, or colleagues effortlessly. Assign
                tasks and track progress together.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Flow State Section */}
      <section id="about" className="bg-zinc-50 py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div className="relative">
              <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-800 to-zinc-900 p-8 shadow-2xl">
                <div className="aspect-[4/3] rounded-lg bg-zinc-700/50"></div>
              </div>
            </div>

            <div>
              <h2 className="mb-6 text-3xl font-bold text-zinc-900 sm:text-4xl">
                Designed for flow state
              </h2>
              <p className="mb-8 text-lg text-zinc-600">
                We stripped away every unnecessary feature to leave only what matters.
                The interface disappears so you can focus entirely on your work. It&apos;s
                not just a tool; it&apos;s a mindset.
              </p>

              <ul className="mb-8 space-y-4">
                <li className="flex items-center gap-3">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-100">
                    <Check className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="text-zinc-700">Keyboard shortcuts for power users</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-100">
                    <Check className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="text-zinc-700">Dark mode included out of the box</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-100">
                    <Check className="h-4 w-4 text-green-600" />
                  </div>
                  <span className="text-zinc-700">Offline support for travel</span>
                </li>
              </ul>

              <a
                href="#"
                className="inline-flex items-center gap-2 font-medium text-indigo-600 hover:text-indigo-700"
              >
                Learn more about our philosophy
                <ArrowRight className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-100 bg-white py-12">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <Check className="h-5 w-5 text-white" strokeWidth={3} />
            </div>
            <span className="text-xl font-bold text-zinc-900">TODO</span>
          </div>

          <p className="text-sm text-zinc-500">
            &copy; {new Date().getFullYear()} TODO Inc. All rights reserved.
          </p>

          <div className="flex items-center gap-4">
            <a href="#" className="text-zinc-400 hover:text-zinc-600">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="#" className="text-zinc-400 hover:text-zinc-600">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
              </svg>
            </a>
            <a href="#" className="text-zinc-400 hover:text-zinc-600">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
