import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { Task } from "../types";

interface TaskCardProps {
  task: Task;
}

const STATUS_BADGE_CLASS: Record<
  NonNullable<Task["status"]>,
  string
> = {
  active: "bg-green-600",
  completed: "bg-blue-600",
  failed: "bg-red-600",
};

export function TaskCard({ task }: TaskCardProps): JSX.Element {
  const navigate = useNavigate();

  const status = task.status ?? "active";
  const badgeColor =
    STATUS_BADGE_CLASS[status] ?? STATUS_BADGE_CLASS.active;

  const progress = useMemo(() => {
    const clampedPhase = Math.min(Math.max(task.phase ?? 0, 0), 10);
    const percentage = (clampedPhase / 10) * 100;
    return Number.isFinite(percentage) ? percentage : 0;
  }, [task.phase]);

  return (
    <button
      type="button"
      onClick={() => navigate(`/tasks/${task.id}`)}
      className="flex w-full flex-col gap-3 rounded-lg border border-gray-700 bg-cube-gray p-4 text-left shadow-sm transition-colors hover:border-gray-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-stone-900"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col">
          <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Task
          </span>
          <span className="text-base font-semibold text-white">
            {task.id}
          </span>
        </div>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold capitalize text-white ${badgeColor}`}
        >
          {status}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Phase</span>
          <span className="font-medium text-white">
            {task.phase}/10
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
          <div
            className="h-full rounded-full bg-blue-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Decision Path
        </span>
        <span
          className="truncate text-xs text-gray-400"
          title={task.path}
        >
          {task.path}
        </span>
      </div>
    </button>
  );
}
