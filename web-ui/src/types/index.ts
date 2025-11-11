// Shared TypeScript types
// More types will be added in future tasks

export interface Task {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
}

export interface ThinkingLine {
  text: string;
  timestamp: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  color: string;
  icon: string;
}

export interface ThinkingBoxProps {
  title: string;
  lines: string[];
  icon: string;
  color?: string;
}
