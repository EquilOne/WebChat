"use client";
import { memo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ErrorBoundary } from "./error-boundary";

type Message = { role: "user" | "assistant"; content: string };

interface Props {
  message: Message;
}

export const MessageBubble = memo(function MessageBubble({ message }: Props) {
  return (
    <ErrorBoundary>
      <div
        className={`p-3 rounded w-fit max-w-[85%] sm:max-w-[75%] min-w-30 ${message.role === "user" ? "ml-auto mr-3 sm:mr-12" : "mr-auto ml-3 sm:ml-12"}`}
        style={{
          background:
            message.role === "user"
              ? "var(--rp-pine)"
              : "var(--rp-highlight-med)",
          color: message.role === "user" ? "#f4ede8" : "var(--rp-text)",
        }}
      >
        <strong>{message.role === "user" ? "You" : "AI"}:</strong>
        <div
          className="prose prose-sm mt-1 w-full max-w-full"
          style={
            {
              color: "var(--rp-text)",
              "--tw-prose-body": "var(--rp-text)",
              "--tw-prose-headings": "var(--rp-text)",
              "--tw-prose-bold": "var(--rp-text)",
              "--tw-prose-links": "var(--rp-rose)",
              "--tw-prose-code": "var(--rp-rose)",
              "--tw-prose-pre-bg": "var(--rp-surface)",
            } as React.CSSProperties
          }
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="overflow-x-auto w-full max-w-full">
                  <table>{children}</table>
                </div>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </ErrorBoundary>
  );
});