import { useEffect, useMemo, useRef } from "react";
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
  const endRef = useRef<HTMLDivElement | null>(null);
  const latestMessages = useMemo(() => messages.slice(-400), [messages]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [latestMessages]);

  return (
    <div
      className={`border border-gray-700 rounded-lg bg-gray-900/90 p-4 h-96 overflow-y-auto font-mono text-xs space-y-1 ${className ?? ""}`}
    >
      {latestMessages.length === 0 ? (
        <p className="text-gray-500">No output yet.</p>
      ) : (
        latestMessages.map((message, index) => {
          const agentColor = message.agent ? AGENT_COLOR_MAP[message.agent] ?? "text-gray-200" : "text-gray-200";
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
  );
}
