export interface Task {
  id: string;
  phase: number;
  path: string;
  status?: "active" | "completed" | "failed";
}

export interface TasksResponse {
  tasks: Task[];
}

export interface ThinkingLine {
  text: string;
  timestamp: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  icon: string;
  color: "green" | "blue" | "gray";
}

export interface ThinkingBoxProps {
  title: string;
  lines: string[];
  icon: string;
  color?: "green" | "blue" | "gray";
}

export interface AgentThinkingSnapshot extends AgentInfo {
  lines: string[];
  lastUpdatedAt: string;
}

export interface DualLayoutProps {
  writerALines: string[];
  writerBLines: string[];
}

export interface TripleLayoutProps {
  judge1Lines: string[];
  judge2Lines: string[];
  judge3Lines: string[];
}
