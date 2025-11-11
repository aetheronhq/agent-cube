import { ThinkingBox } from "./ThinkingBox";

interface DualLayoutProps {
  writerALines: string[];
  writerBLines: string[];
}

export function DualLayout({ writerALines, writerBLines }: DualLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
