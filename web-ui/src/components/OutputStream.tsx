import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { OutputMessage } from "../types";

interface OutputStreamProps {
  messages: OutputMessage[];
  className?: string;
}

const AGENT_COLOR_MAP: Record<string, string> = {
  "Writer A": "text-emerald-300",
  "Writer B": "text-sky-300",
  "Judge 1": "text-purple-300",
  "Judge 2": "text-purple-200",
  "Judge 3": "text-purple-100",
};

const RICH_COLOR_MAP: Record<string, string> = {
  green: "text-emerald-300",
  blue: "text-sky-300",
  yellow: "text-amber-300",
  purple: "text-purple-300",
  magenta: "text-pink-300",
  cyan: "text-cyan-300",
};

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "--:--:--";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function OutputStream({ messages, className }: OutputStreamProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const latestMessages = useMemo(() => messages.slice(-400), [messages]);

  const handleScroll = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const { scrollTop, scrollHeight, clientHeight } = container;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  }, []);

  const scrollToEnd = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    setAutoScroll(true);
  }, []);

  useEffect(() => {
    if (autoScroll) {
      endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [latestMessages, autoScroll]);

  return (
    <div className={`relative flex flex-col min-h-0 ${className ?? ""}`}>
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 border border-gray-700 rounded-lg bg-gray-900/90 p-4 overflow-y-auto font-mono text-xs space-y-1 min-h-[12rem]"
      >
        {latestMessages.length === 0 ? (
          <p className="text-gray-500">No output yet.</p>
        ) : (
          latestMessages.map((message, index) => {
            const defaultColor = message.agent ? AGENT_COLOR_MAP[message.agent] ?? "text-gray-200" : "text-gray-200";
            const agentColor = message.agentColor ? RICH_COLOR_MAP[message.agentColor] ?? defaultColor : defaultColor;
            return (
              <div key={`${message.timestamp}-${index}`} className="text-gray-200 leading-tight">
                <span className="text-gray-500 mr-2">[{formatTimestamp(message.timestamp)}]</span>
                {message.agent && <span className={`${agentColor} font-semibold`}>{message.agent}</span>}
                <span className="ml-2 break-words whitespace-pre-wrap">{message.content}</span>
              </div>
            );
          })
        )}
        <div ref={endRef} />
      </div>
      
      {!autoScroll && (
        <button
          onClick={scrollToEnd}
          className="absolute bottom-4 right-4 px-3 py-1.5 bg-gray-700/90 hover:bg-gray-600 text-gray-200 text-xs rounded-full shadow-lg transition-all flex items-center gap-1.5"
        >
          <span>↓</span>
          <span>Latest</span>
        </button>
      )}
    </div>
  );
}
