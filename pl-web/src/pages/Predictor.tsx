import { useState } from "react";
import { useAPITeamList, fetchPrediction, APIPredictResponse } from "@/lib/api";
import { Loader2, Zap, Brain, Activity, ShieldAlert, CheckCircle2, Bot, AlertTriangle, TrendingUp, DollarSign, BarChart2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { Calendar as CalendarIcon } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";

// Toggle Switch Component
interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  warningLabel: string;
}

function ToggleSwitch({ checked, onChange, label, warningLabel }: ToggleSwitchProps) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={cn(
        "w-full flex items-center justify-between rounded-lg px-4 py-3 border transition-all duration-200",
        checked
          ? "bg-warning/10 border-warning/40 shadow-inner shadow-warning/5"
          : "bg-secondary/30 border-border/50 hover:border-border"
      )}
    >
      <div className="flex items-center gap-2">
        <AlertTriangle className={cn("h-4 w-4 transition-colors", checked ? "text-warning" : "text-muted-foreground/40")} />
        <span className={cn("text-sm font-medium transition-colors", checked ? "text-warning" : "text-muted-foreground")}>
          {checked ? warningLabel : label}
        </span>
      </div>
      <div
        className={cn(
          "w-11 h-6 rounded-full relative transition-all duration-200 shrink-0",
          checked ? "bg-warning" : "bg-secondary"
        )}
      >
        <div
          className={cn(
            "absolute top-1 h-4 w-4 rounded-full bg-white shadow-sm transition-all duration-200",
            checked ? "left-6" : "left-1"
          )}
        />
      </div>
    </button>
  );
}

