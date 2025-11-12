import type { JSX } from "react";
import { useState, useEffect } from "react";
import { TaskCard } from "../components/TaskCard";
import type { Task, TasksResponse } from "../types";

export default function Dashboard(): JSX.Element {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await fetch("http://localhost:3030/api/tasks");
        if (!res.ok) throw new Error("Failed to fetch tasks");
        const data: TasksResponse = await res.json();
        setTasks(data.tasks);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400">Loading tasks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400">
        <div className="text-lg font-semibold mb-2">Error</div>
        <div className="text-sm">{error}</div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg mb-2">No tasks yet</p>
        <p className="text-sm">Start a task with: cube auto &lt;task-file&gt;</p>
      </div>
    );
  }

  // Task is complete when peer review passes or workflow fully done
  const isCompleted = (task: Task) => {
    if (task.current_phase >= 10) return true;
    if (task.workflow_status === "peer-review-complete") return true;
    if (task.workflow_status === "complete") return true;
    return false;
  };
  const activeTasks = tasks.filter((t) => !isCompleted(t));
  const completedTasks = tasks.filter((t) => isCompleted(t));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">AgentCube Dashboard</h1>

      <div className="mb-8 grid grid-cols-2 gap-4">
        <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
          <div className="text-2xl font-bold text-green-500">
            {activeTasks.length}
          </div>
          <div className="text-sm text-gray-400">Active Tasks</div>
        </div>
        <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
          <div className="text-2xl font-bold text-blue-500">
            {completedTasks.length}
          </div>
          <div className="text-sm text-gray-400">Completed Tasks</div>
        </div>
      </div>

      <h2 className="text-xl font-bold mb-4">All Tasks</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}
