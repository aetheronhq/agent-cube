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

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-gray-800 bg-gray-900 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-100">
            Judge {vote.judge}
          </h3>
          <p className="text-xs text-gray-400">{vote.model}</p>
        </div>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold uppercase tracking-wide ${badgeColor}`}
        >
          {vote.vote}
        </span>
      </div>
      <p className="text-sm leading-relaxed text-gray-300">{vote.rationale}</p>
    </div>
  );
}
