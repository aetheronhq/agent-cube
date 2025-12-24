import type { JSX } from "react";
import type { JudgeVote as JudgeVoteType } from "../types";

interface JudgeVoteProps {
  vote: JudgeVoteType;
}

const VOTE_COLOR_MAP: Record<JudgeVoteType["vote"], string> = {
  A: "bg-green-600 text-white",
  B: "bg-blue-600 text-white",
  APPROVE: "bg-green-600 text-white",
  REQUEST_CHANGES: "bg-red-600 text-white",
  COMMENT: "bg-yellow-400 text-gray-900",
};

export function JudgeVote({ vote }: JudgeVoteProps): JSX.Element {
  const badgeColor = VOTE_COLOR_MAP[vote.vote] ?? "bg-gray-600 text-white";
  const hasBlockers = vote.blockers && vote.blockers.length > 0;
  const hasScores = vote.scores && (vote.scores.a > 0 || vote.scores.b > 0);

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-gray-800 bg-gray-900 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-100">
            {vote.label || `Judge ${vote.judge}`}
          </h3>
          <p className="text-xs text-gray-400">{vote.model}</p>
        </div>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold uppercase tracking-wide ${badgeColor}`}
        >
          {vote.vote}
        </span>
      </div>

      {hasScores && (
        <div className="flex gap-4 text-xs">
          <span className="text-emerald-400">A: {vote.scores?.a.toFixed(1)}</span>
          <span className="text-sky-400">B: {vote.scores?.b.toFixed(1)}</span>
        </div>
      )}

      <div className="text-sm leading-relaxed text-gray-300 whitespace-pre-wrap">
        {vote.rationale || "No rationale provided"}
      </div>

      {hasBlockers && (
        <div className="mt-2 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-red-400">
            Blockers ({vote.blockers?.length})
          </p>
          <ul className="space-y-1">
            {vote.blockers?.map((blocker, idx) => (
              <li
                key={idx}
                className="text-xs text-red-300 pl-3 border-l-2 border-red-500/50"
              >
                {blocker}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
