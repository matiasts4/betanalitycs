import { useState, useMemo } from "react";
import { Calendar, TrendingUp, Trophy, ChevronDown, Loader2, Home, Globe, Minus } from "lucide-react";
import { useAPISeasons, useAPIHistoryMatches, APISeasonData } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";

const History = () => {
  const { data: seasons, isLoading: loadingSeasons } = useAPISeasons();
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);

  // Once seasons load, default to the most recent
  const effectiveSeason = selectedSeason ?? (seasons?.[0]?.season ?? null);
  const seasonData: APISeasonData | undefined = seasons?.find(s => s.season === effectiveSeason);

  const { data: matches, isLoading: loadingMatches } = useAPIHistoryMatches(100, effectiveSeason);

  const chartData = useMemo(() => {
    if (!seasons) return [];
    return [...seasons].reverse().map(s => ({
      label: s.label,
      homeWins: s.homeWins,
      draws: s.draws,
      awayWins: s.awayWins,
      matches: s.matches,
    }));
  }, [seasons]);

  if (loadingSeasons) {
    return (
      <div className="flex items-center justify-center p-24">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!seasons || seasons.length === 0) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        <p>No se encontraron temporadas en la base de datos</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-1">Historial Histórico</h1>
          <p className="text-sm text-muted-foreground">
            {seasons.length} temporadas · {seasons.reduce((s, d) => s + d.matches, 0).toLocaleString()} partidos · datos reales del CSV
          </p>
        </div>

        {/* Season Selector */}
        <div className="relative">
          <select
            value={effectiveSeason ?? ""}
            onChange={(e) => setSelectedSeason(Number(e.target.value))}
            className="appearance-none rounded-lg bg-secondary border border-border px-5 py-2.5 pr-10 text-sm font-semibold text-foreground cursor-pointer hover:bg-secondary/80 transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
          >
            {seasons.map((s) => (
              <option key={s.season} value={s.season}>Temporada {s.label}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        </div>
      </div>

      {/* All-time overview */}
      <div className="glass-card p-5 gradient-blue">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="h-4 w-4 text-warning" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Resumen Histórico (Todas las Temporadas)</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-foreground">{seasons.length}</p>
            <p className="text-xs text-muted-foreground mt-1">Temporadas</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-foreground">
              {seasons.reduce((s, d) => s + d.matches, 0).toLocaleString()}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Partidos Totales</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-success">
              {(seasons.reduce((s, d) => s + d.homeWinPct, 0) / seasons.length).toFixed(1)}%
            </p>
            <p className="text-xs text-muted-foreground mt-1">× Victoria Local Media</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-primary">
              {(seasons.reduce((s, d) => s + d.avgGoals, 0) / seasons.length).toFixed(2)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Goles/Partido Media</p>
          </div>
        </div>
      </div>

      {/* Season Breakdown Chart */}
      <div className="glass-card p-6">
        <h2 className="text-sm font-semibold text-foreground mb-4">Resultados por Temporada (partidos)</h2>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: "hsl(215 20% 50%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 50%)" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", fontSize: "12px", color: "hsl(213 31% 91%)" }}
              />
              <Bar dataKey="homeWins" name="Victoria Local" fill="hsl(217 91% 60%)" stackId="a" radius={[0,0,0,0]} />
              <Bar dataKey="draws" name="Empate" fill="hsl(40 90% 55%)" stackId="a" />
              <Bar dataKey="awayWins" name="Victoria Visitante" fill="hsl(200 90% 60%)" stackId="a" radius={[6,6,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex gap-4 justify-center mt-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-primary inline-block" /> Victoria Local</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-warning inline-block" /> Empate</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-info inline-block" /> Victoria Visitante</span>
        </div>
      </div>

      {/* Selected Season Details */}
      {seasonData && (
        <div>
          <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            Temporada {seasonData.label}
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
            {[
              { label: "Partidos", value: seasonData.matches.toLocaleString() },
              { label: "Equipos", value: seasonData.teams.toString() },
              { label: "Victoria Local", value: `${seasonData.homeWinPct}%`, color: "text-primary" },
              { label: "Empates", value: `${seasonData.drawPct}%`, color: "text-warning" },
              { label: "Victoria Visit.", value: `${seasonData.awayWinPct}%`, color: "text-info" },
              { label: "Goles/Partido", value: seasonData.avgGoals.toFixed(2), color: "text-success" },
              { label: "Victorias Loc.", value: seasonData.homeWins.toString(), color: "text-primary" },
            ].map((stat, i) => (
              <div key={i} className="glass-card p-4 text-center">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</p>
                <p className={cn("text-xl font-bold mt-1", stat.color || "text-foreground")}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Monthly Breakdown */}
          {seasonData.monthly.length > 0 && (
            <div className="glass-card overflow-hidden">
              <div className="p-4 border-b border-border">
                <h2 className="text-sm font-semibold text-foreground">Desglose Mensual — {seasonData.label}</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs text-muted-foreground uppercase tracking-wider">
                      <th className="text-left p-3 font-medium">Mes</th>
                      <th className="text-center p-3 font-medium">Partidos</th>
                      <th className="text-center p-3 font-medium"><Home className="h-3 w-3 inline" /> Local</th>
                      <th className="text-center p-3 font-medium"><Minus className="h-3 w-3 inline" /> Empate</th>
                      <th className="text-center p-3 font-medium"><Globe className="h-3 w-3 inline" /> Visit.</th>
                      <th className="text-right p-3 font-medium">Goles/P</th>
                    </tr>
                  </thead>
                  <tbody>
                    {seasonData.monthly.map((m, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                        <td className="p-3 font-medium text-foreground">{m.month}</td>
                        <td className="p-3 text-center text-muted-foreground">{m.matches}</td>
                        <td className="p-3 text-center text-primary font-semibold">{m.homeWins}</td>
                        <td className="p-3 text-center text-warning">{m.draws}</td>
                        <td className="p-3 text-center text-info">{m.awayWins}</td>
                        <td className="p-3 text-right text-foreground font-semibold">{m.avgGoals.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Match Log */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">
            Últimos Partidos — {seasonData?.label ?? "Todas"}
          </h2>
          {loadingMatches && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground uppercase tracking-wider">
                <th className="text-left p-3 font-medium">Fecha</th>
                <th className="text-left p-3 font-medium">Local</th>
                <th className="text-center p-3 font-medium">Marcador</th>
                <th className="text-left p-3 font-medium">Visitante</th>
                <th className="text-center p-3 font-medium">Resultado</th>
                <th className="text-center p-3 font-medium">Árbitro</th>
                <th className="text-right p-3 font-medium">Tarjetas</th>
              </tr>
            </thead>
            <tbody>
              {matches?.map((m, i) => (
                <tr key={i} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                  <td className="p-3 text-muted-foreground whitespace-nowrap text-xs">{m.date}</td>
                  <td className={cn("p-3 font-medium whitespace-nowrap", m.outcome === "home_win" ? "text-success" : "text-foreground")}>
                    {m.homeTeam}
                  </td>
                  <td className="p-3 text-center font-bold mono text-foreground">
                    {m.homeGoals} — {m.awayGoals}
                  </td>
                  <td className={cn("p-3 font-medium whitespace-nowrap", m.outcome === "away_win" ? "text-info" : "text-foreground")}>
                    {m.awayTeam}
                  </td>
                  <td className="p-3 text-center">
                    <span className={cn(
                      "inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold uppercase",
                      m.outcome === "home_win"
                        ? "bg-success/15 text-success"
                        : m.outcome === "away_win"
                        ? "bg-info/15 text-info"
                        : "bg-warning/15 text-warning"
                    )}>
                      {m.outcome === "home_win" ? "Local" : m.outcome === "away_win" ? "Visit." : "Empate"}
                    </span>
                  </td>
                  <td className="p-3 text-center text-xs text-muted-foreground truncate max-w-[120px]">{m.referee || "—"}</td>
                  <td className="p-3 text-right text-muted-foreground">{m.totalCards}</td>
                </tr>
              ))}
              {!loadingMatches && matches?.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-muted-foreground text-sm">No se encontraron partidos para esta temporada</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default History;
