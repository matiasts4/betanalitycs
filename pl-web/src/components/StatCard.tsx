import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  change?: string;
  icon: LucideIcon;
  positive?: boolean;
}

export function StatCard({ label, value, change, icon: Icon, positive }: StatCardProps) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</span>
        <div className="rounded-md bg-primary/10 p-2">
          <Icon className="h-4 w-4 text-primary" />
        </div>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold tracking-tight text-foreground">{value}</span>
        {change && (
          <span className={cn("text-xs font-semibold mb-0.5", positive ? "text-success" : "text-destructive")}>
            {change}
          </span>
        )}
      </div>
    </div>
  );
}
