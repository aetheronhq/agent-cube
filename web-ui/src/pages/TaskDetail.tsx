import type { JSX } from "react";
import { useEffect, useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { DualLayout } from "../components/DualLayout";
import { TripleLayout } from "../components/TripleLayout";
import { OutputStream } from "../components/OutputStream";
import { WorkflowTimeline } from "../components/WorkflowTimeline";
import { PromptsPanel } from "../components/PromptsPanel";
import { useSSE } from "../hooks/useSSE";
import type {
  OutputMessage,
  SSEMessage,
  StatusMessage,
  ThinkingMessage,
  WorkflowState,
} from "../types";

const API_BASE_URL =
  ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:3030/api").replace(/\/$/, "");

function isThinkingMessage(message: SSEMessage): message is ThinkingMessage {
  return message.type === "thinking" && typeof message.text === "string";
}

function isOutputMessage(message: SSEMessage): message is OutputMessage {
  return message.type === "output" && typeof message.content === "string";
}

function isStatusMessage(message: SSEMessage): message is StatusMessage {
  return message.type === "status" && typeof message.status === "string";
}

function formatUpdatedAt(value?: string): string {
  if (!value) {
    return "Unknown";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default function TaskDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = (id ?? "").trim();
  const [task, setTask] = useState<WorkflowState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [historicalMessages, setHistoricalMessages] = useState<SSEMessage[]>([]);
  const streamUrl = taskId ? `${API_BASE_URL}/tasks/${encodeURIComponent(taskId)}/stream` : null;

  const { messages, connected, error: streamError } = useSSE(streamUrl, { 
    enabled: Boolean(taskId),
    initialMessages: historicalMessages
  });

  useEffect(() => {
    if (!taskId) {
      return;
    }

    const loadHistoricalLogs = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/tasks/${encodeURIComponent(taskId)}/logs`);
        if (!res.ok) return;
        
        const data = await res.json();
        const parsed: SSEMessage[] = [];
        
        const inferBoxFromFilename = (filename: string): string => {
          if (filename.startsWith('writer-opus')) return 'writer-a';
          if (filename.startsWith('writer-codex')) return 'writer-b';
          // Judge files can be: judge-1-01-task-panel.json OR judge_1-task-panel.json
          const judgeMatch = filename.match(/^judge[-_](\d+)[-_]/);
          if (judgeMatch) return `judge-${judgeMatch[1]}`;
          return 'unknown';
        };
        
        const boxToAgent = (box: string): string | undefined => {
          if (box === 'writer-a') return 'Writer A';
          if (box === 'writer-b') return 'Writer B';
          const match = box.match(/^judge-(\d+)$/);
          if (match) return `Judge ${match[1]}`;
          return undefined;
        };
        
        for (const logEntry of data.logs || []) {
          const inferredBox = inferBoxFromFilename(logEntry.file || '');
          const lines = logEntry.content.split('\n');
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const msg = JSON.parse(line);
              if (msg.type === 'thinking' && msg.text) {
                parsed.push({
                  type: 'thinking',
                  box: msg.box || inferredBox,
                  text: msg.text,
                  timestamp: msg.timestamp || new Date().toISOString()
                });
              } else if (msg.type === 'tool_call' || msg.type === 'result') {
                const box = msg.box || inferredBox;
                const agent = boxToAgent(box);
                parsed.push({
                  type: 'output',
                  agent,
                  content: `${msg.type}: ${JSON.stringify(msg).substring(0, 100)}...`,
                  timestamp: msg.timestamp || new Date().toISOString()
                });
              }
            } catch {}
          }
        }
        
        setHistoricalMessages(parsed);
      } catch {}
    };

    loadHistoricalLogs();
  }, [taskId]);

  useEffect(() => {
    if (!taskId) {
      setTask(null);
      setLoading(false);
      setError("Task id missing");
      return;
    }

    const controller = new AbortController();

    const fetchTask = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/tasks/${encodeURIComponent(taskId)}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Failed to load task (${response.status})`);
        }
        const data = (await response.json()) as WorkflowState;
        setTask(data);
        setError(null);
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        const message = err instanceof Error ? err.message : "Unable to load task";
        setError(message);
        setTask(null);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    fetchTask();

    return () => {
      controller.abort();
    };
  }, [taskId]);

  const thinkingMessages = useMemo(() => messages.filter(isThinkingMessage), [messages]);
  const outputMessages = useMemo(() => messages.filter(isOutputMessage), [messages]);
  const statusMessages = useMemo(() => messages.filter(isStatusMessage), [messages]);

  const writerALines = useMemo(
    () => thinkingMessages.filter((message) => message.box === "writer-a").map((message) => message.text),
    [thinkingMessages],
  );
  const writerBLines = useMemo(
    () => thinkingMessages.filter((message) => message.box === "writer-b").map((message) => message.text),
    [thinkingMessages],
  );
  const judge1Lines = useMemo(
    () => thinkingMessages.filter((message) => message.box === "judge-1").map((message) => message.text),
    [thinkingMessages],
  );
  const judge2Lines = useMemo(
    () => thinkingMessages.filter((message) => message.box === "judge-2").map((message) => message.text),
    [thinkingMessages],
  );
  const judge3Lines = useMemo(
    () => thinkingMessages.filter((message) => message.box === "judge-3").map((message) => message.text),
    [thinkingMessages],
  );

  const latestStatus = statusMessages.at(-1);
  const currentPhase = task?.current_phase ?? 1;
  const showTripleLayout = currentPhase >= 3;

  return (
    <div className="h-full flex flex-col gap-4 min-h-0">
      <div className="flex flex-wrap items-center justify-between gap-4 shrink-0">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <h1 className="text-2xl font-bold">Task {taskId || "Unknown Task"}</h1>
            <Link 
              to={`/tasks/${taskId}/decisions`}
              className="text-sm px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
            >
              View Decisions →
            </Link>
          </div>
          <div className="text-sm text-gray-400">
            <span className="mr-4">Phase {currentPhase}/10</span>
            <span className="mr-4 capitalize">Path: {task?.path?.toLowerCase() ?? "unknown"}</span>
            <span>Updated: {formatUpdatedAt(task?.updated_at)}</span>
          </div>
        </div>
        <div className="flex flex-col items-end text-sm text-gray-300">
          <div className="flex items-center gap-4">
            <span className="text-xs text-gray-500">
              {outputMessages.length} events • {thinkingMessages.length} thoughts
            </span>
            <div className="flex items-center gap-2">
              <span
                className={`h-2.5 w-2.5 rounded-full ${connected ? "bg-emerald-400" : "bg-red-500"} transition-colors`}
              />
              <span>{connected ? "Live" : "Offline"}</span>
            </div>
          </div>
          {streamError && <span className="text-xs text-red-400 mt-1">Stream error: {streamError}</span>}
          {latestStatus && (
            <span className="text-xs text-gray-400 mt-1">
              Status: <span className="capitalize">{latestStatus.status.replace(/-/g, " ")}</span>
            </span>
          )}
        </div>
      </div>

      <div className="shrink-0">
        <WorkflowTimeline currentPhase={currentPhase} path={task?.path} />
      </div>

      {loading ? (
        <div className="rounded border border-gray-700 bg-gray-900/80 p-6 text-gray-400">Loading task details…</div>
      ) : error ? (
        <div className="rounded border border-red-700/60 bg-red-950/40 p-6 text-red-300">Error: {error}</div>
      ) : task ? (
        <>
          <div className="shrink-0">
            {showTripleLayout ? (
              <TripleLayout judge1Lines={judge1Lines} judge2Lines={judge2Lines} judge3Lines={judge3Lines} />
            ) : (
              <DualLayout writerALines={writerALines} writerBLines={writerBLines} />
            )}
          </div>

          <div className="flex-1 flex flex-col gap-2 min-h-0">
            <div className="shrink-0 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Output Stream</h2>
                <p className="text-xs text-gray-500">Live tool calls and agent events stream here in real time.</p>
              </div>
            </div>
            <OutputStream messages={outputMessages} className="flex-1 min-h-0" />
          </div>

          {/* Floating Prompts Panel */}
          <PromptsPanel taskId={taskId || ""} />
        </>
      ) : (
        <div className="rounded border border-gray-700 bg-gray-900/80 p-6 text-gray-400">
          Task metadata unavailable. Streaming will continue if events arrive.
        </div>
      )}
    </div>
  );
}
