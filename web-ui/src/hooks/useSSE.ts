import { useEffect, useMemo, useRef, useState } from "react";
import type { SSEMessage } from "../types";

interface UseSSEOptions {
  enabled?: boolean;
  reconnectDelayMs?: number;
  maxMessages?: number;
}

interface UseSSEResult {
  messages: SSEMessage[];
  connected: boolean;
  error?: string;
}

const DEFAULT_RECONNECT_DELAY = 3000;
const DEFAULT_MAX_MESSAGES = 1000;

export function useSSE(
  url: string | null,
  { enabled = true, reconnectDelayMs = DEFAULT_RECONNECT_DELAY, maxMessages = DEFAULT_MAX_MESSAGES }: UseSSEOptions = {},
): UseSSEResult {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string>();
  const retryTimerRef = useRef<number>();
  const eventSourceRef = useRef<EventSource | null>(null);
  const normalizedUrl = useMemo(() => (url ? url.replace(/\s+/g, "") : null), [url]);
  const previousUrlRef = useRef<string | null>(null);

  useEffect(() => {
    if (normalizedUrl !== previousUrlRef.current) {
      previousUrlRef.current = normalizedUrl;
      setMessages([]);
    }
  }, [normalizedUrl]);

  useEffect(() => {
    if (!normalizedUrl || !enabled) {
      setConnected(false);
      setMessages([]);
      return;
    }

    let cancelled = false;

    const cleanupTimers = () => {
      if (retryTimerRef.current) {
        window.clearTimeout(retryTimerRef.current);
        retryTimerRef.current = undefined;
      }
    };

    const closeCurrentSource = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };

    const appendMessage = (incoming: SSEMessage) => {
      setMessages((prev) => {
        const next = [...prev, incoming];
        if (next.length > maxMessages) {
          next.splice(0, next.length - maxMessages);
        }
        return next;
      });
    };

    const connect = () => {
      if (cancelled || !normalizedUrl) {
        return;
      }

      try {
        const source = new EventSource(normalizedUrl);
        eventSourceRef.current = source;
        setError(undefined);

        source.onopen = () => {
          if (!cancelled) {
            setConnected(true);
          }
        };

        source.onmessage = (event) => {
          if (!event.data) {
            return;
          }
          try {
            const parsed = JSON.parse(event.data) as SSEMessage;
            if (!parsed.timestamp) {
              parsed.timestamp = new Date().toISOString();
            }
            if (parsed.type !== "heartbeat") {
              appendMessage(parsed);
            }
          } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to parse SSE message");
          }
        };

        source.onerror = () => {
          if (cancelled) {
            return;
          }
          setConnected(false);
          closeCurrentSource();

          cleanupTimers();
          retryTimerRef.current = window.setTimeout(connect, reconnectDelayMs);
        };
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to connect to SSE stream");
        cleanupTimers();
        retryTimerRef.current = window.setTimeout(connect, reconnectDelayMs);
      }
    };

    connect();

    return () => {
      cancelled = true;
      cleanupTimers();
      closeCurrentSource();
    };
  }, [enabled, maxMessages, normalizedUrl, reconnectDelayMs]);

  return { messages, connected, error };
}
