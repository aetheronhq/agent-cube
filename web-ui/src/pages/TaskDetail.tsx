import type { JSX } from "react";
import { useParams } from "react-router-dom";

export default function TaskDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "unknown";

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Task {taskId}</h1>
      <p className="text-gray-400">Thinking boxes coming soon...</p>
    </div>
  );
}
