import { Link } from "react-router-dom";
import { Calendar } from "lucide-react";
import { Match, getRefereeName } from "@/data/mockData";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { EntityLink } from "./EntityLink";
import { TeamLogo } from "./TeamLogo";
import { cn } from "@/lib/utils";

interface MatchCardProps {
  match: Match;
}

export function MatchCard({ match }: MatchCardProps) {
  const isCompleted = match.status === "completed";
  const isTestMatch = String(match.id).startsWith("test-");
  const topMarket = match.markets.length > 0
    ? match.markets.reduce((a, b) => (a.edge ?? 0) > (b.edge ?? 0) ? a : b)
    : null;

  return (
    <Link to={`/match/${match.id}`} className="glass-card-hover block p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Calendar className="h-3.5 w-3.5" />
          <span>{match.date}</span>
        </div>
        <span
          className={cn(
            "text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full",
            isCompleted
              ? "bg-muted text-muted-foreground"
              : "bg-primary/15 text-primary"
          )}
        >
          {isTestMatch ? "Test" : isCompleted ? "Finalizado" : match.time !== "TBD" ? match.time : "Próximo"}
        </span>
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-col items-center gap-1 flex-1">
          <EntityLink type="team" id={match.homeTeam.id} className="no-underline">
            <TeamLogo name={match.homeTeam.name} colors={match.homeTeam.colors} size="md" />
          </EntityLink>
          <span className="text-xs font-semibold text-foreground mt-1">{match.homeTeam.shortName}</span>
        </div>

        {/* Score or Predictions */}
        <div className="flex flex-col items-center gap-1 px-4">
          {isCompleted && match.score ? (
            <div className="flex items-center gap-2">
              <span className={cn(
                "text-2xl font-black mono",
                match.score.home > match.score.away ? "text-success" : "text-foreground"
              )}>
                {match.score.home}
              </span>
              <span className="text-muted-foreground font-mono text-sm">—</span>
              <span className={cn(
                "text-2xl font-black mono",
                match.score.away > match.score.home ? "text-success" : "text-foreground"
              )}>
                {match.score.away}
              </span>
            </div>
          ) : (
            <>
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">vs</span>
              <div className="flex gap-1.5 text-[11px] mono mt-1">
                <span className="text-primary font-bold">{(match.prediction.homeWin * 100).toFixed(0)}%</span>
                <span className="text-muted-foreground">{(match.prediction.draw * 100).toFixed(0)}%</span>
                <span className="text-info font-bold">{(match.prediction.awayWin * 100).toFixed(0)}%</span>
              </div>
            </>
          )}
        </div>

        <div className="flex flex-col items-center gap-1 flex-1">
          <EntityLink type="team" id={match.awayTeam.id} className="no-underline">
            <TeamLogo name={match.awayTeam.name} colors={match.awayTeam.colors} size="md" />
          </EntityLink>
          <span className="text-xs font-semibold text-foreground mt-1">{match.awayTeam.shortName}</span>
        </div>
      </div>

      {/* Result indicator for completed */}
      {isCompleted && match.score && (
        <div className="text-center text-[10px] text-muted-foreground mb-3">
          {match.score.home > match.score.away
            ? <span className="text-success font-medium">Victoria Local</span>
            : match.score.home < match.score.away
            ? <span className="text-info font-medium">Victoria Visitante</span>
            : <span className="text-warning font-medium">Empate</span>
          }
          {" · "}Árb: <EntityLink type="referee" id={match.refereeId} className="text-[10px]">{getRefereeName(match.refereeId)}</EntityLink>
        </div>
      )}

      {/* Best Market Chip */}
      {topMarket && !isCompleted && (
        <div className="flex items-center justify-between rounded-md bg-muted/80 border border-border/50 px-3 py-2.5">
          <div className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">
              Mejor Pick {topMarket.provider ? `(${topMarket.provider})` : ""}
            </span>
            <span className="text-xs font-medium text-foreground">{topMarket.name}: {topMarket.prediction}</span>
          </div>
          <div className="flex items-center gap-2">
            {topMarket.odds !== null && topMarket.odds !== undefined && topMarket.odds > 1 && (
              <span className="text-sm font-bold mono text-success">{topMarket.odds.toFixed(2)}</span>
            )}
            <ConfidenceBadge confidence={topMarket.confidence} />
          </div>
        </div>
      )}

      {/* Completed match — just show ref */}
      {isCompleted && !match.score && (
        <div className="text-[11px] text-muted-foreground text-center">
          Árb: <EntityLink type="referee" id={match.refereeId} className="text-[11px]">{getRefereeName(match.refereeId)}</EntityLink>
        </div>
      )}
    </Link>
  );
}
