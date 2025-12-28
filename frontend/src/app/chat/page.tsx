"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Cookies from "js-cookie";

export default function ChatPage() {
  const { user, isLoading: authLoading } = useAuth();
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

  if (authLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
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
      <div className="flex h-screen flex-col bg-white dark:bg-zinc-950">
        <header className="flex items-center justify-between border-b px-4 py-3 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/dashboard")}
              className="rounded p-1 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
              aria-label="Back to dashboard"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              Task Assistant
            </h1>
          </div>
        </header>
        <div className="flex flex-1 items-center justify-center">
          <div className="text-zinc-500">Loading chat...</div>
        </div>
      </div>
    );
  }

  return <ChatKitWrapper ChatKitModule={ChatKitComponent} router={router} />;
}

// Separate component to use the hook
function ChatKitWrapper({
  ChatKitModule,
  router
}: {
  ChatKitModule: { ChatKit: any; useChatKit: any };
  router: any;
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
    <div className="flex h-screen flex-col bg-white dark:bg-zinc-950">
      <header className="flex items-center justify-between border-b px-4 py-3 dark:border-zinc-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/dashboard")}
            className="rounded p-1 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
            aria-label="Back to dashboard"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Task Assistant
          </h1>
        </div>
      </header>

      <div className="flex-1 overflow-hidden">
        <ChatKit control={control} className="h-full w-full" />
      </div>
    </div>
  );
}
