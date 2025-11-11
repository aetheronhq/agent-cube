import { useState, useEffect } from 'react';

export interface SSEMessage {
  type: string;
  box?: string;
  agent?: string;
  content?: string;
  text?: string;
  timestamp: string;
}

export function useSSE(url: string) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setConnected(true);
    };

    eventSource.onmessage = (event) => {
      try {
        const msg: SSEMessage = JSON.parse(event.data);
        if (msg.type !== 'heartbeat') {
          setMessages((prev) => [...prev, msg]);
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();
      
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    return () => {
      eventSource.close();
    };
  }, [url]);

  return { messages, connected };
}
