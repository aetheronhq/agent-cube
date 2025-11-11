import type { JSX } from "react";
import type { SynthesisInfo } from "../types";

interface SynthesisViewProps {
  synthesis: SynthesisInfo;
}

export function SynthesisView({ synthesis }: SynthesisViewProps): JSX.Element {
  return (
    <div className="border border-gray-700 rounded-lg p-6 bg-gray-900">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-100 mb-2">
          Synthesis Instructions
        </h3>
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm text-gray-400">Compatible:</span>
          <span
            className={`px-2 py-1 rounded text-xs font-bold ${
              synthesis.compatible
                ? "bg-green-600 text-white"
                : "bg-red-600 text-white"
            }`}
          >
            {synthesis.compatible ? "✅ Yes" : "❌ No"}
          </span>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">
          How to Merge:
        </h4>
        <ul className="list-disc list-inside space-y-2 text-sm text-gray-400">
          {synthesis.instructions.map((instruction, i) => (
            <li key={i}>{instruction}</li>
          ))}
        </ul>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold mb-3 text-green-400">
            💎 Best Bits: Writer A
          </h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
            {synthesis.bestBits.writerA.map((bit, i) => (
              <li key={i}>{bit}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold mb-3 text-blue-400">
            💎 Best Bits: Writer B
          </h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
            {synthesis.bestBits.writerB.map((bit, i) => (
              <li key={i}>{bit}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
