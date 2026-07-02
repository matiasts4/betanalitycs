import { TrendingUp, Target, Activity, Flame, Loader2, BarChart3, Zap, RefreshCw } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { MatchCard } from "@/components/MatchCard";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { OddsButton } from "@/components/OddsButton";
import { useAPIStats, useAPIUpcomingMatches, mapAPIUpcomingToMockMatch, APIUpcomingResponse, updateUpcomingMatches, useAPIParlays } from "@/lib/api";
import { MarketPrediction } from "@/data/mockData";
import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// Fallback hot picks — only valid market categories, no player-specific props
const FALLBACK_HOT_PICKS: MarketPrediction[] = [
  { category: "match-odds", name: "Ganador del Partido (1X2)", prediction: "Datos cargando…", odds: 2.10, fairOdds: 2.00, confidence: 72, edge: 5.0 },
  { category: "goals", name: "Más de 2.5 Goles", prediction: "Mercado de goles predefinido", odds: 1.85, fairOdds: 1.72, confidence: 76, edge: 7.6 },
  { category: "goals", name: "Ambos Marcan (Sí)", prediction: "Mercado BTTS predefinido", odds: 1.72, fairOdds: 1.65, confidence: 74, edge: 5.8 },
  { category: "match-odds", name: "Doble Oportunidad (1X)", prediction: "Local o Empate", odds: 1.45, fairOdds: 1.38, confidence: 80, edge: 5.1 },
  { category: "cards-corners", name: "Total Tarjetas Más 3.5", prediction: "Mercado de tarjetas predefinido", odds: 1.80, fairOdds: 1.70, confidence: 70, edge: 5.9 },
];

// Map API market name to frontend category
function marketToCategory(market: string): MarketPrediction["category"] {
  const m = market.toLowerCase();
  if (m.includes("1x2") || m.includes("winner") || m.includes("double chance") || m.includes("clean sheet")) return "match-odds";
  if (m.includes("goal") || m.includes("btts") || m.includes("over") || m.includes("under")) return "goals";
  if (m.includes("card") || m.includes("corner") || m.includes("foul")) return "cards-corners";
  return "match-odds";
}

// Resolve real odds for a market/pick from the API upcoming match
function getRealOddFromMatch(m: APIUpcomingResponse, market: string, pick: number, useMax = false): number | null {
  const oddsObj = useMax ? m.max_odds : m.odds;
  if (!oddsObj) return null;
  const mLower = market.toLowerCase();
  if (mLower.includes("1x2")) {
    if (pick === 2) return oddsObj.home;
    if (pick === 0) return oddsObj.away;
    return oddsObj.draw;
  }
  if (mLower.includes("over 2.5")) return oddsObj.over25;
  if (mLower.includes("under 2.5")) return oddsObj.under25;
  if (mLower.includes("btts")) {
    if (mLower.includes("no")) return oddsObj.btts_no;
    return oddsObj.btts_yes;
  }
  return null;
}

// Build hot picks from real upcoming match API data
function buildHotPicksFromAPI(matches: APIUpcomingResponse[]): MarketPrediction[] {
  const picks: MarketPrediction[] = [];

  for (const m of matches) {
    if (!m.topPrediction) continue;
    const prob = m.topPrediction.Probability;
    const fairOdds = prob > 0 ? 1 / prob : null;
    // Use average odds by default; only fall back to max odds if average is unavailable.
    const realOdd = getRealOddFromMatch(m, m.topPrediction.Market, m.topPrediction.Pick ?? 1, false)
      || getRealOddFromMatch(m, m.topPrediction.Market, m.topPrediction.Pick ?? 1, true);

    let edge: number | null = null;
    if (realOdd !== null && realOdd > 1.0 && prob > 0) {
      edge = Math.round(((prob - 1 / realOdd) * 100) * 10) / 10;
    }

    picks.push({
      category: marketToCategory(m.topPrediction.Market),
      name: m.topPrediction.Market,
      prediction: `${m.homeTeam} vs ${m.awayTeam}`,
      odds: realOdd,
      fairOdds: fairOdds !== null ? Math.round(fairOdds * 100) / 100 : null,
      confidence: Math.round(prob * 100),
      edge,
    });

    if (picks.length >= 5) break;
  }

  return picks.length > 0 ? picks : FALLBACK_HOT_PICKS;
}

