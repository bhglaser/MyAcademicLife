"use client";

import { useState, useRef, useEffect } from "react";
import { chat, ToolAction } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolActions?: ToolAction[] | null;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load chat history on mount
  useEffect(() => {
    let cancelled = false;
    async function loadHistory() {
      try {
        const history = await chat.history();
        if (cancelled) return;
        if (history.length > 0) {
          setMessages(
            history.map((msg) => ({
              role: msg.role,
              content: msg.content,
              toolActions: msg.tool_actions,
            }))
          );
        } else {
          setMessages([
            {
              role: "assistant",
              content:
                "Hi! I'm your academic assistant. Ask me about time management, research priorities, upcoming deadlines, or anything else. I can see your projects, tasks, goals, and journal to give personalised advice. I can also create tasks for you!",
            },
          ]);
        }
      } catch {
        setMessages([
          {
            role: "assistant",
            content:
              "Hi! I'm your academic assistant. Ask me about time management, research priorities, upcoming deadlines, or anything else.",
          },
        ]);
      } finally {
        if (!cancelled) setHistoryLoaded(true);
      }
    }
    loadHistory();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await chat.send(userMessage);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply,
          toolActions: res.tool_actions,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't process that. Make sure the API server is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await chat.clearHistory();
      setMessages([
        {
          role: "assistant",
          content: "Conversation cleared! How can I help you today?",
        },
      ]);
    } catch {
      // ignore
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Assistant</h1>
        {messages.length > 1 && (
          <button
            onClick={handleClearHistory}
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            Clear history
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {!historyLoaded && (
          <div className="text-sm text-slate-400 text-center py-8">
            Loading conversation...
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i}>
            <div
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                  msg.role === "user"
                    ? "bg-slate-900 text-white rounded-br-md"
                    : "bg-white border border-slate-200 shadow-sm rounded-bl-md"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
            {msg.toolActions && msg.toolActions.length > 0 && (
              <div className="flex justify-start mt-1 ml-2">
                <div className="flex flex-wrap gap-1">
                  {msg.toolActions.map((action, j) => (
                    <span
                      key={j}
                      className="inline-flex items-center gap-1 text-xs bg-green-50 text-green-700 border border-green-200 rounded-full px-2 py-0.5"
                    >
                      {action.tool === "create_task" && (
                        <>
                          <span>Created task:</span>
                          <span className="font-medium">
                            {(action.result as Record<string, unknown>).title as string}
                          </span>
                        </>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 shadow-sm rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1">
                <span
                  className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="flex gap-3 pt-4 border-t border-slate-200"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your research, deadlines, or say 'create a task to...'"
          className="flex-1 border border-slate-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-slate-900 text-white px-5 py-3 rounded-xl text-sm font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>
    </div>
  );
}
