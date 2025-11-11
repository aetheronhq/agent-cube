export interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface ThinkingBox {
  id: string;
  agent: string;
  lines: string[];
}
