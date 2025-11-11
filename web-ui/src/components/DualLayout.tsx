import type { JSX } from "react";
import type { DualLayoutProps } from "../types";
import { ThinkingBox } from "./ThinkingBox";

export function DualLayout({
  writerALines,
  writerBLines,
}: DualLayoutProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <ThinkingBox
        title="Writer A"
        lines={writerALines}
        icon="💭"
        color="green"
      />
      <ThinkingBox
        title="Writer B"
        lines={writerBLines}
        icon="💭"
        color="blue"
      />
    </div>
  );
}