const Predictor = () => {
  const { data: teamList, isLoading: loadingTeams } = useAPITeamList();

  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [homeMissingKey, setHomeMissingKey] = useState(false);
  const [awayMissingKey, setAwayMissingKey] = useState(false);
  const [matchDate, setMatchDate] = useState<Date | undefined>(undefined);

  const [prediction, setPrediction] = useState<APIPredictResponse | null>(null);
  const [loadingPred, setLoadingPred] = useState(false);
  const [error, setError] = useState("");

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) {
      setError("Por favor selecciona ambos equipos");
      return;
    }
    if (homeTeam === awayTeam) {
      setError("Los equipos local y visitante no pueden ser el mismo");
      return;
    }

    setError("");
    setLoadingPred(true);
    setPrediction(null);
    try {
      const payload: any = { homeTeam, awayTeam, homeMissingKey, awayMissingKey };
      if (matchDate) payload.date = format(matchDate, "yyyy-MM-dd");
      const res = await fetchPrediction(payload);
      setPrediction(res);
    } catch (err) {
      setError("Error al obtener la predicción. Asegúrate de que el motor ML esté en ejecución.");
    } finally {
      setLoadingPred(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-1 tracking-tight">
          Predictor Neuronal
        </h1>
        <p className="text-sm text-muted-foreground">Simula cualquier enfrentamiento usando el Motor de IA V2.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input Form — Simulator-style panel */}
        <div className="lg:col-span-1 glass-card p-6 h-fit sticky top-6">
          <h2 className="text-lg font-semibold text-foreground mb-5 flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Parámetros del Partido
          </h2>

          <div className="space-y-5">
            {/* Home Team */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Equipo Local</label>
              <Select value={homeTeam} onValueChange={setHomeTeam}>
                <SelectTrigger className="w-full bg-secondary/50 border-border h-11 focus:ring-primary/50">
                  <SelectValue placeholder="— Seleccionar equipo —" />
                </SelectTrigger>
                <SelectContent>
                  {teamList?.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
              <ToggleSwitch
                checked={homeMissingKey}
                onChange={setHomeMissingKey}
                label="Plantilla completa"
                warningLabel="Jugador clave ausente"
              />
            </div>

            {/* Away Team */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Equipo Visitante</label>
              <Select value={awayTeam} onValueChange={setAwayTeam}>
                <SelectTrigger className="w-full bg-secondary/50 border-border h-11 focus:ring-primary/50">
                  <SelectValue placeholder="— Seleccionar equipo —" />
                </SelectTrigger>
                <SelectContent>
                  {teamList?.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
              <ToggleSwitch
                checked={awayMissingKey}
                onChange={setAwayMissingKey}
                label="Plantilla completa"
                warningLabel="Jugador clave ausente"
              />
            </div>

            {/* Date Time Machine */}
            <div className="space-y-2 pt-4 border-t border-border/50">
              <label className="text-sm font-medium text-primary uppercase tracking-wider">⏳ Viaje en el Tiempo (Opcional)</label>
              <p className="text-xs text-muted-foreground">Simula como si estuvieras en una fecha pasada. El modelo solo usará información hasta ese momento exacto.</p>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal bg-secondary/50 border-border h-11 hover:bg-secondary/70 hover:text-foreground",
                      !matchDate && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {matchDate ? format(matchDate, "PPP", { locale: es }) : <span>Selecciona una fecha del pasado...</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-background border-border" align="start">
                  <Calendar
                    mode="single"
                    selected={matchDate}
                    onSelect={setMatchDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {(homeMissingKey || awayMissingKey) && (
            <div className="mt-4 bg-warning/5 border border-warning/25 rounded-lg p-3.5 flex gap-2.5 text-xs text-warning leading-normal">
              <Bot className="h-4 w-4 shrink-0 text-warning" />
              <div>
                <span className="font-bold">Nota del Modelo:</span> El motor predictivo actual está optimizado sobre una matriz matemática de 27 variables de rendimiento continuo (ELO, goles, xG, tiros). La ausencia de jugadores clave se incluye de manera ilustrativa y no altera la probabilidad numérica en esta versión del modelo.
              </div>
            </div>
          )}

          {error && <p className="mt-4 text-destructive text-sm font-medium bg-destructive/10 p-3 rounded-md">{error}</p>}

          <button
            onClick={handlePredict}
            disabled={loadingPred || loadingTeams}
            className="w-full mt-5 bg-primary text-primary-foreground font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-primary/20 hover:bg-primary/90 hover:shadow-primary/40 disabled:opacity-50"
          >
            {loadingPred ? <Loader2 className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
            {loadingPred ? "Analizando Redes Neuronales..." : "Generar Predicción"}
          </button>
        </div>

        {/* Output Panel */}
        <div className="glass-card p-6 flex flex-col min-h-[520px]">
          {prediction ? (
            <div className="space-y-6 animate-fade-in flex-1">
              <div className="text-center pb-6 border-b border-border/50">
                <h2 className="text-xl font-bold text-foreground">Análisis Completo</h2>
                <div className="flex justify-center items-center gap-6 mt-4">
                  <div className="text-center">
                    <p className="text-sm font-semibold">{prediction.homeTeam}</p>
                    <p className="text-xs text-muted-foreground">Elo: {prediction.homeElo.toFixed(1)}</p>
                    {prediction.homeForm && (
                      <div className="flex gap-1 justify-center mt-1">
                        <span className="text-[10px] bg-primary/15 text-primary rounded-full px-2 py-0.5">{prediction.homeForm.pts?.toFixed(1) ?? "—"} pts</span>
                      </div>
                    )}
                  </div>
                  <span className="text-muted-foreground font-mono text-sm px-3 py-1.5 bg-secondary rounded-lg">VS</span>
                  <div className="text-center">
                    <p className="text-sm font-semibold">{prediction.awayTeam}</p>
                    <p className="text-xs text-muted-foreground">Elo: {prediction.awayElo.toFixed(1)}</p>
                    {prediction.awayForm && (
                      <div className="flex gap-1 justify-center mt-1">
                        <span className="text-[10px] bg-info/15 text-info rounded-full px-2 py-0.5">{prediction.awayForm.pts?.toFixed(1) ?? "—"} pts</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-success" /> Mercados por Probabilidad
                </h3>
                {prediction.predictions.map((p, i) => (
                  <div
                    key={i}
                    className={cn(
                      "border rounded-lg p-4 flex flex-col gap-2 relative overflow-hidden transition-colors",
                      i === 0
                        ? "bg-primary/5 border-primary/30"
                        : "bg-secondary/30 border-border/50 hover:border-border"
                    )}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        {i === 0 && <span className="text-[9px] bg-primary text-primary-foreground font-bold px-1.5 py-0.5 rounded uppercase tracking-wide">Top</span>}
                        <span className="font-semibold text-foreground text-sm">{p.Market}</span>
                      </div>
                      <ConfidenceBadge confidence={Math.round(p.Probability * 100)} />
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-2 bg-background rounded-full overflow-hidden border border-border">
                        <div
                          className={cn("h-full transition-all duration-1000 ease-out rounded-full", i === 0 ? "bg-primary" : "bg-muted-foreground/50")}
                          style={{ width: `${(p.Probability * 100).toFixed(0)}%` }}
                        />
                      </div>
                      <span className={cn("text-sm mono font-bold", i === 0 ? "text-primary" : "text-foreground")}>
                        {(p.Probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
                {prediction.predictions.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground flex flex-col items-center gap-2">
                    <ShieldAlert className="h-8 w-8 text-muted-foreground/50" />
                    <p>El modelo no encontró mercados con suficiente valor para este partido.</p>
                  </div>
                )}
              </div>

              {/* Kelly Financial Recommendation */}
              {(() => {
                // Find the best bet based on Expected Value (EV)
                const bestBet = [...prediction.predictions].sort((a, b) => (b.ExpectedValue ?? 0) - (a.ExpectedValue ?? 0))[0];
                if (!bestBet) return null;
                const ev = bestBet.ExpectedValue ?? 0;
                const stakePct = bestBet.RecommendedStakePct ?? 0;
                const fairOdds = bestBet.FairOdds ?? 0;
                return (
                  <div className={cn(
                    "rounded-lg border p-4 space-y-3",
                    ev > 0 ? "bg-success/5 border-success/30" : "bg-destructive/5 border-destructive/20"
                  )}>
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-success" /> Recomendación Financiera (Kelly)
                    </h3>
                    
                    {ev > 0 ? (
                      <div className="bg-secondary/40 p-2.5 rounded border border-border/50 text-xs">
                        <span className="text-muted-foreground">Mercado con mayor EV:</span>{" "}
                        <span className="font-bold text-primary">{bestBet.Market}</span>
                      </div>
                    ) : (
                      <div className="bg-secondary/40 p-2.5 rounded border border-border/50 text-xs">
                        <span className="text-muted-foreground">Mercado con mayor EV:</span>{" "}
                        <span className="font-medium text-foreground">Ninguno (Sin valor esperado positivo)</span>
                      </div>
                    )}

                    <div className="grid grid-cols-3 gap-3">
                      <div className="text-center">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">EV</p>
                        <p className={cn("text-lg font-bold", ev > 0 ? "text-success" : "text-destructive")}>
                          {ev > 0 ? "+" : ""}{(ev * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Cuota Justa</p>
                        <p className="text-lg font-bold text-foreground">{fairOdds.toFixed(2)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Stake Kelly</p>
                        <p className={cn("text-lg font-bold", stakePct > 0 ? "text-primary" : "text-muted-foreground")}>
                          {stakePct > 0 ? `${stakePct.toFixed(1)}%` : "—"}
                        </p>
                      </div>
                    </div>
                    {ev <= 0 ? (
                      <p className="text-xs text-destructive/80 flex items-center gap-1">
                        <ShieldAlert className="h-3 w-3" /> EV negativo en todos los mercados — Kelly no recomienda apostar en este partido.
                      </p>
                    ) : (
                      <p className="text-xs text-success/80 flex items-center gap-1">
                        <BarChart2 className="h-3 w-3" /> Se recomienda apostar el {stakePct.toFixed(1)}% del bankroll en {bestBet.Market}.
                      </p>
                    )}
                  </div>
                );
              })()}
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 opacity-50 space-y-4">
              <Bot className="h-16 w-16 text-muted-foreground/30" />
              <div className="space-y-1">
                <p className="text-lg font-medium text-foreground">Esperando Datos</p>
                <p className="text-sm text-muted-foreground">Selecciona dos equipos y presiona "Generar Predicción" para iniciar el análisis.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Predictor;
