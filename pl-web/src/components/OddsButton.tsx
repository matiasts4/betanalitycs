import { cn } from "@/lib/utils";

interface OddsButtonProps {
  odds: number | null;
  label?: string;
  edge?: number | null;
  className?: string;
}

export function OddsButton({ odds, label, edge, className }: OddsButtonProps) {
  const hasEdge = edge !== null && edge !== undefined && edge > 5;
  return (
    <button className={cn(
      "flex flex-col items-center gap-0.5 rounded-md border px-4 py-2 text-sm font-medium transition-all duration-150",
      hasEdge
        ? "border-success/25 bg-success/8 text-success hover:bg-success/15"
        : "border-border bg-muted text-secondary-foreground hover:bg-secondary",
      className
    )}>
      {label && <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>}
      <span className="text-base font-bold mono">
        {odds !== null && odds !== undefined ? odds.toFixed(2) : "—"}
      </span>
      {edge !== null && edge !== undefined && edge > 0 && (
        <span className={cn("text-[10px] font-semibold", hasEdge ? "text-success" : "text-muted-foreground")}>
          +{edge.toFixed(1)}% edge
        </span>
      )}
    </button>
  );
}
