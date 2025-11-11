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

export interface SSEMessage {
  type: string;
  box?: string;
  agent?: string;
  content?: string;
  text?: string;
  timestamp: string;
}
