import type { JSX } from "react";
import type { DualLayoutProps } from "../types";
import { ThinkingBox } from "./ThinkingBox";

export function DualLayout({
  writerALines,
  writerBLines,
  writerATitle = "Writer A",
  writerBTitle = "Writer B",
}: DualLayoutProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <ThinkingBox
        title={writerATitle}
        lines={writerALines}
        icon="💭"
        color="green"
      />
      <ThinkingBox
        title={writerBTitle}
        lines={writerBLines}
        icon="💭"
        color="blue"
      />
    </div>
  );
}
