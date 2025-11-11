import type { JSX } from "react";
import { useParams } from "react-router-dom";

export default function Decisions(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "unknown";

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Decisions - Task {taskId}</h1>
      <p className="text-gray-400">Judge panel coming soon...</p>
    </div>
  );
}
