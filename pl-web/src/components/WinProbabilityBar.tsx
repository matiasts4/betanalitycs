interface WinProbabilityBarProps {
  homeWin: number;
  draw: number;
  awayWin: number;
  homeLabel: string;
  awayLabel: string;
}

export function WinProbabilityBar({ homeWin, draw, awayWin, homeLabel, awayLabel }: WinProbabilityBarProps) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs font-medium mono">
        <span className="text-primary">{homeLabel} {(homeWin * 100).toFixed(0)}%</span>
        <span className="text-muted-foreground">Draw {(draw * 100).toFixed(0)}%</span>
        <span className="text-info">{awayLabel} {(awayWin * 100).toFixed(0)}%</span>
      </div>
      <div className="flex h-2.5 overflow-hidden rounded-full bg-muted">
        <div className="bg-primary transition-all duration-500 rounded-l-full" style={{ width: `${homeWin * 100}%` }} />
        <div className="bg-muted-foreground/30 transition-all duration-500" style={{ width: `${draw * 100}%` }} />
        <div className="bg-info transition-all duration-500 rounded-r-full" style={{ width: `${awayWin * 100}%` }} />
      </div>
    </div>
  );
}
