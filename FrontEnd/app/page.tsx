"use client";
import { useState, useRef, useEffect } from "react";

type Message = { role: "user" | "assistant"; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const [sidebarContent, setSidebarContent] = useState("");
  const [sidebarLoading, setSidebarLoading] = useState(true);
  const [tab, setTab] = useState<"chat" | "about">("chat");

  useEffect(() => {
    const ctrl = new AbortController();
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/sidebar", {
          signal: ctrl.signal,
        });
        const reader = res.body!.getReader();
        const dec = new TextDecoder();
        let acc = "";
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          for (const line of dec.decode(value).split("\n")) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              if (data === "[DONE]") {
                setSidebarLoading(false);
                break;
              }
              acc += data;
              setSidebarContent(acc);
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

  const send = async () => {
    if (!input.trim() || streaming) return;

    const userMsg: Message = { role: "user", content: input };
    const history = [...messages, userMsg];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setStreaming(true);

    abortRef.current?.abort();

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: history }),
        signal: controller.signal,
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        for (const line of text.split("\n")) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            accumulated += data;
            setMessages((prev) => {
              const next = [...prev];
              next[next.length - 1] = {
                role: "assistant",
                content: accumulated,
              };
              return next;
            });
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") console.error(err);
    } finally {
      setStreaming(false);
      abortRef.current = null;
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
        {sidebarContent}
      </div>
    </>
  );

  return (
    <div className="flex h-screen w-full">
      <aside
        className="hidden md:block w-72 shrink-0 overflow-y-auto p-4 border-r"
        style={{
          background: "var(--rp-base)",
          borderColor: "var(--rp-highlight-high)",
        }}
      >
        <h2 className="font-semibold mb-3" style={{ color: "var(--rp-text)" }}>
          About
        </h2>
        {sidebarInner}
      </aside>

      <div className="flex-1 flex flex-col">
        <div
          className="md:hidden flex justify-center gap-2 p-2 border-b"
          style={{
            background: "var(--rp-base)",
            borderColor: "var(--rp-highlight-high)",
          }}
        >
          <button
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
            onClick={() => setTab("about")}
            className="px-5 py-1.5 rounded-full text-sm font-medium transition-colors"
            style={{
              background:
                tab === "about" ? "var(--rp-rose)" : "var(--rp-highlight-med)",
              color: tab === "about" ? "#fff" : "var(--rp-text)",
            }}
          >
            About
          </button>
        </div>

        <div
          className={`${tab === "about" ? "hidden md:flex" : "flex"} flex-1 flex-col w-full mx-auto px-3 sm:px-0 sm:max-w-xl md:max-w-2xl lg:max-w-3xl xl:max-w-4xl 2xl:max-w-5xl bg-linear-to-br from-(--rp-base) to-(--rp-overlay)`}
        >
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`p-3 rounded w-fit max-w-[85%] sm:max-w-[75%] min-w-30 ${m.role === "user" ? "ml-auto mr-3 sm:mr-12" : "mr-auto ml-3 sm:ml-12"}`}
                style={{
                  background:
                    m.role === "user"
                      ? "var(--rp-pine)"
                      : "var(--rp-highlight-med)",
                  color: m.role === "user" ? "#f4ede8" : "var(--rp-text)",
                }}
              >
                <strong>{m.role === "user" ? "You" : "AI"}:</strong>
                <p className="mt-1">{m.content}</p>
              </div>
            ))}
          </div>

          <div
            className="flex gap-2 p-4 mx-3 sm:mx-6 mb-4 rounded-xl shadow-lg border border-(--rp-highlight-high) sticky bottom-0"
            style={{ background: "var(--rp-base)" }}
          >
            <input
              className="flex-1 border rounded p-2 border-(--rp-highlight-high) hover:border-(--rp-rose) hover:shadow-[0_0_8px_var(--rp-rose)] focus:border-(--rp-rose) focus:shadow-[0_0_3px_var(--rp-rose)] focus:hover:shadow-[0_0_8px_var(--rp-rose)] focus:outline-none transition-colors duration-200"
              style={{
                background: "var(--rp-surface)",
                color: "var(--rp-text)",
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              disabled={streaming}
              placeholder="Type your message..."
            />
            <button
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
          className={`${tab === "chat" ? "hidden" : ""} md:hidden flex-1 overflow-y-auto p-4`}
          style={{ background: "var(--rp-base)" }}
        >
          {sidebarInner}
        </div>
      </div>
    </div>
  );
}
