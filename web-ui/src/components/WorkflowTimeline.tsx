import type { JSX } from "react";

interface WorkflowTimelineProps {
  currentPhase: number;
  path?: string;
}

interface Step {
  phase: number;
  label: string;
  shortLabel: string;
  description: string;
}

const WORKFLOW_STEPS: Step[] = [
  { phase: 1, label: "Prompt", shortLabel: "Prompt", description: "Prompter generates detailed instructions for writers" },
  { phase: 2, label: "Writers", shortLabel: "Writers", description: "Two AI writers implement the task in parallel" },
  { phase: 3, label: "Panel", shortLabel: "Panel", description: "Three judges review both implementations and vote" },
  { phase: 4, label: "Decision", shortLabel: "Decide", description: "Aggregate votes and determine winning approach" },
  { phase: 5, label: "Feedback", shortLabel: "Feedback", description: "Generate synthesis feedback for the winner" },
  { phase: 6, label: "Synthesis", shortLabel: "Synth", description: "Winner applies synthesis of best ideas from both" },
  { phase: 7, label: "Review", shortLabel: "Review", description: "Peer review of the synthesized implementation" },
  { phase: 8, label: "Complete", shortLabel: "Done", description: "Task approved and ready for merge" },
];

function getStepStatus(stepPhase: number, currentPhase: number): "completed" | "current" | "pending" {
  if (stepPhase < currentPhase) return "completed";
  if (stepPhase === currentPhase) return "current";
  return "pending";
}

export function WorkflowTimeline({ currentPhase, path }: WorkflowTimelineProps): JSX.Element {
  const currentStep = WORKFLOW_STEPS.find(s => s.phase === currentPhase);
  
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {WORKFLOW_STEPS.map((step, idx) => {
          const status = getStepStatus(step.phase, currentPhase);
          const isLast = idx === WORKFLOW_STEPS.length - 1;
          
          return (
            <div key={step.phase} className="flex items-center">
              <div
                className={`
                  flex items-center justify-center px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all
                  ${status === "completed" ? "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30" : ""}
                  ${status === "current" ? "bg-blue-600/30 text-blue-300 border border-blue-400/50 ring-2 ring-blue-400/20" : ""}
                  ${status === "pending" ? "bg-gray-800/50 text-gray-500 border border-gray-700/50" : ""}
                `}
                title={step.description}
              >
                {status === "completed" && <span className="mr-1.5">✓</span>}
                {status === "current" && <span className="mr-1.5 animate-pulse">●</span>}
                {step.shortLabel}
              </div>
              {!isLast && (
                <div
                  className={`w-4 h-0.5 mx-0.5 ${
                    status === "completed" ? "bg-emerald-500/50" : "bg-gray-700/50"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      
      {currentStep && (
        <div className="bg-gray-800/50 rounded-lg px-4 py-3 border border-gray-700/50">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-blue-400 font-medium">{currentStep.label}</span>
            {path && path !== "INIT" && (
              <span className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">
                Path: {path}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-400">{currentStep.description}</p>
        </div>
      )}
    </div>
  );
}

