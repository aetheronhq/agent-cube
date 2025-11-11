import type { JSX } from "react";
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { JudgeVote } from "../components/JudgeVote";
import { SynthesisView } from "../components/SynthesisView";
import type { Decision } from "../types";

export default function Decisions(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "unknown";
  const [decision, setDecision] = useState<Decision | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:3030/api/tasks/${taskId}/decisions`)
      .then((res) => {
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error("No decisions found for this task");
          }
          throw new Error("Failed to fetch decisions");
        }
        return res.json();
      })
      .then((data) => {
        setDecision(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [taskId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Loading decisions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-400 mb-2">⚠️ {error}</div>
        <p className="text-gray-500 text-sm">
          Run the judge panel first:{" "}
          <code className="bg-gray-800 px-2 py-1 rounded">
            cube panel {taskId}
          </code>
        </p>
      </div>
    );
  }

  if (!decision || !decision.judges || decision.judges.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="mb-2">No decisions yet</p>
        <p className="text-sm text-gray-500">
          Run:{" "}
          <code className="bg-gray-800 px-2 py-1 rounded">
            cube panel {taskId}
          </code>
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-100">
        Decisions: {taskId}
      </h1>

      <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
        <h2 className="text-lg font-semibold text-gray-100 mb-3">
          Decision Summary
        </h2>
        <div className="text-sm text-gray-300 space-y-1">
          <p>
            <span className="text-gray-500">Type:</span>{" "}
            <span className="font-semibold">{decision.type}</span>
          </p>
          {decision.winner && (
            <p>
              <span className="text-gray-500">Winner:</span>{" "}
              <span className="font-semibold text-green-400">
                Writer {decision.winner}
              </span>
            </p>
          )}
          {decision.consensus !== undefined && (
            <p>
              <span className="text-gray-500">Consensus:</span>{" "}
              <span
                className={
                  decision.consensus ? "text-green-400" : "text-yellow-400"
                }
              >
                {decision.consensus ? "✅ Yes" : "⚠️ No"}
              </span>
            </p>
          )}
          <p>
            <span className="text-gray-500">Timestamp:</span>{" "}
            {new Date(decision.timestamp).toLocaleString()}
          </p>
          {decision.aggregated && (
            <>
              <p>
                <span className="text-gray-500">Average Score A:</span>{" "}
                <span className="text-gray-200">
                  {decision.aggregated.avg_score_a.toFixed(1)}
                </span>
              </p>
              <p>
                <span className="text-gray-500">Average Score B:</span>{" "}
                <span className="text-gray-200">
                  {decision.aggregated.avg_score_b.toFixed(1)}
                </span>
              </p>
              <p>
                <span className="text-gray-500">Next Action:</span>{" "}
                <span className="font-semibold text-blue-400">
                  {decision.aggregated.next_action}
                </span>
              </p>
            </>
          )}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-100 mb-3">
          Judge Votes
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {decision.judges.map((vote) => (
            <JudgeVote key={vote.judge} vote={vote} />
          ))}
        </div>
      </div>

      {decision.synthesis && (
        <div>
          <h2 className="text-lg font-semibold text-gray-100 mb-3">
            Synthesis
          </h2>
          <SynthesisView synthesis={decision.synthesis} />
        </div>
      )}

      {decision.aggregated?.blocker_issues &&
        decision.aggregated.blocker_issues.length > 0 && (
          <div className="border border-red-900 rounded-lg p-4 bg-red-950">
            <h2 className="text-lg font-semibold text-red-300 mb-3">
              ⚠️ Blocker Issues
            </h2>
            <ul className="list-disc list-inside space-y-2 text-sm text-red-200">
              {decision.aggregated.blocker_issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}
    </div>
  );
}
