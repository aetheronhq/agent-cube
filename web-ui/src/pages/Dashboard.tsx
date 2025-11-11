import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { TaskCard } from "../components/TaskCard";
import type { Task, TasksResponse } from "../types";

const TASKS_ENDPOINT = "http://localhost:3030/api/tasks";
const POLL_INTERVAL_MS = 5000;

export default function Dashboard(): JSX.Element {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isMountedRef = useRef(true);
  const controllersRef = useRef<Set<AbortController>>(new Set());

  useEffect(() => {
    const controllers = controllersRef.current;
    return () => {
      isMountedRef.current = false;
      controllers.forEach((controller) => controller.abort());
      controllers.clear();
    };
  }, []);

  const fetchTasks = useCallback(
    async (options?: { withLoading?: boolean }) => {
      const controller = new AbortController();
      controllersRef.current.add(controller);

      if (options?.withLoading) {
        setLoading(true);
        setError(null);
      }

      try {
        const response = await fetch(TASKS_ENDPOINT, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch tasks (${response.status})`);
        }
        const data: TasksResponse = await response.json();
        if (!isMountedRef.current) return;
        setTasks(Array.isArray(data.tasks) ? data.tasks : []);
        setError(null);
      } catch (err) {
        if (controller.signal.aborted || !isMountedRef.current) return;
        const message =
          err instanceof Error ? err.message : "Unexpected error fetching tasks";
        setError(message);
      } finally {
        controllersRef.current.delete(controller);
        if (isMountedRef.current) {
          setLoading(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    void fetchTasks({ withLoading: true });
    const intervalId = window.setInterval(() => {
      void fetchTasks();
    }, POLL_INTERVAL_MS);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [fetchTasks]);

  const activeCount = useMemo(
    () =>
      tasks.filter((task) => (task.status ?? "active") === "active").length,
    [tasks],
  );

  const completedCount = useMemo(
    () => tasks.filter((task) => task.status === "completed").length,
    [tasks],
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-12 text-gray-400">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-600 border-t-transparent" />
        <p className="text-sm font-medium">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-12 text-red-400">
        <p className="text-base font-semibold">Unable to load tasks</p>
        <p className="text-sm text-red-300">{error}</p>
        <button
          type="button"
          className="rounded border border-red-500 px-3 py-1 text-sm font-medium text-red-100 transition-colors hover:border-red-400 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 focus-visible:ring-offset-stone-900"
          onClick={() => {
            void fetchTasks({ withLoading: true });
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="mx-auto max-w-lg rounded-lg border border-dashed border-gray-700 bg-cube-gray/60 px-6 py-12 text-center">
        <h2 className="text-xl font-semibold text-white">No tasks yet</h2>
        <p className="mt-2 text-sm text-gray-400">
          Start a new Agent Cube workflow to see it appear here.
        </p>
        <p className="mt-4 text-xs font-mono text-gray-500">
          cube auto &lt;task-file&gt;
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">AgentCube Dashboard</h1>
        <p className="text-sm text-gray-400">
          Monitor active workflows and jump into details.
        </p>
      </header>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-700 bg-cube-gray p-4 shadow-sm">
          <p className="text-sm text-gray-400">Active Tasks</p>
          <p className="mt-2 text-3xl font-semibold text-green-500">{activeCount}</p>
        </div>
        <div className="rounded-lg border border-gray-700 bg-cube-gray p-4 shadow-sm">
          <p className="text-sm text-gray-400">Completed Tasks</p>
          <p className="mt-2 text-3xl font-semibold text-blue-500">
            {completedCount}
          </p>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">All Tasks</h2>
          <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Updated every 5 seconds
          </span>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      </section>
    </div>
  );
}
