"use client";
import { useState, useRef, useEffect } from "react";
import { MessageBubble } from "./message-bubble";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Message = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const [sidebarContent, setSidebarContent] = useState("");
  const [sidebarLoading, setSidebarLoading] = useState(true);
  const [tab, setTab] = useState<"chat" | "about">("chat");

  useEffect(() => {
    const ctrl = new AbortController();
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/sidebar`, {
          signal: ctrl.signal,
        });
        const reader = res.body!.getReader();
        const dec = new TextDecoder();
        let acc = "";
        let doneStreaming = false;
        let buffer = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done || doneStreaming) break;
          buffer += dec.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          let eventData: string[] = [];
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              eventData.push(line.slice(6));
            } else if (line === "" && eventData.length > 0) {
              const data = eventData.join("\n");
              if (data === "[DONE]") {
                setSidebarLoading(false);
                doneStreaming = true;
                break;
              }
              acc += data;
              setSidebarContent(acc);
              eventData = [];
            }
          }
        }
      } catch {
        setSidebarContent("Could not load app overview.");
        setSidebarLoading(false);
      }
    })();
    return () => ctrl.abort();
  }, []);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleScroll = () => {
    const el = messagesContainerRef.current;
    if (!el) return;
    const threshold = 50;
    const isNearBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
    shouldAutoScrollRef.current = isNearBottom;
  };

  useEffect(() => {
    if (shouldAutoScrollRef.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const scrollToBottom = (smooth = false) => {
    if (shouldAutoScrollRef.current) {
      messagesEndRef.current?.scrollIntoView({
        behavior: smooth ? "smooth" : "instant",
      });
    }
  };

  const send = async () => {
    if (!input.trim() || streaming) return;

    const userMsg: Message = { role: "user", content: input };
    const history = [...messages, userMsg];
    setMessages([...history, { role: "assistant", content: "" }]);
    requestAnimationFrame(() => scrollToBottom());
    setInput("");
    setStreaming(true);

    abortRef.current?.abort();

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: history }),
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status} ${res.statusText}`);
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";
      let doneStreaming = false;
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done || doneStreaming) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        let eventData: string[] = [];
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            eventData.push(line.slice(6));
          } else if (line === "" && eventData.length > 0) {
            const data = eventData.join("\n");
            if (data === "[DONE]") {
              doneStreaming = true;
              break;
            }
            accumulated += data;
            setMessages((prev) => {
              const next = [...prev];
              next[next.length - 1] = {
                role: "assistant",
                content: accumulated,
              };
              return next;
            });
            requestAnimationFrame(() => scrollToBottom());
            eventData = [];
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        console.error(err);
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.content === "") {
            return prev.slice(0, -1);
          }
          return prev;
        });
      }
    } finally {
      if (abortRef.current === controller) {
        setStreaming(false);
        abortRef.current = null;
        inputRef.current?.focus();
      }
    }
  };

  const sidebarInner = (
    <>
      {sidebarLoading && !sidebarContent && (
        <p className="text-sm opacity-60" style={{ color: "var(--rp-text)" }}>
          Loading...
        </p>
      )}
      <div
        className="text-sm whitespace-pre-line leading-relaxed"
        style={{ color: "var(--rp-text)" }}
      >
        {sidebarContent.replace(/  - /g, "\n- ")}
      </div>
    </>
  );

  return (
    <div className="flex h-screen w-full bg-(--rp-base)">
      <div className="flex mx-auto w-full max-w-[1400px]">
        <aside
          className="hidden md:block w-72 shrink-0 overflow-hidden p-4 border"
          style={{
            background: "var(--rp-base)",
            borderColor: "var(--rp-highlight-high)",
          }}
        >
          <h2
            className="font-semibold mb-3"
            style={{ color: "var(--rp-text)" }}
          >
            About
          </h2>
          {sidebarInner}
        </aside>

        <div className="flex-1 flex flex-col">
          <div
            role="tablist"
            aria-label="Navigation tabs"
            className="md:hidden flex justify-center gap-2 p-2 border-b"
            style={{
              background: "var(--rp-base)",
              borderColor: "var(--rp-highlight-high)",
            }}
          >
            <button
              id="chat-tab"
              role="tab"
              aria-selected={tab === "chat"}
              type="button"
              onClick={() => setTab("chat")}
              className="px-5 py-1.5 rounded-full text-sm font-medium transition-colors"
              style={{
                background:
                  tab === "chat" ? "var(--rp-rose)" : "var(--rp-highlight-med)",
                color: tab === "chat" ? "#fff" : "var(--rp-text)",
              }}
            >
              Chat
            </button>
            <button
              id="about-tab"
              role="tab"
              aria-selected={tab === "about"}
              type="button"
              onClick={() => setTab("about")}
              className="px-5 py-1.5 rounded-full text-sm font-medium transition-colors"
              style={{
                background:
                  tab === "about"
                    ? "var(--rp-rose)"
                    : "var(--rp-highlight-med)",
                color: tab === "about" ? "#fff" : "var(--rp-text)",
              }}
            >
              About
            </button>
          </div>

          <div
            role="tabpanel"
            aria-labelledby="chat-tab"
            className={`${tab === "about" ? "hidden md:flex" : "flex"} flex-1 flex-col min-h-0 w-full px-3 sm:px-0 bg-linear-to-br from-(--rp-base) to-(--rp-overlay)`}
          >
            <div
              ref={messagesContainerRef}
              onScroll={handleScroll}
              role="log"
              aria-live="polite"
              aria-relevant="additions"
              className="flex-1 overflow-y-auto min-h-0 p-4 space-y-4"
            >
              {messages.map((m, i) => (
                <MessageBubble key={i} message={m} />
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div
              className="flex gap-2 p-4 mx-3 sm:mx-6 mb-4 rounded-xl shadow-lg border border-(--rp-highlight-high) sticky bottom-0"
              style={{ background: "var(--rp-base)" }}
            >
              <input
                ref={inputRef}
                aria-label="Chat message"
                className="flex-1 border rounded p-2 border-(--rp-highlight-high) hover:border-(--rp-rose) hover:shadow-[0_0_8px_var(--rp-rose)] focus:border-(--rp-rose) focus:shadow-[0_0_3px_var(--rp-rose)] focus:hover:shadow-[0_0_8px_var(--rp-rose)] focus:outline-none transition-colors duration-200"
                style={{
                  background: "var(--rp-surface)",
                  color: "var(--rp-text)",
                }}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
                disabled={streaming}
                placeholder="Type your message..."
              />
              <button
                type="button"
                aria-label="Send message"
                className="text-white px-4 py-2 rounded disabled:opacity-50"
                style={{ background: "var(--rp-iris)" }}
                onClick={send}
                disabled={streaming}
              >
                {streaming ? "..." : "Send"}
              </button>
            </div>
          </div>

          <div
            role="tabpanel"
            aria-labelledby="about-tab"
            className={`${tab === "chat" ? "hidden" : ""} md:hidden flex-1 overflow-y-auto p-4`}
            style={{ background: "var(--rp-base)" }}
          >
            {sidebarInner}
          </div>
        </div>
      </div>
    </div>
  );
}
