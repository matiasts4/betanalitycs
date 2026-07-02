import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { 
  Play, 
  DollarSign, 
  TrendingUp, 
  Activity, 
  BarChart2, 
  Download, 
  AlertTriangle, 
  Percent, 
  Calculator, 
  ChevronDown, 
  ChevronUp, 
  Database,
  Loader2
} from "lucide-react";
import { fetchSimulation, fetchPerformance, useAPISeasons, APISimulateParams, APISimulateResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend
} from "recharts";

const Simulator = () => {
  const [activeTab, setActiveTab] = useState<"simulate" | "performance">("simulate");
  const [expandedSimRows, setExpandedSimRows] = useState<Record<number, boolean>>({});
  const [expandedPerfRows, setExpandedPerfRows] = useState<Record<number, boolean>>({});

  const { data: seasons } = useAPISeasons();

  // Simulation parameters
  const [params, setParams] = useState<APISimulateParams>({
    initialBankroll: 1000,
    stake: 5,
    nMatches: 100,
    strategy: "variable",
    season: "2425",
    minOdds: 1.00,
    minEv: 0.0,
    model: "xgboost",
    compareModel: "logistic",
    minProb: 50,
    selectionCriteria: "combined",
    allowedMarkets: ["1X2", "Double Chance", "Over 2.5", "Under 2.5", "BTTS", "Clean Sheet"]
  });

  // Simulation Mutation
  const simMutation = useMutation({
    mutationFn: (p: APISimulateParams) => fetchSimulation(p),
  });

  // Live Performance Query
  const { data: perfData, isLoading: loadingPerf, refetch: refetchPerf } = useQuery({
    queryKey: ["performance_data"],
    queryFn: fetchPerformance,
    staleTime: 60000
  });

  const handleSimulate = (e: React.FormEvent) => {
    e.preventDefault();
    setExpandedSimRows({});
    simMutation.mutate(params);
  };

  const handleExportCSV = () => {
    const simResult = simMutation.data;
    if (!simResult) return;
    const headers = ["Fecha", "Partido", "Prediccion", "Cuota", "Resultado", "Beneficio", "Balance"];
    const rows = simResult.historyData.map(r => 
      [r.date, r.match, r.prediction, r.odds, r.result, r.profit, r.balance].join(",")
    );
    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `simulacion_${params.model}_${params.season}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleSimRow = (idx: number) => {
    setExpandedSimRows(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const togglePerfRow = (idx: number) => {
    setExpandedPerfRows(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const simData = simMutation.data as APISimulateResponse | undefined;

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Consola Cuantitativa</h1>
        <p className="text-muted-foreground">
          Simula estrategias de inversión deportiva o analiza el rendimiento acumulado en tiempo real de tu portafolio de Machine Learning.
        </p>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-border/50 gap-4 mb-4">
        <button
          onClick={() => setActiveTab("simulate")}
          className={cn(
            "pb-3 text-sm font-semibold transition-all border-b-2 px-1 relative -bottom-[2px]",
            activeTab === "simulate" 
              ? "border-primary text-primary" 
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          Simulador de Estrategias
        </button>
        <button
          onClick={() => setActiveTab("performance")}
          className={cn(
            "pb-3 text-sm font-semibold transition-all border-b-2 px-1 relative -bottom-[2px]",
            activeTab === "performance" 
              ? "border-primary text-primary" 
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          Rendimiento del Portafolio
        </button>
      </div>

      {activeTab === "simulate" && (
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Controls Panel */}
          <div className="lg:col-span-1 glass-card p-6 h-fit sticky top-6 space-y-6">
            <div className="flex items-center gap-2 border-b border-border/50 pb-4">
              <Calculator className="w-5 h-5 text-primary" /> 
              <h2 className="text-lg font-semibold text-foreground">Parámetros</h2>
            </div>
            
            <form onSubmit={handleSimulate} className="space-y-5">
              {/* Machine Learning Models */}
              <div className="space-y-3">
                <label className="text-sm font-semibold text-foreground">Modelos Predictivos</label>
                
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Modelo Principal</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.model}
                    onChange={(e) => setParams({ ...params, model: e.target.value })}
                  >
                    <option value="xgboost">Portafolio Híbrido Calibrado (Óptimo)</option>
                  </select>
                  <p className="text-[10px] text-muted-foreground mt-1">El modelo principal utiliza el ensamble híbrido óptimo (XGBoost/Reg.Log/MLP) calibrado por mercado.</p>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Comparar con...</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.compareModel}
                    onChange={(e) => setParams({ ...params, compareModel: e.target.value })}
                  >
                    <option value="none">Sin Comparación</option>
                    <option value="logistic">Consenso ELO del Mercado (Línea Base)</option>
                  </select>
                </div>
              </div>

              {/* Odds Source */}
              <div className="space-y-3 pt-4 border-t border-border/50">
                <label className="text-sm font-semibold text-foreground">Origen de Cuotas</label>
                <div className="space-y-1.5">
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.oddsSource || "average"}
                    onChange={(e) => setParams({ ...params, oddsSource: e.target.value as any })}
                  >
                    <option value="average">Promedio / Bet365</option>
                    <option value="maximum">Máximas (Line Shopping)</option>
                  </select>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    Compara el rendimiento con cuotas promedio frente a tomar la mejor cuota disponible del mercado.
                  </p>
                </div>
              </div>

              {/* Financial Parameters */}
              <div className="space-y-3 pt-4 border-t border-border/50">
                <label className="text-sm font-semibold text-foreground">Gestión de Riesgo</label>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Capital Inicial ($)</label>
                  <input
                    type="number"
                    min="10"
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.initialBankroll}
                    onChange={(e) => setParams({ ...params, initialBankroll: Number(e.target.value) })}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Estrategia</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.strategy || "fixed"}
                    onChange={(e) => setParams({ 
                      ...params, 
                      strategy: e.target.value as any,
                      stake: e.target.value === "variable" ? 5 : 10
                    })}
                  >
                    <option value="fixed">Plana Estándar (Flat Staking)</option>
                    <option value="variable">Criterio de Kelly (Óptimo)</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">
                    {params.strategy === "variable" ? "Límite Apuesta (%)" : "Apuesta Fija ($)"}
                  </label>
                  <input
                    type="number"
                    min="1"
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.stake}
                    onChange={(e) => setParams({ ...params, stake: Number(e.target.value) })}
                  />
                </div>
              </div>

              {/* Data Filters */}
              <div className="space-y-3 pt-4 border-t border-border/50">
                <label className="text-sm font-semibold text-foreground">Filtros de Datos</label>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Temporada (Test Set)</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.season || "all"}
                    onChange={(e) => setParams({ ...params, season: e.target.value })}
                  >
                    <option value="all">Últimos N partidos</option>
                    {seasons?.map((s) => (
                      <option key={s.season} value={String(s.season)}>Temporada {s.label}</option>
                    ))}
                  </select>
                </div>

                {params.season === "all" && (
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Cantidad de Partidos</label>
                    <input
                      type="number"
                      min="10"
                      max="1000"
                      className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                      value={params.nMatches}
                      onChange={(e) => setParams({ ...params, nMatches: Number(e.target.value) })}
                    />
                  </div>
                )}
                
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Cuota Mínima</label>
                  <input
                    type="number"
                    step="0.05"
                    min="1.0"
                    max="10.0"
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.minOdds || 1.0}
                    onChange={(e) => setParams({ ...params, minOdds: Number(e.target.value) })}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">EV Mínimo Requerido (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="50"
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.minEv || 0}
                    onChange={(e) => setParams({ ...params, minEv: Number(e.target.value) })}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground">Filtro de Selección</label>
                  <select
                    className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                    value={params.selectionCriteria || "combined"}
                    onChange={(e) => setParams({ ...params, selectionCriteria: e.target.value as any })}
                  >
                    <option value="combined">EV Mínimo + Confianza Mínima</option>
                    <option value="ev_only">Solo EV Mínimo (Filtro EV)</option>
                    <option value="prob_only">Solo Confianza Mínima (Filtro %)</option>
                  </select>
                </div>

                {(params.selectionCriteria === "combined" || params.selectionCriteria === "prob_only") && (
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground">Confianza Mínima (%)</label>
                    <input
                      type="number"
                      min="30"
                      max="95"
                      step="1"
                      className="w-full bg-secondary/50 border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                      value={params.minProb || 50}
                      onChange={(e) => setParams({ ...params, minProb: Number(e.target.value) })}
                    />
                  </div>
                )}

                <div className="space-y-1.5 pt-2">
                  <label className="text-xs font-medium text-muted-foreground block mb-1">Mercados Permitidos</label>
                  <div className="space-y-1 bg-secondary/20 p-2.5 rounded-lg border border-border/50 max-h-[140px] overflow-y-auto">
                    {[
                      { key: "1X2", label: "1X2 (Ganador)" },
                      { key: "Double Chance", label: "Doble Oportunidad" },
                      { key: "Over 2.5", label: "Over 2.5 Goles" },
                      { key: "Under 2.5", label: "Under 2.5 Goles" },
                      { key: "BTTS", label: "Ambos Marcan (BTTS)" },
                      { key: "Clean Sheet", label: "Valla Invicta" }
                    ].map((mkt) => {
                      const isChecked = (params.allowedMarkets ?? []).includes(mkt.key);
                      return (
                        <label key={mkt.key} className="flex items-center gap-2 text-xs text-foreground cursor-pointer py-0.5 hover:text-primary transition-colors">
                          <input
                            type="checkbox"
                            className="rounded border-border bg-secondary text-primary focus:ring-primary/50"
                            checked={isChecked}
                            onChange={(e) => {
                              const current = params.allowedMarkets ?? [];
                              const updated = e.target.checked
                                ? [...current, mkt.key]
                                : current.filter(x => x !== mkt.key);
                              setParams({ ...params, allowedMarkets: updated });
                            }}
                          />
                          <span>{mkt.label}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={simMutation.isPending}
                className="w-full mt-2 bg-primary text-primary-foreground font-semibold py-2.5 rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {simMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Play className="w-4 h-4" /> Simular Modelos</>}
              </button>
            </form>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-3 space-y-6">
            {simMutation.isPending && (
              <div className="glass-card h-64 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="text-sm text-muted-foreground">Evaluando iteraciones en el dataset de validación...</p>
                </div>
              </div>
            )}

            {simData && !simMutation.isPending && (
              <>
                {/* Visual warning for in-sample predictions */}
                <div className="glass-card border-warning/20 bg-warning/5 p-4 flex items-start gap-3 text-xs mb-6">
                  <AlertTriangle className="h-4 w-4 text-warning shrink-0 mt-0.5" />
                  <div className="space-y-1 text-muted-foreground">
                    <p className="font-semibold text-foreground flex items-center gap-1.5">
                      Evaluación de Datos Históricos (In-Sample)
                    </p>
                    <p className="leading-relaxed">
                      El conjunto de partidos evaluado para la temporada <strong className="text-foreground">
                        {params.season === "all" 
                          ? `los últimos ${params.nMatches} partidos` 
                          : (seasons?.find(s => String(s.season) === params.season)?.label || `Temporada ${params.season}`)}
                      </strong> forma parte del conjunto de datos histórico en el cual fueron entrenados los modelos de producción. Dado que los clasificadores predictivos se entrenan con todo el historial de juego disponible para maximizar la exactitud de las predicciones en vivo, esta simulación retrospectiva representa un rendimiento de entrenamiento ("Dentro de Muestra"). Las métricas de exactitud ciega real (Out-of-Sample) se validan únicamente sobre partidos futuros no jugados.
                    </p>
                  </div>
                </div>

                {/* Primary Model KPIs */}
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-3 px-1 border-l-2 border-primary pl-2">
                    Rendimiento: {params.model.toUpperCase()}
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="glass-card p-4">
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1"><TrendingUp className="w-3 h-3"/> Yield (ROI)</p>
                      <p className={`text-xl font-bold ${simData.performanceSummary.yieldPct >= 0 ? "text-success" : "text-destructive"}`}>
                        {simData.performanceSummary.yieldPct > 0 ? "+" : ""}{simData.performanceSummary.yieldPct}%
                      </p>
                    </div>
                    <div className="glass-card p-4">
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Max Drawdown</p>
                      <p className="text-xl font-bold text-destructive">
                        -{simData.performanceSummary.maxDrawdown}%
                      </p>
                    </div>
                    <div className="glass-card p-4">
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1"><Percent className="w-3 h-3"/> Tasa Acierto</p>
                      <p className="text-xl font-bold text-foreground">
                        {simData.performanceSummary.winRate}%
                      </p>
                    </div>
                    <div className="glass-card p-4">
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1"><DollarSign className="w-3 h-3"/> Beneficio Neto</p>
                      <p className={`text-xl font-bold ${simData.performanceSummary.netProfit >= 0 ? "text-success" : "text-destructive"}`}>
                        ${simData.performanceSummary.netProfit.toLocaleString(undefined, {maximumFractionDigits: 1})}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Compare Model KPIs */}
                {simData.performanceSummaryB && (
                  <div>
                    <h3 className="text-sm font-semibold text-foreground mb-3 px-1 border-l-2 border-warning pl-2">
                      Rendimiento: {params.compareModel?.toUpperCase()} (Comparación)
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="glass-card p-3 border-warning/20">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Yield (ROI)</p>
                        <p className={`text-lg font-bold ${simData.performanceSummaryB.yieldPct >= 0 ? "text-warning" : "text-destructive"}`}>
                          {simData.performanceSummaryB.yieldPct > 0 ? "+" : ""}{simData.performanceSummaryB.yieldPct}%
                        </p>
                      </div>
                      <div className="glass-card p-3 border-warning/20">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Max Drawdown</p>
                        <p className="text-lg font-bold text-destructive">
                          -{simData.performanceSummaryB.maxDrawdown}%
                        </p>
                      </div>
                      <div className="glass-card p-3 border-warning/20">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Tasa Acierto</p>
                        <p className="text-lg font-bold text-foreground">
                          {simData.performanceSummaryB.winRate}%
                        </p>
                      </div>
                      <div className="glass-card p-3 border-warning/20">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Beneficio Neto</p>
                        <p className={`text-lg font-bold ${simData.performanceSummaryB.netProfit >= 0 ? "text-warning" : "text-destructive"}`}>
                          ${simData.performanceSummaryB.netProfit.toLocaleString(undefined, {maximumFractionDigits: 1})}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Main Comparison Chart */}
                <div className="glass-card p-6">
                  <h2 className="text-sm font-semibold text-foreground mb-4">
                    Evolución del Capital (Curva de Aprendizaje) {simData.performanceSummary.period && <span className="text-xs text-primary font-normal ml-2">({simData.performanceSummary.period})</span>}
                  </h2>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={simData.profitChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" vertical={false} />
                        <XAxis dataKey="name" stroke="hsl(215 20% 55%)" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="hsl(215 20% 55%)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
                        <Tooltip
                          contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", color: "hsl(213 31% 91%)" }}
                        />
                        <Legend verticalAlign="top" height={36} />
                        <Line
                          name={`Capital - ${params.model.toUpperCase()}`}
                          type="monotone"
                          dataKey="bankrollA"
                          stroke="hsl(217 91% 60%)"
                          strokeWidth={3}
                          dot={false}
                          activeDot={{ r: 6 }}
                        />
                        {simData.performanceSummaryB && (
                          <Line
                            name={`Capital - ${params.compareModel.toUpperCase()}`}
                            type="monotone"
                            dataKey="bankrollB"
                            stroke="hsl(35 91% 60%)"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Error Analysis Chart */}
                <div className="glass-card p-6">
                  <h2 className="text-sm font-semibold text-foreground mb-1">Análisis de Errores por Rango de Cuota</h2>
                  <p className="text-xs text-muted-foreground mb-4">Muestra en qué rangos de probabilidad el modelo principal pierde o gana dinero.</p>
                  <div className="h-60">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={simData.profitByOddsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" vertical={false} />
                        <XAxis dataKey="oddsRange" stroke="hsl(215 20% 55%)" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="hsl(215 20% 55%)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
                        <Tooltip
                          cursor={{fill: 'hsl(220 25% 15%)'}}
                          contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", color: "hsl(213 31% 91%)" }}
                        />
                        <Bar 
                          name="Beneficio Neto ($)" 
                          dataKey="profit" 
                          fill="hsl(217 91% 60%)" 
                          radius={[4, 4, 0, 0]}
                          activeBar={{ stroke: 'hsl(217 91% 70%)', strokeWidth: 2 }}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Simulation History Table */}
                <div className="glass-card overflow-hidden">
                  <div className="p-4 border-b border-border/50 flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <Database className="w-4 h-4 text-primary" />
                      Registro de Validaciones (Expandible)
                    </h2>
                    <button 
                      onClick={handleExportCSV}
                      className="flex items-center gap-2 text-xs font-medium bg-secondary text-foreground px-3 py-1.5 rounded-md hover:bg-secondary/80 transition-colors"
                    >
                      <Download className="w-3 h-3" /> Exportar Notebook CSV
                    </button>
                  </div>
                  <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-background/95 backdrop-blur z-10 border-b border-border/50">
                        <tr className="text-xs text-muted-foreground uppercase tracking-wider">
                          <th className="p-4 w-6"></th>
                          <th className="text-left p-4 font-medium">Fecha</th>
                          <th className="text-left p-4 font-medium">Partido</th>
                          <th className="text-left p-4 font-medium">Predicción</th>
                          <th className="text-right p-4 font-medium">Cuota</th>
                          {params.strategy === "variable" && (
                            <>
                              <th className="text-right p-4 font-medium">EV</th>
                              <th className="text-right p-4 font-medium">Stake</th>
                            </>
                          )}
                          <th className="text-center p-4 font-medium">Resultado</th>
                          <th className="text-right p-4 font-medium">P/L ($)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {simData.historyData.map((row, i) => {
                          const isExpanded = expandedSimRows[i];
                          return (
                            <>
                              <tr 
                                key={`row-${i}`} 
                                onClick={() => toggleSimRow(i)}
                                className={cn(
                                  "border-b border-border/50 last:border-0 hover:bg-secondary/20 transition-colors cursor-pointer",
                                  isExpanded && "bg-secondary/10 hover:bg-secondary/15"
                                )}
                              >
                                <td className="p-4 text-center">
                                  {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                                </td>
                                <td className="p-4 text-muted-foreground whitespace-nowrap">{row.date}</td>
                                <td className="p-4 font-semibold text-foreground whitespace-nowrap">{row.match}</td>
                                <td className="p-4 text-primary whitespace-nowrap font-medium">{row.prediction}</td>
                                <td className="p-4 text-right tabular-nums font-mono">{row.odds.toFixed(2)}</td>
                                {params.strategy === "variable" && (
                                  <>
                                    <td className={`p-4 text-right tabular-nums text-xs font-mono font-semibold ${
                                      (row.ev ?? 0) >= 0 ? 'text-success' : 'text-destructive'
                                    }`}>
                                      {(row.ev ?? 0) >= 0 ? '+' : ''}{((row.ev ?? 0) * 100).toFixed(1)}%
                                    </td>
                                    <td className="p-4 text-right tabular-nums text-xs text-muted-foreground whitespace-nowrap">
                                      {row.stakeAmount != null ? `$${row.stakeAmount.toLocaleString(undefined, {maximumFractionDigits: 1})}` : '—'}
                                    </td>
                                  </>
                                )}
                                <td className="p-4 text-center">
                                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                    row.result === "Won" ? "bg-success/20 text-success" : "bg-destructive/20 text-destructive"
                                  }`}>
                                    {row.result === "Won" ? "Acertada" : "Fallada"}
                                  </span>
                                </td>
                                <td className={`p-4 text-right font-mono font-semibold ${row.profit >= 0 ? "text-success" : "text-destructive"}`}>
                                  {row.profit >= 0 ? "+" : ""}{row.profit.toLocaleString(undefined, {maximumFractionDigits: 1})}
                                </td>
                              </tr>

                              {isExpanded && (
                                <tr key={`expanded-${i}`} className="bg-secondary/15">
                                  <td colSpan={params.strategy === "variable" ? 9 : 7} className="p-5 border-b border-border/50">
                                    <div className="grid lg:grid-cols-2 gap-6 text-left animate-fade-in">
                                      {/* Detailed Input Log */}
                                      <div>
                                        <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                                          <Database className="w-3.5 h-3.5 text-primary" />
                                          Variables del Modelo (Capa 1 Input)
                                        </h4>
                                        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px] font-mono">
                                          {row.features && Object.entries(row.features).map(([key, val]) => (
                                            <div key={key} className="flex justify-between border-b border-border/20 pb-0.5">
                                              <span className="text-muted-foreground truncate mr-2" title={key}>{key}</span>
                                              <span className="text-foreground font-semibold">
                                                {typeof val === 'number' ? val.toFixed(2).replace(/\.00$/, '') : String(val)}
                                              </span>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                      {/* Detailed Output Log */}
                                      <div>
                                        <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                                          <Activity className="w-3.5 h-3.5 text-primary" />
                                          Predicciones de Capa 1 y 2 (Output)
                                        </h4>
                                        <div className="space-y-1.5">
                                          {row.predictions && row.predictions.map((pred, pIdx) => (
                                            <div key={pIdx} className="flex items-center justify-between p-2 rounded bg-background/50 border border-border/50 hover:border-primary/50 transition-all">
                                              <span className="text-xs font-semibold text-foreground">{pred.market}</span>
                                              <div className="flex items-center gap-3 text-[11px]">
                                                <span className="text-muted-foreground">Cuota: <span className="text-foreground font-semibold">{pred.odds.toFixed(2)}</span></span>
                                                <span className="text-primary font-bold">{pred.probability.toFixed(1)}%</span>
                                                <span className={`text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded font-bold ${
                                                  pred.won ? "bg-success/20 text-success" : "bg-destructive/20 text-destructive"
                                                }`}>
                                                  {pred.won ? "Acierto" : "Fallo"}
                                                </span>
                                              </div>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    </div>
                                  </td>
                                </tr>
                              )}
                            </>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {!simData && !simMutation.isPending && (
              <div className="glass-card h-64 flex flex-col items-center justify-center text-muted-foreground">
                <BarChart2 className="w-12 h-12 mb-3 opacity-20" />
                <p>Selecciona tus modelos de ML y ejecuta la simulación para evaluar sus métricas.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "performance" && (
        <div className="space-y-6">
          {loadingPerf && (
            <div className="glass-card h-64 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}

          {!loadingPerf && perfData && (
            <>
              {/* Performance Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-card p-4 flex flex-col gap-1">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Yield (ROI)</p>
                  <p className={`text-xl font-bold ${perfData.performanceSummary.totalProfit >= 0 ? "text-success" : "text-destructive"}`}>
                    {(perfData.performanceSummary.totalProfit / (perfData.performanceSummary.totalBets || 1) * 10).toFixed(2)}%
                  </p>
                </div>
                <div className="glass-card p-4 flex flex-col gap-1">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Victorias</p>
                  <p className="text-xl font-bold text-success">{perfData.performanceSummary.wins}</p>
                </div>
                <div className="glass-card p-4 flex flex-col gap-1">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Derrotas</p>
                  <p className="text-xl font-bold text-destructive">{perfData.performanceSummary.losses}</p>
                </div>
                <div className="glass-card p-4 flex flex-col gap-1">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Beneficio Neto</p>
                  <p className={`text-xl font-bold ${perfData.performanceSummary.totalProfit >= 0 ? "text-success" : "text-destructive"}`}>
                    {perfData.performanceSummary.totalProfit >= 0 ? "+" : ""}${perfData.performanceSummary.totalProfit.toFixed(1)}
                  </p>
                </div>
              </div>

              {/* Profit Evolution Chart */}
              <div className="glass-card p-6">
                <h2 className="text-sm font-semibold text-foreground mb-4">Beneficio Real Acumulado</h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={perfData.profitChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" vertical={false} />
                      <XAxis dataKey="name" stroke="hsl(215 20% 55%)" fontSize={11} tickLine={false} axisLine={false} />
                      <YAxis stroke="hsl(215 20% 55%)" fontSize={11} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", fontSize: "12px", color: "hsl(213 31% 91%)" }} />
                      <Line type="monotone" dataKey="profit" stroke="hsl(217 91% 60%)" strokeWidth={2} dot={{ r: 3, fill: "hsl(217 91% 60%)" }} activeDot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Real Performance Table */}
              <div className="glass-card overflow-hidden">
                <div className="p-4 border-b border-border/50">
                  <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Database className="w-4 h-4 text-primary" />
                    Registro de Apuestas Reales (Expandible)
                  </h2>
                </div>
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-background/95 backdrop-blur z-10 border-b border-border/50">
                      <tr className="text-xs text-muted-foreground uppercase tracking-wider">
                        <th className="p-3 w-6"></th>
                        <th className="text-left p-3 font-medium">Fecha</th>
                        <th className="text-left p-3 font-medium">Partido</th>
                        <th className="text-left p-3 font-medium">Mercado</th>
                        <th className="text-right p-3 font-medium">Cuota</th>
                        <th className="text-center p-3 font-medium">Resultado</th>
                        <th className="text-right p-3 font-medium">P/L ($)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {perfData.historyData.map((h, idx) => {
                        const isExpanded = expandedPerfRows[idx];
                        return (
                          <>
                            <tr 
                              key={`perf-row-${idx}`} 
                              onClick={() => togglePerfRow(idx)}
                              className={cn(
                                "border-b border-border/50 last:border-0 hover:bg-secondary/20 transition-colors cursor-pointer",
                                isExpanded && "bg-secondary/10 hover:bg-secondary/15"
                              )}
                            >
                              <td className="p-3 text-center">
                                {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                              </td>
                              <td className="p-3 text-muted-foreground whitespace-nowrap">{h.date}</td>
                              <td className="p-3 font-semibold text-foreground whitespace-nowrap">{h.match}</td>
                              <td className="p-3 text-primary whitespace-nowrap font-medium">{h.prediction}</td>
                              <td className="p-3 text-right font-semibold font-mono">{h.odds.toFixed(2)}</td>
                              <td className="p-3 text-center">
                                <span className={cn(
                                  "inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold uppercase",
                                  h.result === "Won" ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"
                                )}>
                                  {h.result === "Won" ? "Acertada" : "Fallada"}
                                </span>
                              </td>
                              <td className={cn("p-3 text-right font-mono font-bold", h.profit >= 0 ? "text-success" : "text-destructive")}>
                                {h.profit >= 0 ? "+" : ""}{h.profit.toFixed(1)}
                              </td>
                            </tr>

                            {isExpanded && (
                              <tr key={`perf-expanded-${idx}`} className="bg-secondary/15">
                                <td colSpan={7} className="p-5 border-b border-border/50">
                                  <div className="grid lg:grid-cols-2 gap-6 text-left animate-fade-in">
                                    {/* Detailed Input Log */}
                                    <div>
                                      <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                                        <Database className="w-3.5 h-3.5 text-primary" />
                                        Variables del Modelo (Capa 1 Input)
                                      </h4>
                                      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px] font-mono">
                                        {h.features && Object.entries(h.features).map(([key, val]) => (
                                          <div key={key} className="flex justify-between border-b border-border/20 pb-0.5">
                                            <span className="text-muted-foreground truncate mr-2" title={key}>{key}</span>
                                            <span className="text-foreground font-semibold">
                                              {typeof val === 'number' ? val.toFixed(2).replace(/\.00$/, '') : String(val)}
                                            </span>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                    {/* Detailed Output Log */}
                                    <div>
                                      <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                                        <Activity className="w-3.5 h-3.5 text-primary" />
                                        Predicciones de Capa 1 y 2 (Output)
                                      </h4>
                                      <div className="space-y-1.5">
                                        {h.predictions && h.predictions.map((pred, pIdx) => (
                                          <div key={pIdx} className="flex items-center justify-between p-2 rounded bg-background/50 border border-border/50 hover:border-primary/50 transition-all">
                                            <span className="text-xs font-semibold text-foreground">{pred.market}</span>
                                            <div className="flex items-center gap-3 text-[11px]">
                                              <span className="text-muted-foreground">Cuota: <span className="text-foreground font-semibold">{pred.odds.toFixed(2)}</span></span>
                                              <span className="text-primary font-bold">{pred.probability.toFixed(1)}%</span>
                                              <span className={`text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded font-bold ${
                                                pred.won ? "bg-success/20 text-success" : "bg-destructive/20 text-destructive"
                                              }`}>
                                                {pred.won ? "Acierto" : "Fallo"}
                                              </span>
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          </>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Simulator;