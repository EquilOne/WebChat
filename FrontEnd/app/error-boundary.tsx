"use client";
import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error("ErrorBoundary caught:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-center" style={{ color: "var(--rp-text)" }}>
          <p>Something went wrong displaying this message.</p>
          <button
            className="mt-2 px-3 py-1 rounded text-sm"
            style={{ background: "var(--rp-highlight-med)", color: "var(--rp-text)" }}
            onClick={() => this.setState({ hasError: false })}
          >
            Dismiss
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}