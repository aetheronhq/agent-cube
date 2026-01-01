import type { JSX } from "react";
import { useEffect, useState } from "react";

interface PromptData {
  filename: string;
  content: string;
  truncated: boolean;
}

interface PromptsResponse {
  prompts: Record<string, PromptData>;
}

interface PromptsPanelProps {
  taskId: string;
}

const PROMPT_LABELS: Record<string, string> = {
  writer: "Writer Prompt",
  panel: "Panel Prompt",
  synthesis: "Synthesis Instructions",
  peer_review: "Peer Review Prompt",
  feedback_a: "Feedback A",
  feedback_b: "Feedback B",
};

function formatPromptLabel(key: string): string {
  if (PROMPT_LABELS[key]) return PROMPT_LABELS[key];
  // Convert kebab-case or snake_case to Title Case
  return key
    .replace(/[-_]/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

const API_BASE_URL = "http://localhost:3030/api";

export function PromptsPanel({ taskId }: PromptsPanelProps): JSX.Element {
  const [prompts, setPrompts] = useState<Record<string, PromptData>>({});
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!taskId) return;

    fetch(`${API_BASE_URL}/tasks/${taskId}/prompts`)
      .then((res) => res.json())
      .then((data: PromptsResponse) => {
        setPrompts(data.prompts || {});
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [taskId]);

  const promptKeys = Object.keys(prompts);
  const hasPrompts = promptKeys.length > 0;

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full shadow-lg shadow-indigo-900/50 transition-all hover:scale-105 active:scale-95"
        title="View prompts"
      >
        <span>📝</span>
        <span className="font-medium">Prompts</span>
        {hasPrompts && (
          <span className="bg-indigo-400/30 px-2 py-0.5 rounded-full text-xs">
            {promptKeys.length}
          </span>
        )}
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Slide-out Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-xl bg-gray-900 border-l border-gray-700 shadow-2xl z-50 transform transition-transform duration-300 ease-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Panel Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gray-900/95 sticky top-0">
          <div className="flex items-center gap-3">
            <span className="text-xl">📝</span>
            <div>
              <h2 className="text-lg font-semibold text-white">Prompts</h2>
              <p className="text-xs text-gray-500">
                Instructions sent to each agent
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Panel Content */}
        <div className="h-full overflow-y-auto pb-24">
          {loading ? (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-gray-600 border-t-indigo-500 rounded-full animate-spin" />
                <span>Loading prompts...</span>
              </div>
            </div>
          ) : !hasPrompts ? (
            <div className="flex flex-col items-center justify-center h-48 text-gray-500">
              <span className="text-4xl mb-3 opacity-50">📭</span>
              <p>No prompts generated yet</p>
              <p className="text-xs text-gray-600 mt-1">
                Prompts appear after each phase starts
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {promptKeys.map((key) => {
                const prompt = prompts[key];
                const isExpanded = expanded === key;
                const label = formatPromptLabel(key);

                return (
                  <div key={key}>
                    <button
                      onClick={() => setExpanded(isExpanded ? null : key)}
                      className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-800/50 transition-colors group"
                    >
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-200 group-hover:text-white transition-colors">
                            {label}
                          </span>
                          {prompt.truncated && (
                            <span className="text-xs px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
                              truncated
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-gray-600 font-mono">
                          {prompt.filename}
                        </span>
                      </div>
                      <div className={`transform transition-transform ${isExpanded ? "rotate-180" : ""}`}>
                        <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="px-6 pb-4">
                        <div className="relative">
                          <pre className="text-xs text-gray-300 bg-gray-950 border border-gray-800 rounded-lg p-4 overflow-x-auto max-h-[60vh] overflow-y-auto whitespace-pre-wrap font-mono leading-relaxed">
                            {prompt.content}
                          </pre>
                          <button
                            onClick={() => navigator.clipboard.writeText(prompt.content)}
                            className="absolute top-2 right-2 px-2 py-1 text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white rounded transition-colors"
                            title="Copy to clipboard"
                          >
                            📋 Copy
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
