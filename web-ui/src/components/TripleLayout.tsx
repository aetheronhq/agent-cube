import type { JSX } from "react";
import type { TripleLayoutProps } from "../types";
import { ThinkingBox } from "./ThinkingBox";

export function TripleLayout({
  judge1Lines,
  judge2Lines,
  judge3Lines,
}: TripleLayoutProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <ThinkingBox title="Judge 1" lines={judge1Lines} icon="⚖️" />
      <ThinkingBox title="Judge 2" lines={judge2Lines} icon="⚖️" />
      <ThinkingBox title="Judge 3" lines={judge3Lines} icon="⚖️" />
    </div>
  );
}
