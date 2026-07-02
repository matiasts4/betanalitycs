import { useParams, Link } from "react-router-dom";
import { useState } from "react";
import { ArrowLeft, Calendar, MapPin, User, Loader2, Shield, Target, CreditCard, TrendingUp, Sparkles, Brain, AlertTriangle, Trash, Plus } from "lucide-react";
import { matches, getRefereeName } from "@/data/mockData";
import { WinProbabilityBar } from "@/components/WinProbabilityBar";
import { OddsButton } from "@/components/OddsButton";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { useAPIUpcomingMatches, mapAPIUpcomingToMockMatch, useAPIMatches, mapAPIMatchToMockMatch, fetchAIAnalysis } from "@/lib/api";
import { EntityLink } from "@/components/EntityLink";
import { TeamLogo } from "@/components/TeamLogo";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

const predictionCategories = [
  { key: "match-odds", label: "Cuotas" },
  { key: "goals", label: "Goles" },
  { key: "player-props", label: "Especiales" },
  { key: "cards-corners", label: "Tarjetas" },
] as const;

const MatchDetail = () => {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [provider, setProvider] = useState<string>("minimax");

  let match = matches.find((m) => m.id === id);

  const handleAnalyzeMatch = async () => {
    if (!match) return;
    setLoadingAnalysis(true);
    setAnalysisError(null);
    try {
      const res = await fetchAIAnalysis({
        homeTeam: match.homeTeam.name,
        awayTeam: match.awayTeam.name,
        date: match.date,
        provider: provider
      });
      setAnalysis(res.analysis);
    } catch (err: any) {
      console.error(err);
      setAnalysisError(err.message || "Ocurrió un error inesperado al analizar el partido");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const renderMarkdown = (text: string) => {
    if (!text) return null;
    
    const lines = text.split("\n");
    let inList = false;
    let listItems: string[] = [];
    let inTable = false;
    let tableRows: string[][] = [];
    const elements: React.ReactNode[] = [];
    
    const parseInline = (line: string): React.ReactNode[] => {
      const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);
      return parts.map((part, idx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={idx} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith("`") && part.endsWith("`")) {
          return <code key={idx} className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-primary">{part.slice(1, -1)}</code>;
        }
        return part;
      });
    };

    const flushList = (key: number) => {
      if (listItems.length > 0) {
        elements.push(
          <ul key={`list-${key}`} className="list-disc pl-5 my-3 space-y-1.5 text-sm text-muted-foreground">
            {listItems.map((item, idx) => (
              <li key={idx}>{parseInline(item)}</li>
            ))}
          </ul>
        );
        listItems = [];
        inList = false;
      }
    };

    const isSeparator = (cells: string[]) => {
      return cells.every(c => c.trim().replace(/[:-]/g, "") === "");
    };

    const flushTable = (key: number) => {
      if (tableRows.length > 0) {
        const headers = tableRows[0];
        const dataRows = tableRows.slice(1).filter(row => !isSeparator(row));
        elements.push(
          <div key={`table-${key}`} className="overflow-x-auto my-4 border border-border/50 rounded-lg">
            <table className="w-full text-sm text-left text-muted-foreground border-collapse">
              <thead className="text-xs uppercase bg-muted/60 text-foreground border-b border-border/50">
                <tr>
                  {headers.map((h, idx) => (
                    <th key={idx} className="px-4 py-2.5 font-bold border-r border-border/30 last:border-0">{h.trim()}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {dataRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-muted/10">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-4 py-2.5 font-medium text-foreground/80 border-r border-border/20 last:border-0">{parseInline(cell.trim())}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        tableRows = [];
        inTable = false;
      }
    };

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
        flushList(index);
        inTable = true;
        const cells = trimmed.split("|").slice(1, -1);
        tableRows.push(cells);
      } else {
        flushTable(index);
        
        if (trimmed.startsWith("### ")) {
          flushList(index);
          elements.push(<h3 key={index} className="text-base font-bold text-foreground mt-4 mb-2">{parseInline(trimmed.substring(4))}</h3>);
        } else if (trimmed.startsWith("## ")) {
          flushList(index);
          elements.push(<h2 key={index} className="text-lg font-bold text-foreground mt-5 mb-2 border-b border-border/40 pb-1">{parseInline(trimmed.substring(3))}</h2>);
        } else if (trimmed.startsWith("# ")) {
          flushList(index);
          elements.push(<h1 key={index} className="text-xl font-black text-foreground mt-6 mb-3">{parseInline(trimmed.substring(2))}</h1>);
        } else if (trimmed.startsWith("> ")) {
          flushList(index);
          elements.push(
            <blockquote key={index} className="border-l-4 border-primary/50 bg-muted/40 pl-4 py-2.5 my-3 rounded-r text-sm italic text-muted-foreground">
              {parseInline(trimmed.substring(2))}
            </blockquote>
          );
        } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
          inList = true;
          listItems.push(trimmed.substring(2));
        } else if (/^\d+\.\s/.test(trimmed)) {
          inList = true;
          listItems.push(trimmed.replace(/^\d+\.\s/, ""));
        } else if (trimmed === "") {
          flushList(index);
        } else {
          flushList(index);
          elements.push(<p key={index} className="text-sm text-muted-foreground leading-relaxed my-2">{parseInline(trimmed)}</p>);
        }
      }
    });
    
    flushList(lines.length);
    flushTable(lines.length);
    
    return <div className="space-y-1">{elements}</div>;
  };

  const { data: upcomingMatches, isLoading: upcomingLoading } = useAPIUpcomingMatches();
  const { data: recentAPIMatches, isLoading: recentLoading } = useAPIMatches();
  const isLoading = upcomingLoading || recentLoading;

  if (!match && upcomingMatches) {
    const liveMatch = upcomingMatches.find((m) => m.id === id);
    if (liveMatch) match = mapAPIUpcomingToMockMatch(liveMatch);
  }

  if (!match && recentAPIMatches) {
    const historical = recentAPIMatches.find((m) => m.id === id);
    if (historical) match = mapAPIMatchToMockMatch(historical);
  }

  if (isLoading && !match) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
        <p>Cargando detalles del partido...</p>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <p>Partido no encontrado</p>
        <Link to="/matches" className="mt-2 text-primary hover:underline text-sm">Volver a Partidos</Link>
      </div>
    );
  }

  const isCompleted = match.status === "completed";
  const homeWon = match.score && match.score.home > match.score.away;
  const awayWon = match.score && match.score.away > match.score.home;
  const isDraw  = match.score && match.score.home === match.score.away;

  // Find the total cards market entry
  const cardsMarket = match.markets.find((m: any) => m.category === "cards-corners");
  const goalsTotal = match.score ? match.score.home + match.score.away : null;
  const btts = match.score ? match.score.home > 0 && match.score.away > 0 : false;

  const sortedMarkets = [...match.markets].sort((a: any, b: any) => b.edge - a.edge);
  const bestMarket = sortedMarkets.length > 0 && sortedMarkets[0].edge > 0 ? sortedMarkets[0] : null;

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <Link to="/matches" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="h-4 w-4" /> Volver a Partidos
      </Link>

      {/* Header card — teams + score/vs */}
      <div className="glass-card p-6 text-center space-y-4 gradient-blue">
        <div className="flex items-center justify-center gap-8 md:gap-16">
          <EntityLink type="team" id={match.homeTeam.id} className="flex flex-col items-center gap-2 no-underline">
            <TeamLogo name={match.homeTeam.name} colors={match.homeTeam.colors} size="lg" />
            <span className={cn("text-lg font-bold mt-2", homeWon && "text-success")}>{match.homeTeam.name}</span>
          </EntityLink>

          {/* Score or VS */}
          <div className="flex flex-col items-center gap-1">
            {isCompleted && match.score ? (
              <>
                <div className="flex items-center gap-3">
                  <span className={cn("text-5xl font-black mono", homeWon ? "text-success" : "text-foreground")}>{match.score.home}</span>
                  <span className="text-2xl text-muted-foreground font-light">–</span>
                  <span className={cn("text-5xl font-black mono", awayWon ? "text-success" : "text-foreground")}>{match.score.away}</span>
                </div>
                <span className={cn(
                  "text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mt-1",
                  homeWon ? "bg-success/15 text-success" :
                  awayWon ? "bg-info/15 text-info" :
                  "bg-warning/15 text-warning"
                )}>
                  {homeWon ? `Gana ${match.homeTeam.shortName}` : awayWon ? `Gana ${match.awayTeam.shortName}` : "Empate"}
                </span>
                <span className="text-[10px] text-muted-foreground mt-0.5">Partido Finalizado</span>
              </>
            ) : (
              <span className="text-2xl font-bold text-muted-foreground">VS</span>
            )}
          </div>

          <EntityLink type="team" id={match.awayTeam.id} className="flex flex-col items-center gap-2 no-underline">
            <TeamLogo name={match.awayTeam.name} colors={match.awayTeam.colors} size="lg" />
            <span className={cn("text-lg font-bold mt-2", awayWon && "text-success")}>{match.awayTeam.name}</span>
          </EntityLink>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{match.date} · {match.time}</span>
          <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{match.stadium}</span>
          {match.refereeId && match.refereeId !== "tbd" && (
            <span className="flex items-center gap-1">
              <User className="h-3 w-3" />
              <EntityLink type="referee" id={match.refereeId}>{getRefereeName(match.refereeId)}</EntityLink>
            </span>
          )}
        </div>

        {/* Win probability bar — only for upcoming */}
        {!isCompleted && (
          <WinProbabilityBar
            homeWin={match.prediction.homeWin}
            draw={match.prediction.draw}
            awayWin={match.prediction.awayWin}
            homeLabel={match.homeTeam.shortName}
            awayLabel={match.awayTeam.shortName}
          />
        )}
      </div>

      {/* COMPLETED MATCH: show real stats grid */}
      {isCompleted && match.score && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="glass-card p-4 text-center">
            <Target className="h-5 w-5 text-primary mx-auto mb-2" />
            <p className="text-2xl font-black mono text-foreground">{goalsTotal}</p>
            <p className="text-[11px] text-muted-foreground uppercase tracking-wide mt-1">Total Goles</p>
          </div>
          <div className="glass-card p-4 text-center">
            <TrendingUp className="h-5 w-5 text-success mx-auto mb-2" />
            <p className="text-2xl font-black mono text-foreground">{goalsTotal !== null && goalsTotal > 2.5 ? "Sí" : "No"}</p>
            <p className="text-[11px] text-muted-foreground uppercase tracking-wide mt-1">Más de 2.5</p>
          </div>
          <div className="glass-card p-4 text-center">
            <Shield className="h-5 w-5 text-info mx-auto mb-2" />
            <p className="text-2xl font-black mono text-foreground">{btts ? "Sí" : "No"}</p>
            <p className="text-[11px] text-muted-foreground uppercase tracking-wide mt-1">Ambos Marcan</p>
          </div>
          <div className="glass-card p-4 text-center">
            <CreditCard className="h-5 w-5 text-warning mx-auto mb-2" />
            <p className="text-2xl font-black mono text-foreground">
              {cardsMarket ? cardsMarket.prediction.split(" ")[0] : "—"}
            </p>
            <p className="text-[11px] text-muted-foreground uppercase tracking-wide mt-1">Tarjetas</p>
          </div>
        </div>
      )}

      {/* COMPLETED MATCH: detailed result rows */}
      {isCompleted && match.score && (
        <div className="glass-card overflow-hidden">
          <div className="p-4 border-b border-border/50">
            <h2 className="text-sm font-semibold text-foreground">Resumen del Partido</h2>
          </div>
          <div className="divide-y divide-border/50">
            {[
              { label: "Resultado", value: `${match.homeTeam.shortName} ${match.score.home} – ${match.score.away} ${match.awayTeam.shortName}` },
              { label: "Vencedor", value: homeWon ? match.homeTeam.name : awayWon ? match.awayTeam.name : "Empate" },
              { label: "Total de Goles", value: `${goalsTotal} gol${goalsTotal !== 1 ? "es" : ""}` },
              { label: "Ambos Marcan", value: btts ? "Sí" : "No" },
              { label: "Más de 2.5 Goles", value: goalsTotal !== null && goalsTotal > 2.5 ? "Sí" : "No" },
              ...(cardsMarket ? [{ label: "Total Tarjetas", value: cardsMarket.prediction }] : []),
              ...(match.refereeId && match.refereeId !== "tbd" ? [{ label: "Árbitro", value: getRefereeName(match.refereeId) }] : []),
              { label: "Fecha", value: match.date },
            ].map((row, i) => (
              <div key={i} className="flex items-center justify-between px-4 py-3">
                <span className="text-sm text-muted-foreground">{row.label}</span>
                <span className="text-sm font-medium text-foreground">{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* UPCOMING MATCH: show predictions list */}
      {!isCompleted && (
        <div className="space-y-6">
          {/* AI EXPERT ANALYST CARD */}
          <div className="glass-card p-5 relative overflow-hidden bg-gradient-to-br from-primary/10 via-card to-card border-primary/20 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-primary/15 rounded-lg text-primary">
                  <Brain className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-bold text-foreground text-sm flex items-center gap-1.5">
                    Analista Experto de IA <Sparkles className="h-3.5 w-3.5 text-primary animate-pulse" />
                  </h3>
                  <p className="text-[11px] text-muted-foreground">Análisis de valor y sugerencias en base a ELO y racha en Premier League</p>
                </div>
              </div>
              <div className="flex items-center gap-2 self-start sm:self-center">
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="bg-card text-foreground text-xs border border-border rounded px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary h-8"
                >
                  <option value="minimax">MiniMax (M3)</option>
                  <option value="openai">OpenAI (GPT-4o mini)</option>
                  <option value="anthropic">Anthropic (Claude 3.5)</option>
                  <option value="openrouter">OpenRouter (Qwen)</option>
                </select>
                <button
                  onClick={handleAnalyzeMatch}
                  disabled={loadingAnalysis}
                  className="bg-primary text-primary-foreground text-xs font-semibold rounded px-3 py-1.5 inline-flex items-center gap-1.5 hover:bg-primary/90 transition-all disabled:opacity-50 h-8"
                >
                  {loadingAnalysis ? (
                    <>
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Analizando...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-3 w-3" />
                      Analizar
                    </>
                  )}
                </button>
              </div>
            </div>

            {analysisError && (
              <div className="flex items-start gap-2 bg-destructive/10 border border-destructive/20 text-destructive text-xs rounded p-3">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Error al conectar con la IA</p>
                  <p className="opacity-90">{analysisError}</p>
                </div>
              </div>
            )}

            {analysis ? (
              <div className="border-t border-border/50 pt-4 text-sm font-normal text-muted-foreground animate-fade-in">
                {renderMarkdown(analysis)}
              </div>
            ) : (
              !loadingAnalysis && (
                <div className="border-t border-border/30 pt-3 flex flex-col items-center justify-center py-6 text-center text-xs text-muted-foreground">
                  <p className="max-w-md">¿Querés una sugerencia personalizada? Seleccioná un proveedor de IA y hacé clic en "Analizar" para que nuestro analista de apuestas y machine learning procese las cuotas locales en español rioplatense.</p>
                </div>
              )
            )}

            {loadingAnalysis && (
              <div className="border-t border-border/30 pt-4 flex flex-col items-center justify-center py-8 text-center text-sm text-muted-foreground space-y-2">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <p className="font-medium text-foreground">Procesando cuotas justas y calculando valor esperado...</p>
                <p className="text-xs opacity-75">El analista de IA está formulando el informe en voseo</p>
              </div>
            )}
          </div>

          {/* Model predictions compact table */}
          <div className="glass-card p-5 border-border/50">
            <div className="border-b border-border/50 pb-3 mb-4">
              <h3 className="font-bold text-foreground text-sm">
                Predicciones de Modelos de Machine Learning
              </h3>
              <p className="text-[11px] text-muted-foreground">
                Evaluación de todos los mercados ordenada por ventaja matemática (EV) en base a los modelos optimizados.
              </p>
            </div>

            {sortedMarkets.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">Aún no hay predicciones calculadas para este encuentro.</p>
            ) : (
              <div className="overflow-x-auto border border-border/40 rounded-lg">
                <table className="w-full text-xs text-left border-collapse">
                  <thead className="text-[10px] uppercase bg-muted/70 text-foreground border-b border-border/40">
                    <tr>
                      <th className="px-3 py-2.5 font-bold">Mercado / Selección</th>
                      <th className="px-3 py-2.5 font-bold text-center">Probabilidad</th>
                      <th className="px-3 py-2.5 font-bold text-center">Cuota Bookie</th>
                      <th className="px-3 py-2.5 font-bold text-center">Cuota Justa</th>
                      <th className="px-3 py-2.5 font-bold text-center">Ventaja (EV)</th>
                      <th className="px-3 py-2.5 font-bold text-center">Stake Kelly (0.25x)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/30">
                    {sortedMarkets.map((market: any, i: number) => {
                      const isBest = bestMarket && bestMarket.name === market.name;
                      return (
                        <tr
                          key={i}
                          className={cn(
                            "transition-colors",
                            isBest ? "bg-success/5 border-l-4 border-l-success font-medium" : "hover:bg-muted/5"
                          )}
                        >
                          <td className="px-3 py-2.5">
                            <div className="flex flex-col gap-0.5">
                              <div className="flex items-center gap-1.5">
                                <span className="font-bold text-foreground">{market.name}</span>
                                {isBest && (
                                  <span className="bg-success text-success-foreground text-[8px] font-bold px-1 rounded uppercase tracking-wider">
                                    Mejor Opción
                                  </span>
                                )}
                              </div>
                              <span className="text-[10px] text-muted-foreground">{market.prediction}</span>
                            </div>
                          </td>
                          <td className="px-3 py-2.5 text-center">
                            <ConfidenceBadge confidence={Math.round(market.confidence)} />
                          </td>
                          <td className="px-3 py-2.5 text-center font-semibold font-mono text-foreground">
                            x{market.odds.toFixed(2)}
                          </td>
                          <td className="px-3 py-2.5 text-center text-muted-foreground font-mono">
                            x{market.fairOdds.toFixed(2)}
                          </td>
                          <td className="px-3 py-2.5 text-center">
                            <span className={cn(
                              "font-bold font-mono text-xs",
                              market.edge > 5
                                ? "text-success"
                                : market.edge > 0
                                  ? "text-warning"
                                  : "text-muted-foreground"
                            )}>
                              {market.edge > 0 ? "+" : ""}{market.edge.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-3 py-2.5 text-center font-bold font-mono text-primary">
                            {market.recommendedStakePct.toFixed(1)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MatchDetail;

