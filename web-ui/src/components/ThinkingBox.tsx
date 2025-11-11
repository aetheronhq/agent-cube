import type { JSX } from "react";
import type { ThinkingBoxProps } from "../types";

const COLOR_VARIANTS: Record<
  NonNullable<ThinkingBoxProps["color"]>,
  { border: string; title: string }
> = {
  green: {
    border: "border-emerald-500/60",
    title: "text-emerald-300",
  },
  blue: {
    border: "border-sky-500/60",
    title: "text-sky-300",
  },
  gray: {
    border: "border-gray-700",
    title: "text-gray-300",
  },
};

function formatLine(line: string): string {
  if (line.length <= 91) {
    return line;
  }

  return `${line.slice(0, 91)}...`;
}

export function ThinkingBox({
  title,
  lines,
  icon,
  color = "gray",
}: ThinkingBoxProps): JSX.Element {
  const variant = COLOR_VARIANTS[color] ?? COLOR_VARIANTS.gray;
  const displayLines = lines.slice(-3);

  return (
    <div
      className={`border ${variant.border} rounded-lg bg-gray-900/90 p-4 shadow-sm min-h-[8rem] transition-colors`}
    >
      <div className="flex items-center justify-between text-sm">
        <span className={`font-semibold ${variant.title}`}>
          {icon} {title}
        </span>
      </div>
      <div className="mt-3 space-y-1 font-mono text-xs text-gray-200 min-h-[3.5rem]">
        {displayLines.map((line, index) => (
          <p key={index} className="whitespace-pre-wrap break-words leading-tight">
            {formatLine(line)}
          </p>
        ))}
      </div>
    </div>
  );
}
