import type { JSX } from "react";
import type { JudgeVote as JudgeVoteType } from "../types";

interface JudgeVoteProps {
  vote: JudgeVoteType;
}

export function JudgeVote({ vote }: JudgeVoteProps): JSX.Element {
  const voteColorMap: Record<string, string> = {
    A: "bg-green-600 text-white",
    B: "bg-blue-600 text-white",
    TIE: "bg-gray-600 text-white",
    APPROVE: "bg-green-600 text-white",
    REQUEST_CHANGES: "bg-red-600 text-white",
    COMMENT: "bg-yellow-600 text-black",
  };

  const voteColor = voteColorMap[vote.vote] || "bg-gray-600 text-white";

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-100">Judge {vote.judge}</h3>
          <p className="text-xs text-gray-400">{vote.model}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-bold ${voteColor}`}>
          {vote.vote}
        </span>
      </div>
      <p className="text-sm text-gray-300 mt-2">{vote.rationale}</p>
      {vote.scores && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="flex justify-between text-xs text-gray-400">
            <span>
              Writer A: <span className="text-gray-200">{vote.scores.writer_a.toFixed(1)}</span>
            </span>
            <span>
              Writer B: <span className="text-gray-200">{vote.scores.writer_b.toFixed(1)}</span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
