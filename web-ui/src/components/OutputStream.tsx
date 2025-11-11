import type { JSX } from 'react';
import { useEffect, useRef } from 'react';

interface OutputMessage {
  agent?: string;
  content?: string;
  timestamp: string;
}

interface OutputStreamProps {
  messages: OutputMessage[];
}

export function OutputStream({ messages }: OutputStreamProps): JSX.Element {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getAgentColor = (agent?: string): string => {
    if (!agent) return 'text-gray-300';
    if (agent.includes('writer-a') || agent.includes('sonnet')) return 'text-green-400';
    if (agent.includes('writer-b') || agent.includes('codex')) return 'text-blue-400';
    if (agent.includes('judge')) return 'text-yellow-400';
    return 'text-gray-300';
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  if (messages.length === 0) {
    return (
      <div className="border border-gray-700 rounded-lg p-4 bg-gray-900 h-96 overflow-y-auto font-mono text-xs">
        <div className="text-gray-500 text-center">Waiting for output...</div>
      </div>
    );
  }

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900 h-96 overflow-y-auto font-mono text-xs">
      {messages.map((msg, i) => (
        <div key={i} className="mb-1">
          <span className="text-gray-500">[{formatTimestamp(msg.timestamp)}]</span>
          {msg.agent && <span className={getAgentColor(msg.agent)}> [{msg.agent}]</span>}
          <span className="text-gray-300"> {msg.content}</span>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
