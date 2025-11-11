import type { JSX } from "react";
import { useNavigate } from "react-router-dom";
import type { Task } from "../types";

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps): JSX.Element {
  const navigate = useNavigate();

  const statusColor =
    task.status === "completed"
      ? "bg-blue-600"
      : task.status === "failed"
        ? "bg-red-600"
        : "bg-green-600";

  const progressPercentage = (task.phase / 10) * 100;

  return (
    <div
      onClick={() => navigate(`/tasks/${task.id}`)}
      className="border border-gray-700 rounded-lg p-4 hover:border-gray-500 cursor-pointer transition-colors bg-cube-gray"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-white">{task.id}</h3>
        <span className={`text-xs px-2 py-1 rounded text-white ${statusColor}`}>
          {task.status || "active"}
        </span>
      </div>

      <div className="text-sm text-gray-400 mb-2">Phase {task.phase}/10</div>

      <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      <div className="mt-2 text-xs text-gray-500 truncate" title={task.path}>
        {task.path}
      </div>
    </div>
  );
}