const Dashboard = () => {
  const queryClient = useQueryClient();
  const [isUpdating, setIsUpdating] = useState(false);
  const { data: stats, isLoading: statsLoading } = useAPIStats();
  const { data: matches, isLoading: matchesLoading } = useAPIUpcomingMatches();
  const { data: parlays, isLoading: parlaysLoading, error: parlaysError } = useAPIParlays("average");
  const [parlayTab, setParlayTab] = useState<"multi" | "sameGame">("multi");

  const handleUpdate = async () => {
    setIsUpdating(true);
    toast.loading("Actualizando partidos y predicciones desde FBref...", { id: "update-toast" });
    try {
      await updateUpcomingMatches();
      queryClient.invalidateQueries({ queryKey: ["matches_upcoming"] });
      queryClient.invalidateQueries({ queryKey: ["parlays_suggested"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      queryClient.invalidateQueries({ queryKey: ["performance_stats"] });
      queryClient.invalidateQueries({ queryKey: ["history"] });
      toast.success("¡Calendario y predicciones actualizados con éxito!", { id: "update-toast" });
    } catch (err: any) {
      toast.error(err.message || "Error al actualizar los partidos", { id: "update-toast" });
    } finally {
      setIsUpdating(false);
    }
  };

  const hotPicks = matches && matches.length > 0
    ? buildHotPicksFromAPI(matches)
    : FALLBACK_HOT_PICKS;

  const hasSimulatedOdds = matches?.some(m => m.odds?.is_simulated) ?? false;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Stats */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground mb-1 tracking-tight">Panel de Control</h1>
        <p className="text-sm text-muted-foreground mb-6">Insights de apuestas de la Premier League con IA</p>
        {hasSimulatedOdds && (
          <div className="mb-4 rounded-md border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-300">
            ⚠️ Algunas cuotas mostradas son <strong>simuladas</strong> (modo mock). No son aptas para apostar dinero real.
          </div>
        )}
        {statsLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="glass-card p-4 h-24 flex items-center justify-center">
                <Loader2 className="h-5 w-5 animate-spin text-primary opacity-50" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard
              label="TASA DE ACIERTO"
              value={stats ? `${stats.accuracy_pct.toFixed(1)}%` : "—"}
              change="Evaluado en 380 partidos out-of-sample"
              icon={Target}
              positive
            />
            <StatCard
              label="MERCADOS ACTIVOS"
              value={stats ? stats.markets_tracked.toString() : "—"}
              change="Tipos de apuesta con modelos propios"
              icon={Zap}
            />
            <StatCard
              label="PARTIDOS ANALIZADOS"
              value={stats ? stats.totalMatches.toLocaleString() : "—"}
              change="Historial de la Premier League"
              icon={Activity}
              positive
            />
            <StatCard
              label="TEMPORADAS"
              value={stats ? stats.seasons.toString() : "—"}
              change="Desde 2017/18 hasta 2025/26"
              icon={TrendingUp}
              positive
            />
          </div>
        )}
      </div>

      {/* Hot Picks — derived from real upcoming match predictions */}
      <div className="animate-fade-in" style={{ animationDelay: "100ms" }}>
        <div className="flex items-center gap-2 mb-4">
          <Flame className="h-5 w-5 text-warning" />
          <h2 className="text-lg font-semibold text-foreground tracking-tight">Selecciones Destacadas</h2>
          <span className="text-xs text-muted-foreground">
            · {matches && matches.length > 0 ? "Generadas desde partidos de test" : "Las mejores apuestas de test"}
          </span>
        </div>
        <div className="space-y-2.5">
          {hotPicks.map((pick, i) => (
            <div 
              key={i} 
              className="glass-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-primary/20 transition-all duration-300 group hover:translate-x-1"
            >
              <div className="flex items-center gap-3">
                <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-primary/10 text-primary font-bold text-xs shrink-0 group-hover:bg-primary group-hover:text-primary-foreground transition-colors duration-300">
                  #{i + 1}
                </span>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] uppercase tracking-wider text-muted-foreground font-bold bg-secondary/50 px-2 py-0.5 rounded">
                      {pick.category.replace(/-/g, " ")}
                    </span>
                    <ConfidenceBadge confidence={pick.confidence} />
                  </div>
                  <p className="text-sm font-bold text-foreground">{pick.name}</p>
                  <p className="text-xs text-muted-foreground">{pick.prediction}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 sm:gap-6 justify-between sm:justify-end shrink-0">
                <div className="text-left sm:text-right">
                  <p className="text-[9px] text-muted-foreground uppercase tracking-wider font-semibold">Ventaja (Edge)</p>
                  <p className="text-sm font-bold mono text-success">+{pick.edge.toFixed(1)}%</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-center bg-secondary/35 px-2.5 py-1 rounded-md border border-border/40">
                    <p className="text-[8px] text-muted-foreground uppercase font-semibold">Cuota Justa</p>
                    <p className="text-xs font-bold font-mono text-foreground">{pick.fairOdds.toFixed(2)}</p>
                  </div>
                  <OddsButton odds={pick.odds} edge={pick.edge} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Suggested Parlays */}
      <div className="animate-fade-in" style={{ animationDelay: "150ms" }}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-success" />
            <h2 className="text-lg font-semibold text-foreground tracking-tight">Combinadas Recomendadas (+EV)</h2>
            <span className="text-xs text-muted-foreground">· Generadas mediante Line Shopping</span>
          </div>
          
          {/* Sub-Tabs Switcher */}
          <div className="flex bg-secondary/35 p-1 rounded-lg border border-border/40 text-[11px] font-semibold shrink-0">
            <button
              onClick={() => setParlayTab("multi")}
              className={cn(
                "px-3 py-1 rounded-md transition-all",
                parlayTab === "multi" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Multi-Partido
            </button>
            <button
              onClick={() => setParlayTab("sameGame")}
              className={cn(
                "px-3 py-1 rounded-md transition-all",
                parlayTab === "sameGame" ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
              )}
            >
              Mismo Partido (SGP)
            </button>
          </div>
        </div>

        {parlaysLoading ? (
          <div className="glass-card p-6 flex justify-center items-center h-32">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : parlayTab === "multi" ? (
          (parlays?.doubles?.length || 0) + (parlays?.trebles?.length || 0) > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {/* Doubles */}
              {parlays?.doubles?.slice(0, 2).map((parlay, idx) => (
                <div key={`double-${idx}`} className="glass-card p-5 border-success/20 hover:border-success/40 transition-all duration-300 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-success/20 text-success border border-success/30">
                        Combinada Doble
                      </span>
                      <div className="flex gap-2">
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          EV: +{(parlay.ev * 100).toFixed(1)}%
                        </span>
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          Kelly: {parlay.recommended_stake_pct}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-3 my-4">
                      {parlay.selections.map((sel, sIdx) => (
                        <div key={sIdx} className="flex justify-between items-center text-xs border-b border-border/20 pb-2 last:border-0 last:pb-0">
                          <div>
                            <p className="font-bold text-foreground">{sel.home_team} vs {sel.away_team}</p>
                            <p className="text-muted-foreground text-[10px]">{sel.market} ({sel.pick === 2 ? 'L' : sel.pick === 0 ? 'V' : 'E'})</p>
                          </div>
                          <div className="text-right">
                            <span className="font-mono font-bold text-foreground">{sel.odd.toFixed(2)}</span>
                            <span className="text-[9px] text-muted-foreground block">({sel.provider})</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between border-t border-border/50 pt-3 mt-2">
                    <span className="text-xs text-muted-foreground">Cuota Total</span>
                    <span className="text-lg font-black font-mono text-success">{parlay.odds.toFixed(2)}</span>
                  </div>
                </div>
              ))}

              {/* Trebles */}
              {parlays?.trebles?.slice(0, 2).map((parlay, idx) => (
                <div key={`treble-${idx}`} className="glass-card p-5 border-info/20 hover:border-info/40 transition-all duration-300 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-info/20 text-info border border-info/30">
                        Combinada Triple
                      </span>
                      <div className="flex gap-2">
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          EV: +{(parlay.ev * 100).toFixed(1)}%
                        </span>
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          Kelly: {parlay.recommended_stake_pct}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-3 my-4">
                      {parlay.selections.map((sel, sIdx) => (
                        <div key={sIdx} className="flex justify-between items-center text-xs border-b border-border/20 pb-2 last:border-0 last:pb-0">
                          <div>
                            <p className="font-bold text-foreground">{sel.home_team} vs {sel.away_team}</p>
                            <p className="text-muted-foreground text-[10px]">{sel.market} ({sel.pick === 2 ? 'L' : sel.pick === 0 ? 'V' : 'E'})</p>
                          </div>
                          <div className="text-right">
                            <span className="font-mono font-bold text-foreground">{sel.odd.toFixed(2)}</span>
                            <span className="text-[9px] text-muted-foreground block">({sel.provider})</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between border-t border-border/50 pt-3 mt-2">
                    <span className="text-xs text-muted-foreground">Cuota Total</span>
                    <span className="text-lg font-black font-mono text-info">{parlay.odds.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 flex flex-col items-center justify-center text-center text-muted-foreground h-32 gap-1">
              <Zap className="w-6 h-6 opacity-20" />
              <p className="text-xs font-semibold">Sin Combinadas Recomendadas</p>
              <p className="text-[10px] opacity-65">No hay suficientes partidos con cuotas de valor (+EV) para formar combinadas hoy.</p>
            </div>
          )
        ) : (
          (parlays?.same_game?.length || 0) > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {parlays?.same_game?.map((parlay, idx) => (
                <div key={`sgp-${idx}`} className="glass-card p-5 border-primary/20 hover:border-primary/40 transition-all duration-300 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-primary/15 text-primary border border-primary/25">
                        Crear Apuesta (SGP)
                      </span>
                      <div className="flex gap-1.5">
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          EV: +{(parlay.ev * 100).toFixed(1)}%
                        </span>
                        <span className="text-[10px] bg-secondary/80 px-2 py-0.5 rounded text-muted-foreground font-semibold">
                          Kelly: {parlay.recommended_stake_pct}%
                        </span>
                      </div>
                    </div>

                    <h4 className="text-xs font-bold text-foreground mb-2 pb-1 border-b border-border/30">
                      {parlay.match_name}
                    </h4>
                    
                    <div className="space-y-2.5 my-3">
                      {parlay.selections.map((sel, sIdx) => (
                        <div key={sIdx} className="flex justify-between items-center text-xs pb-1 last:border-0 last:pb-0">
                          <div>
                            <p className="font-semibold text-foreground text-[11px]">{sel.market}</p>
                            <p className="text-[9px] text-muted-foreground">Pick: {sel.pick === 2 ? 'L' : sel.pick === 0 ? 'V' : 'E'}</p>
                          </div>
                          <div className="text-right">
                            <span className="font-mono font-bold text-foreground">{sel.odd.toFixed(2)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between border-t border-border/50 pt-3 mt-2">
                    <div className="text-left">
                      <span className="text-[9px] text-muted-foreground uppercase font-bold block">Casa Recomendada</span>
                      <span className="text-[11px] text-foreground font-semibold">{parlay.selections[0]?.provider || "Mercado Máximo"}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[9px] text-muted-foreground uppercase font-bold block">Cuota SGP</span>
                      <span className="text-base font-black font-mono text-primary">{parlay.odds.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card p-8 flex flex-col items-center justify-center text-center text-muted-foreground h-32 gap-1">
              <Zap className="w-6 h-6 opacity-20" />
              <p className="text-xs font-semibold">Sin Same-Game Parlays</p>
              <p className="text-[10px] opacity-65">No hay partidos hoy con mercados dependientes correlacionados que superen el EV+ requerido.</p>
            </div>
          )
        )}
      </div>

      {/* Upcoming Matches */}
      <div className="animate-fade-in" style={{ animationDelay: "200ms" }}>
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground tracking-tight">Partidos de Test</h2>
            {matches && (
              <span className="text-xs text-muted-foreground ml-2">
                ({matches.length} partido{matches.length !== 1 ? "s" : ""})
              </span>
            )}
          </div>
          <button
            onClick={handleUpdate}
            disabled={isUpdating}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-primary hover:text-primary-foreground bg-primary/10 hover:bg-primary border border-primary/20 rounded-md transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isUpdating ? "animate-spin" : ""}`} />
            {isUpdating ? "Actualizando..." : "Recargar Partidos de Test"}
          </button>
        </div>
        {matchesLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : matches && matches.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {matches.slice(0, 9).map((m) => (
              <MatchCard key={m.id} match={mapAPIUpcomingToMockMatch(m)} />
            ))}
          </div>
        ) : (
          <div className="glass-card p-10 flex flex-col items-center justify-center text-center text-muted-foreground gap-2">
            <BarChart3 className="h-10 w-10 opacity-20 mb-1" />
            <p className="text-sm font-medium">No hay partidos de test disponibles</p>
            <p className="text-xs opacity-60">No se encontraron partidos de test en el sistema</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
