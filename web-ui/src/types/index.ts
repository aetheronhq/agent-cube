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

export interface JudgeVote {
  judge: number;
  model: string;
  vote: string;
  rationale: string;
  scores?: {
    writer_a: number;
    writer_b: number;
  };
  timestamp?: string;
}

export interface SynthesisInfo {
  instructions: string[];
  bestBits: {
    writerA: string[];
    writerB: string[];
  };
  compatible: boolean;
}

export interface Decision {
  type: "panel" | "peer-review";
  judges: JudgeVote[];
  winner?: string;
  consensus?: boolean;
  synthesis?: SynthesisInfo;
  timestamp: string;
  aggregated?: {
    avg_score_a: number;
    avg_score_b: number;
    next_action: string;
    blocker_issues: string[];
  };
}
