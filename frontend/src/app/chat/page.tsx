"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import Cookies from "js-cookie";
import {
  Check,
  ArrowLeft,
  MessageSquare,
  Sparkles,
  ListTodo,
  Search,
  CheckCircle,
  Plus,
  LayoutDashboard,
  LogOut,
} from "lucide-react";

export default function ChatPage() {
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const [chatKitLoaded, setChatKitLoaded] = useState(false);
  const [ChatKitComponent, setChatKitComponent] = useState<any>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Load ChatKit script and component
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Check if already loaded
    if (customElements.get("openai-chatkit")) {
      setChatKitLoaded(true);
      return;
    }

    // Load the script
    const script = document.createElement("script");
    script.src = "https://cdn.platform.openai.com/deployments/chatkit/chatkit.js";
    script.async = true;
    script.onload = () => {
      customElements.whenDefined("openai-chatkit").then(() => {
        setChatKitLoaded(true);
      });
    };
    script.onerror = (e) => {
      console.error("Failed to load ChatKit script:", e);
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup if needed
    };
  }, []);

  // Initialize ChatKit component after script loads
  useEffect(() => {
    if (!chatKitLoaded || !user) return;

    import("@openai/chatkit-react").then(({ ChatKit, useChatKit }) => {
      setChatKitComponent(() => ({ ChatKit, useChatKit }));
    });
  }, [chatKitLoaded, user]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-zinc-500">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Show loading while ChatKit loads
  if (!chatKitLoaded || !ChatKitComponent) {
    return (
      <div className="flex min-h-screen bg-zinc-50">
        {/* Sidebar */}
        <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-zinc-200 bg-white">
          <div className="flex h-16 items-center gap-2 border-b border-zinc-100 px-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
              <Check className="h-5 w-5 text-white" strokeWidth={3} />
            </div>
            <span className="text-xl font-bold text-zinc-900">TODO</span>
          </div>
          <div className="flex flex-1 items-center justify-center">
            <div className="text-zinc-500">Loading...</div>
          </div>
        </aside>
        <main className="ml-64 flex flex-1 items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100">
              <Sparkles className="h-8 w-8 text-indigo-600" />
            </div>
            <p className="text-zinc-500">Loading AI Assistant...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <ChatKitWrapper
      ChatKitModule={ChatKitComponent}
      router={router}
      user={user}
      onLogout={handleLogout}
    />
  );
}

// Separate component to use the hook
function ChatKitWrapper({
  ChatKitModule,
  router,
  user,
  onLogout,
}: {
  ChatKitModule: { ChatKit: any; useChatKit: any };
  router: any;
  user: any;
  onLogout: () => void;
}) {
  const { ChatKit, useChatKit } = ChatKitModule;

  const { control } = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chatkit`,
      domainKey: "local-dev",
      fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
        const token = Cookies.get("token");
        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            Authorization: `Bearer ${token || ""}`,
          },
        });
      },
    },
    startScreen: {
      greeting: "How can I help you manage your tasks today?",
      prompts: [
        {
          label: "Add Task",
          prompt: "Add a task to buy groceries",
          icon: "write",
        },
        {
          label: "Show Tasks",
          prompt: "Show me all my tasks",
          icon: "search",
        },
        {
          label: "Complete Task",
          prompt: "Mark the groceries task as complete",
          icon: "check",
        },
      ],
    },
    composer: {
      placeholder: "Tell me what you'd like to do with your tasks...",
    },
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
              Navigation
            </p>
            <div className="space-y-1">
              <Link
                href="/dashboard"
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100"
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>

              <div className="flex w-full items-center gap-3 rounded-lg bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700">
                <MessageSquare className="h-4 w-4" />
                AI Assistant
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-6">
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Quick Actions
            </p>
            <div className="space-y-1">
              <button
                onClick={() => control?.sendUserMessage({ text: "Show me all my tasks" })}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-600 transition-colors hover:bg-zinc-100"
              >
                <ListTodo className="h-4 w-4" />
                List all tasks
              </button>
              <button
                onClick={() => control?.sendUserMessage({ text: "Add a new task" })}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-600 transition-colors hover:bg-zinc-100"
              >
                <Plus className="h-4 w-4" />
                Add new task
              </button>
              <button
                onClick={() => control?.sendUserMessage({ text: "Show my completed tasks" })}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-600 transition-colors hover:bg-zinc-100"
              >
                <CheckCircle className="h-4 w-4" />
                Completed tasks
              </button>
              <button
                onClick={() => control?.sendUserMessage({ text: "Search for tasks" })}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-zinc-600 transition-colors hover:bg-zinc-100"
              >
                <Search className="h-4 w-4" />
                Search tasks
              </button>
            </div>
          </div>

          {/* Tips */}
          <div className="rounded-xl bg-gradient-to-br from-indigo-50 to-purple-50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              <p className="text-sm font-medium text-indigo-900">AI Tips</p>
            </div>
            <p className="text-xs text-indigo-700">
              Try asking me to create tasks, set priorities, add due dates, or search
              for specific items!
            </p>
          </div>
        </nav>

        {/* Bottom - User */}
        <div className="border-t border-zinc-100 p-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-medium text-indigo-700">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 truncate">
              <p className="truncate text-sm font-medium text-zinc-900">
                {user?.email?.split("@")[0]}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="rounded-lg p-2 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex flex-1 flex-col">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-zinc-200 bg-white/80 backdrop-blur-sm">
          <div className="flex h-16 items-center justify-between px-8">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100">
                <Sparkles className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-zinc-900">AI Assistant</h1>
                <p className="text-sm text-zinc-500">
                  Powered by natural language processing
                </p>
              </div>
            </div>

            <Link
              href="/dashboard"
              className="flex items-center gap-2 rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-50"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden">
          <ChatKit
            control={control}
            className="h-full w-full"
            style={{
              "--chatkit-primary": "#4f46e5",
              "--chatkit-primary-hover": "#4338ca",
            } as React.CSSProperties}
          />
        </div>
      </main>
    </div>
  );
}
