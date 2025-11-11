import { ThinkingBox } from "./ThinkingBox";

interface TripleLayoutProps {
  judge1Lines: string[];
  judge2Lines: string[];
  judge3Lines: string[];
}

export function TripleLayout({ judge1Lines, judge2Lines, judge3Lines }: TripleLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <ThinkingBox
        title="Judge 1"
        lines={judge1Lines}
        icon="⚖️"
      />
      <ThinkingBox
        title="Judge 2"
        lines={judge2Lines}
        icon="⚖️"
      />
      <ThinkingBox
        title="Judge 3"
        lines={judge3Lines}
        icon="⚖️"
      />
    </div>
  );
}
