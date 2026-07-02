import { landingData } from "@/data/landingData";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { TrendingUp, ShieldAlert, Zap, Filter, Award } from "lucide-react";
import { cn } from "@/lib/utils";

export const LandingBacktesting = () => {
  const { metaDecision } = landingData;

  const summaryStats = [
    { label: "ROI del Meta-Modelo", value: "+6.91%", detail: "Frente al -5.08% de la línea base", icon: TrendingUp },
    { label: "Mitigación de Varianza", value: "27.77%", detail: "Drawdown controlado frente al 99.42% de la línea base", icon: ShieldAlert },
    { label: "Falsos Positivos Evitados", value: "1,463", detail: "64.6% del volumen de candidatos sospechosos bloqueados", icon: Filter },
    { label: "Apuestas Realizadas", value: "802", detail: "Picks de alta confianza sobre 2,265 eventos simulados", icon: Zap },
  ];

  // Colors for Recharts lines
  const colors = {
    lineaBase: "#ef4444",   // Red
    metaModelo: "#3b82f6",  // Blue (Primary)
    sistemaDual: "#06b6d4", // Cyan (Info)
  };

  const barChartData = metaDecision.configs.map((config) => ({
    name: config.configName.split(" (")[0], // Short name
    ROI: config.roi,
  }));

  return (
    <div className="py-12 px-6 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-8rem)]">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-foreground mb-4">
          Motor de Inversión y Backtesting Real
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Evaluamos la robustez financiera de BetAnalytics sobre una línea temporal cronológica de <strong>2,265 partidos reales</strong> con cuotas 100% de <strong>Bet365</strong>. Comparamos la eficacia de los filtros cuantitativos y del motor de Meta-Labeling.
        </p>
      </div>

      {/* Summary Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        {summaryStats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="glass-card p-6 bg-card/30 border border-border/40 hover:border-primary/20 transition-all duration-300">
              <div className="flex justify-between items-start mb-3">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {stat.label}
                </span>
                <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
                  <Icon className="h-4 w-4" />
                </div>
              </div>
              <p className="text-3xl font-black tracking-tight text-foreground mb-1 mono">
                {stat.value}
              </p>
              <p className="text-xs text-muted-foreground leading-normal">
                {stat.detail}
              </p>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid lg:grid-cols-5 gap-8 mb-12 items-start">
        {/* Left: Capital Growth Line Chart (3 series) */}
        <div className="lg:col-span-3 glass-card p-6 md:p-8 bg-card/30 border border-border/40 flex flex-col h-[420px]">
          <div className="mb-6">
            <h3 className="text-base font-bold text-foreground">
              Trayectorias de Capital (Walk-Forward Simulation)
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Evolución cronológica de la banca ($1,000 USD iniciales) en mercados reales de la Premier League.
            </p>
          </div>

          <div className="flex-grow min-h-0 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={metaDecision.crecimiento}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                <XAxis
                  dataKey="step"
                  tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[500, 2000]}
                  tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `$${val}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(var(--foreground))",
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "11px", paddingTop: "15px" }}
                />
                <Line
                  name="Línea Base (Capa 1)"
                  type="monotone"
                  dataKey="lineaBase"
                  stroke={colors.lineaBase}
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: colors.lineaBase }}
                  activeDot={{ r: 5 }}
                />
                <Line
                  name="Solo Meta-Modelo (Capa 2)"
                  type="monotone"
                  dataKey="metaModelo"
                  stroke={colors.metaModelo}
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: colors.metaModelo }}
                  activeDot={{ r: 5 }}
                />
                <Line
                  name="Sistema Dual (Óptimo)"
                  type="monotone"
                  dataKey="sistemaDual"
                  stroke={colors.sistemaDual}
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: colors.sistemaDual }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: ROI comparison bar chart */}
        <div className="lg:col-span-2 glass-card p-6 md:p-8 bg-card/30 border border-border/40 flex flex-col h-[420px]">
          <div className="mb-6">
            <h3 className="text-base font-bold text-foreground">
              Comparativa de ROI Neto (%)
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Retorno porcentual de inversión por configuración del motor cuantitativo.
            </p>
          </div>

          <div className="flex-grow min-h-0 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={barChartData}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `${val}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(var(--foreground))",
                  }}
                />
                <Bar
                  dataKey="ROI"
                  fill="hsl(var(--primary))"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={40}
                >
                  {barChartData.map((entry, index) => {
                    const isPositive = entry.ROI >= 0;
                    return (
                      <Cell
                        key={`cell-${index}`}
                        fill={isPositive ? "hsl(var(--success))" : "hsl(var(--destructive))"}
                        fillOpacity={0.8}
                      />
                    );
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Real Simulation Table */}
      <div className="glass-card overflow-hidden border border-border/40 mb-12">
        <div className="p-4 border-b border-border/40 bg-secondary/20">
          <h3 className="text-sm font-bold text-foreground">Tabla de Resultados Consolidados (Portafolio Multimercado)</h3>
        </div>
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="bg-secondary/40 border-b border-border/40 text-muted-foreground font-semibold">
              <th className="p-3">Configuración de Decisión</th>
              <th className="p-3 text-right">Banca Final</th>
              <th className="p-3 text-right">ROI Neto</th>
              <th className="p-3 text-center">Apuestas Colocadas</th>
              <th className="p-3 text-center">Apuestas Evitadas</th>
              <th className="p-3 text-right">Max Drawdown</th>
              <th className="p-3">Diagnóstico de Riesgo</th>
            </tr>
          </thead>
          <tbody>
            {metaDecision.configs.map((row, index) => {
              const isProfit = row.roi >= 0;
              return (
                <tr
                  key={index}
                  className={cn(
                    "border-b border-border/20 hover:bg-secondary/10 transition-colors",
                    row.configName.includes("Óptimo") || row.configName.includes("Meta-Modelo") ? "bg-success/5" : ""
                  )}
                >
                  <td className="p-3 font-semibold text-foreground">{row.configName}</td>
                  <td className="p-3 text-right mono font-bold text-foreground">${row.bankroll.toFixed(2)}</td>
                  <td className={cn("p-3 text-right mono font-bold", isProfit ? "text-success" : "text-destructive")}>
                    {isProfit ? "+" : ""}{row.roi.toFixed(2)}%
                  </td>
                  <td className="p-3 text-center mono text-muted-foreground">{row.bets}</td>
                  <td className="p-3 text-center mono text-muted-foreground">{row.avoided}</td>
                  <td className="p-3 text-right mono text-destructive font-semibold">{row.drawdown.toFixed(2)}%</td>
                  <td className="p-3 font-medium text-muted-foreground">{row.diagnostic}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Explanatory Section */}
      <div className="border-t border-border/40 pt-12 mt-6 text-sm text-muted-foreground leading-relaxed space-y-4">
        <h2 className="text-lg font-bold text-foreground tracking-tight flex items-center gap-2">
          <Award className="h-5 w-5 text-primary" /> Justificación del Motor de Meta-Decisión
        </h2>
        <p>
          En el mercado tradicional de apuestas, el cobro del <strong>overround comercial</strong> (~6.38% en Bet365) empuja sistemáticamente las cuentas al terreno de pérdidas si solo se apuesta basándose en la exactitud bruta del clasificador primario (Capa 1). Nuestra Línea Base Real lo demuestra al sufrir un drawdown acumulado del <strong>99.42%</strong>.
        </p>
        <p>
          Para resolver esto, aplicamos la teoría de <strong>Meta-Labeling de Marcos López de Prado</strong>. En lugar de forzar al modelo principal a reajustar sus hiperparámetros (lo que causaría overfitting), creamos una segunda capa de Machine Learning que actúa como un guardián de riesgo (gatekeeper). Esta segunda capa analiza el contexto del mercado (fatiga de los equipos, diferencia de ELO, varianza de cuotas) y predice <em>la probabilidad de éxito de la decisión de inversión en sí misma</em>.
        </p>
        <p>
          Como se observa en los resultados empíricos, el Meta-Modelo **evitó 1,463 apuestas perdedoras** (el 64.6% del volumen total), elevando el ROI neto al **+6.91%** y reduciendo drásticamente el drawdown a solo el **27.77%**. Esto valida la estrategia como un activo financiero de bajo riesgo y crecimiento robusto en la Premier League.
        </p>
      </div>
    </div>
  );
};
