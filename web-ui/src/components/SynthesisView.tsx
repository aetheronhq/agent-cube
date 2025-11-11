import type { JSX } from "react";
import type { SynthesisInfo } from "../types";

interface SynthesisViewProps {
  synthesis: SynthesisInfo;
}

const STATUS_STYLES = {
  compatible: "bg-green-600 text-white",
  incompatible: "bg-red-600 text-white",
} as const;

export function SynthesisView({ synthesis }: SynthesisViewProps): JSX.Element {
  const { compatible, instructions, bestBits } = synthesis;
  const statusClass = compatible ? STATUS_STYLES.compatible : STATUS_STYLES.incompatible;

  return (
    <div className="flex flex-col gap-6 rounded-lg border border-gray-800 bg-gray-900 p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-gray-100">Synthesis Instructions</h3>
        <span className={`rounded px-3 py-1 text-xs font-semibold ${statusClass}`}>
          {compatible ? "✅ Compatible" : "❌ Not Compatible"}
        </span>
      </div>

      <div>
        <h4 className="text-sm font-semibold uppercase tracking-wide text-gray-400">
          How to merge
        </h4>
        {instructions.length > 0 ? (
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-gray-300">
            {instructions.map((instruction, index) => (
              <li key={index}>{instruction}</li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-gray-400">No synthesis instructions available.</p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
          <h4 className="mb-3 text-sm font-semibold text-green-400">
            💎 Best Bits: Writer A
          </h4>
          {bestBits.writerA.length > 0 ? (
            <ul className="space-y-2 text-sm text-gray-300">
              {bestBits.writerA.map((bit, index) => (
                <li key={index} className="list-disc pl-5">
                  {bit}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No highlights recorded.</p>
          )}
        </div>

        <div className="rounded-lg border border-gray-800 bg-gray-950 p-4">
          <h4 className="mb-3 text-sm font-semibold text-blue-400">
            💎 Best Bits: Writer B
          </h4>
          {bestBits.writerB.length > 0 ? (
            <ul className="space-y-2 text-sm text-gray-300">
              {bestBits.writerB.map((bit, index) => (
                <li key={index} className="list-disc pl-5">
                  {bit}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No highlights recorded.</p>
          )}
        </div>
      </div>
    </div>
  );
}
