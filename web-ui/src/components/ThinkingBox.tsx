import type { ThinkingBoxProps } from "../types";

export function ThinkingBox({ title, lines, icon, color = "gray" }: ThinkingBoxProps) {
  const displayLines = lines.slice(-3);

  const borderColorClass =
    color === "green"
      ? "border-green-700"
      : color === "blue"
      ? "border-blue-700"
      : "border-gray-700";

  const textColorClass =
    color === "green"
      ? "text-green-400"
      : color === "blue"
      ? "text-blue-400"
      : "text-gray-400";

  const truncateLine = (line: string): string => {
    if (line.length > 91) {
      return line.slice(0, 91) + "...";
    }
    return line;
  };

  return (
    <div className={`border ${borderColorClass} rounded-lg p-4 bg-gray-900 min-h-[8rem]`}>
      <h3 className={`text-sm ${textColorClass} mb-2 font-medium`}>
        {icon} {title}
      </h3>
      <div className="space-y-1 font-mono text-xs text-gray-300 min-h-[3rem]">
        {displayLines.map((line, i) => (
          <p key={i} className="leading-relaxed">
            {truncateLine(line)}
          </p>
        ))}
      </div>
    </div>
  );
}
