import type { JSX } from "react";
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { useSSE } from "../hooks/useSSE";
import { DualLayout } from "../components/DualLayout";
import { TripleLayout } from "../components/TripleLayout";
import { OutputStream } from "../components/OutputStream";

interface TaskInfo {
  task_id: string;
  current_phase: number;
  path: string;
  status: string;
}

export default function TaskDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "unknown";
  
  const [task, setTask] = useState<TaskInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { messages, connected } = useSSE(`http://localhost:3030/api/tasks/${taskId}/stream`);

  useEffect(() => {
    fetch(`http://localhost:3030/api/tasks/${taskId}`)
      .then(res => {
        if (!res.ok) {
          throw new Error(`Failed to fetch task: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        setTask(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [taskId]);

  const thinkingMessages = messages.filter(m => m.type === 'thinking');
  const outputMessages = messages.filter(m => m.type === 'output');

  const writerALines = thinkingMessages
    .filter(m => m.box === 'writer_a' || m.box === 'writer-a')
    .map(m => m.text || '');
    
  const writerBLines = thinkingMessages
    .filter(m => m.box === 'writer_b' || m.box === 'writer-b')
    .map(m => m.text || '');

  const judge1Lines = thinkingMessages
    .filter(m => m.box === 'judge_1' || m.box === 'judge-1')
    .map(m => m.text || '');
    
  const judge2Lines = thinkingMessages
    .filter(m => m.box === 'judge_2' || m.box === 'judge-2')
    .map(m => m.text || '');
    
  const judge3Lines = thinkingMessages
    .filter(m => m.box === 'judge_3' || m.box === 'judge-3')
    .map(m => m.text || '');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading task...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-400">Error: {error}</div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Task not found</div>
      </div>
    );
  }

  const isJudgePhase = task.current_phase >= 3 && task.current_phase <= 10;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">{taskId}</h1>
          <p className="text-sm text-gray-400">
            Phase {task.current_phase} • {task.status}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-400">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Thinking Boxes</h2>
        {isJudgePhase ? (
          <TripleLayout
            judge1Lines={judge1Lines}
            judge2Lines={judge2Lines}
            judge3Lines={judge3Lines}
          />
        ) : (
          <DualLayout
            writerALines={writerALines}
            writerBLines={writerBLines}
          />
        )}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-2">Output Stream</h2>
        <OutputStream messages={outputMessages} />
      </div>
    </div>
  );
}
