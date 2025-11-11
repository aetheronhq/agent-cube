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

export interface WorkflowState {
  task_id: string;
  current_phase: number;
  path: string;
  completed_phases: number[];
  winner?: string | null;
  next_action?: string | null;
  writers_complete: boolean;
  panel_complete: boolean;
  synthesis_complete: boolean;
  peer_review_complete: boolean;
  updated_at?: string;
}

export type SSEMessageType = "thinking" | "output" | "status" | "heartbeat";

export interface SSEMessage {
  type: SSEMessageType;
  taskId?: string;
  box?: string;
  agent?: string;
  text?: string;
  content?: string;
  status?: string;
  error?: string;
  resume?: boolean;
  reviewType?: string;
  timestamp: string;
}

export type ThinkingMessage = SSEMessage & {
  type: "thinking";
  text: string;
};

export type OutputMessage = SSEMessage & {
  type: "output";
  content: string;
};

export type StatusMessage = SSEMessage & {
  type: "status";
  status: string;
};
