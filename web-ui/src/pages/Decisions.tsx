import type { JSX } from "react";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { JudgeVote } from "../components/JudgeVote";
import { SynthesisView } from "../components/SynthesisView";
import type { Decision } from "../types";

type VoteSummary = Record<string, number>;

const DECISION_BADGE_STYLES = {
  panel: "bg-purple-600 text-white",
  "peer-review": "bg-teal-600 text-white",
} as const;

function formatTimestamp(timestamp: string): string {
  if (!timestamp) {
    return "Unknown";
  }

  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString();
}

function calculateConsensus(decision: Decision): boolean {
  if (decision.judges.length === 0) {
    return false;
  }

  const firstVote = decision.judges[0]?.vote;
  return decision.judges.every((judge) => judge.vote === firstVote);
}

export function Decisions(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const taskId = id ?? "";

  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) {
      setError("Task id is missing.");
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    setLoading(true);
    setError(null);

    fetch(`http://localhost:3030/api/tasks/${taskId}/decisions`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("No decisions found for this task.");
          }
          throw new Error("Failed to fetch decisions.");
        }
        return response.json();
      })
      .then((payload) => {
        const results = Array.isArray(payload.decisions)
          ? (payload.decisions as Decision[])
          : [];
        setDecisions(results);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }

        const message =
          err instanceof Error ? err.message : "Failed to fetch decisions.";
        setError(message);
        setDecisions([]);
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [taskId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-sm text-gray-400">Loading decisions…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4 py-12 text-center">
        <div className="text-red-400">⚠️ {error}</div>
        {taskId && (
          <p className="text-sm text-gray-500">
            Run the judge panel first:{" "}
            <code className="rounded bg-gray-900 px-2 py-1 text-xs text-gray-200">
              cube panel {taskId}
            </code>
          </p>
        )}
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <div className="space-y-4 py-12 text-center text-gray-400">
        <p>No decisions recorded for this task yet.</p>
        {taskId && (
          <p className="text-sm text-gray-500">
            Run:{" "}
            <code className="rounded bg-gray-900 px-2 py-1 text-xs text-gray-200">
              cube panel {taskId}
            </code>
          </p>
        )}
      </div>
    );
  }

  const latestDecision = decisions[decisions.length - 1];
  const badgeStyle =
    DECISION_BADGE_STYLES[latestDecision.type] ?? "bg-gray-600 text-white";
  const consensus = calculateConsensus(latestDecision);

  const voteSummary = useMemo<VoteSummary>(() => {
    return latestDecision.judges.reduce<VoteSummary>((acc, judge) => {
      acc[judge.vote] = (acc[judge.vote] ?? 0) + 1;
      return acc;
    }, {});
  }, [latestDecision]);

  return (
    <div className="space-y-8 px-4 pb-12 pt-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-gray-100">
          Decisions • {taskId}
        </h1>
        <p className="text-sm text-gray-500">
          Viewing the latest recorded decision for this task.
        </p>
      </header>

      <section className="rounded-lg border border-gray-800 bg-gray-900 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-100">
              Decision Summary
            </h2>
            <p className="text-sm text-gray-400">
              Last updated {formatTimestamp(latestDecision.timestamp)}
            </p>
          </div>
          <span
            className={`rounded px-3 py-1 text-xs font-semibold uppercase tracking-wide ${badgeStyle}`}
          >
            {latestDecision.type === "panel" ? "Panel Decision" : "Peer Review"}
          </span>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Consensus
            </p>
            <p className="mt-1 text-lg font-semibold text-gray-100">
              {consensus ? "Yes" : "No"}
            </p>
            <p className="text-xs text-gray-500">
              {consensus
                ? "All judges aligned on the same outcome."
                : "Judges provided differing feedback."}
            </p>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Winner
            </p>
            <p className="mt-1 text-lg font-semibold text-gray-100">
              {latestDecision.winner
                ? `Writer ${latestDecision.winner}`
                : "No winner selected"}
            </p>
            <p className="text-xs text-gray-500">
              {latestDecision.type === "panel"
                ? "Panel decisions choose between Writer A and Writer B."
                : "Peer review decisions provide feedback without selecting a winner."}
            </p>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Judges
            </p>
            <p className="mt-1 text-lg font-semibold text-gray-100">
              {latestDecision.judges.length}
            </p>
            <p className="text-xs text-gray-500">
              Individual votes recorded for this decision.
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Vote Breakdown
          </p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(voteSummary).map(([voteType, count]) => (
              <span
                key={voteType}
                className="rounded border border-gray-800 bg-gray-950 px-3 py-1 text-xs text-gray-300"
              >
                {voteType}: {count}
              </span>
            ))}
          </div>
        </div>

        {decisions.length > 1 && (
          <p className="mt-6 text-xs text-gray-500">
            Showing the latest decision out of {decisions.length} records.
          </p>
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-100">Judge Votes</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {latestDecision.judges.map((judgeVote) => (
            <JudgeVote key={judgeVote.judge} vote={judgeVote} />
          ))}
        </div>
      </section>

      {latestDecision.synthesis && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-100">Synthesis</h2>
          <SynthesisView synthesis={latestDecision.synthesis} />
        </section>
      )}
    </div>
  );
}
