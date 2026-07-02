import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: number;
  className?: string;
}

export function ConfidenceBadge({ confidence, className }: ConfidenceBadgeProps) {
  const color = confidence >= 75 ? "bg-success/15 text-success border-success/20" 
    : confidence >= 50 ? "bg-warning/15 text-warning border-warning/20" 
    : "bg-destructive/15 text-destructive border-destructive/20";

  return (
    <span className={cn("inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-semibold mono", color, className)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", 
        confidence >= 75 ? "bg-success" : confidence >= 50 ? "bg-warning" : "bg-destructive"
      )} />
      {Number(confidence).toFixed(1)}%
    </span>
  );
}
