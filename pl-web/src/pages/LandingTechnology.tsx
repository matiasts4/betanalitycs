import { useState } from "react";
import { landingData } from "@/data/landingData";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Brain, Cpu, Sparkles, Code2, AlertCircle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export const LandingTechnology = () => {
  const { modelResults, overfitting } = landingData;
  const [activeTab, setActiveTab] = useState<"accuracy" | "overfitting">("accuracy");
  
  // States for accuracy tab
  const [selectedMarketId, setSelectedMarketId] = useState(modelResults.markets[0].id);
  const selectedMarket = modelResults.markets.find((m) => m.id === selectedMarketId) || modelResults.markets[0];
  const chartData = selectedMarket.models.map((model) => ({
    name: model.name,
    "Precisión (Accuracy)": model.accuracy,
    "Puntaje F1 (F1-Score)": model.f1,
  }));

  // States for overfitting tab
  const [overfittingMarket, setOverfittingMarket] = useState<"1x2" | "over25">("1x2");
  const overfittingData = overfitting[overfittingMarket];
  const overfittingChartData = overfittingData.map((item) => ({
    name: item.modelName.split(" (")[0], // short name
    "Train Accuracy": item.trainAcc,
    "Test Accuracy": item.testAcc,
    "Brecha (Gap)": item.gap,
  }));

  const modelDescriptions = [
    {
      name: "XGBoost",
      desc: "Algoritmo de ensamble de árboles impulsado por gradiente. Sobresale en la captura de relaciones complejas no lineales entre las variables estadísticas de los equipos y jugadores.",
      icon: Cpu,
    },
    {
      name: "HistGradientBoosting",
      desc: "Optimizado para grandes volúmenes de datos continuos. Proporciona predicciones muy robustas y rápidas estructurando agrupaciones de histogramas de forma iterativa.",
      icon: Sparkles,
    },
    {
      name: "Random Forest",
      desc: "Clasificador basado en múltiples árboles de decisión. Evita el sobreajuste promediando predicciones y destaca por su consistencia e interpretabilidad en mercados con alta volatilidad.",
      icon: Brain,
    },
    {
      name: "Logistic Regression",
      desc: "Modelo estadístico lineal de referencia. Utilizado para calibrar las probabilidades predictivas brutas y establecer una línea base sólida contra el consenso del mercado de apuestas.",
      icon: Code2,
    },
  ];

  return (
    <div className="py-12 px-6 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-8rem)]">
      <div className="text-center max-w-3xl mx-auto mb-8">
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-foreground mb-4">
          Inteligencia Artificial y Modelos
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Nuestras predicciones provienen de un proceso de modelado científico estricto. Entrenamos y validamos de forma cruzada de tipo temporal múltiples clasificadores de ML para encontrar ineficiencias de cuotas.
        </p>
      </div>

      {/* Subpage Tabs switcher */}
      <div className="flex border-b border-border/50 gap-4 mb-8 justify-center">
        <button
          onClick={() => setActiveTab("accuracy")}
          className={cn(
            "pb-3 text-sm font-semibold transition-all border-b-2 px-4 relative -bottom-[2px]",
            activeTab === "accuracy"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          Exactitud de Modelos (CV)
        </button>
        <button
          onClick={() => setActiveTab("overfitting")}
          className={cn(
            "pb-3 text-sm font-semibold transition-all border-b-2 px-4 relative -bottom-[2px]",
            activeTab === "overfitting"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          Diagnóstico de Ajuste (Overfitting)
        </button>
      </div>

      {activeTab === "accuracy" ? (
        <div className="grid lg:grid-cols-3 gap-8 items-start mb-16">
          {/* Left Column: Interactive Chart Controls & Selector */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-card p-6 bg-card/30 border border-border/40">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                Seleccionar Mercado
              </h2>
              <div className="flex flex-col gap-2">
                {modelResults.markets.map((market) => (
                  <button
                    key={market.id}
                    onClick={() => setSelectedMarketId(market.id)}
                    className={cn(
                      "text-left text-xs font-bold px-4 py-3 rounded-lg border transition-all duration-200",
                      selectedMarketId === market.id
                        ? "bg-primary/10 border-primary text-primary shadow-sm"
                        : "bg-transparent border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/20"
                    )}
                  >
                    {market.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="glass-card p-6 bg-card/10 border border-border/20 text-xs text-muted-foreground leading-relaxed">
              <p className="font-semibold text-foreground mb-2">Información del Evaluador:</p>
              {modelResults.source}
            </div>
          </div>

          {/* Right Column: Recharts Interactive Chart */}
          <div className="lg:col-span-2 glass-card p-6 md:p-8 bg-card/30 border border-border/40 flex flex-col h-[500px]">
            <div className="mb-6 flex justify-between items-start flex-wrap gap-4">
              <div>
                <h3 className="text-lg font-bold text-foreground">
                  Comparativa de Precisión: {selectedMarket.label}
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Valores de rendimiento en base al dataset histórico sanitizado.
                </p>
              </div>
              <span className="inline-flex items-center rounded-full bg-primary/10 border border-primary/30 px-3 py-1 text-xs font-semibold text-primary">
                Métrica Ganadora: {selectedMarket.models.find(m => m.isBest)?.name}
              </span>
            </div>

            <div className="flex-grow min-h-0 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[30, 90]}
                    tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--popover))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "hsl(var(--foreground))",
                    }}
                    cursor={{ fill: "rgba(255, 255, 255, 0.03)" }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    iconType="circle"
                    iconSize={8}
                    wrapperStyle={{ fontSize: "11px", paddingTop: "15px" }}
                  />
                  <Bar
                    dataKey="Precisión (Accuracy)"
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={45}
                  />
                  <Bar
                    dataKey="Puntaje F1 (F1-Score)"
                    fill="hsl(var(--info))"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={45}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-8 items-start mb-16">
          {/* Left Column: Overfitting Market Selector */}
          <div className="lg:col-span-1 space-y-6">
            <div className="glass-card p-6 bg-card/30 border border-border/40">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
                Mercado de Diagnóstico
              </h2>
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => setOverfittingMarket("1x2")}
                  className={cn(
                    "text-left text-xs font-bold px-4 py-3 rounded-lg border transition-all duration-200",
                    overfittingMarket === "1x2"
                      ? "bg-primary/10 border-primary text-primary shadow-sm"
                      : "bg-transparent border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/20"
                  )}
                >
                  1X2 (Match Winner - Multiclase)
                </button>
                <button
                  onClick={() => setOverfittingMarket("over25")}
                  className={cn(
                    "text-left text-xs font-bold px-4 py-3 rounded-lg border transition-all duration-200",
                    overfittingMarket === "over25"
                      ? "bg-primary/10 border-primary text-primary shadow-sm"
                      : "bg-transparent border-border/50 text-muted-foreground hover:text-foreground hover:bg-secondary/20"
                  )}
                >
                  Más de 2.5 Goles (Binario)
                </button>
              </div>
            </div>

            <div className="glass-card p-5 bg-card/10 border border-border/20 text-xs text-muted-foreground space-y-3 leading-relaxed">
              <div className="flex gap-2 items-start">
                <AlertCircle className="h-4 w-4 text-warning shrink-0 mt-0.5" />
                <p>
                  El fútbol tiene un <strong>ruido aleatorio extremadamente alto</strong>. Si un clasificador memoriza patrones históricos (overfitting), su Train Accuracy subirá al ~99%, pero fallará severamente al predecir partidos futuros (Test Accuracy inferior al azar).
                </p>
              </div>
              <div className="flex gap-2 items-start">
                <CheckCircle className="h-4 w-4 text-success shrink-0 mt-0.5" />
                <p>
                  Mediante optimización bayesiana en <strong>Optuna</strong>, mantenemos la brecha de ajuste en mínimos reales (<strong>0.82%</strong> en 1X2 y <strong>2.84%</strong> en Over 2.5), garantizando la máxima capacidad de generalización en producción.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Train vs Test Grouped Bar Chart */}
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-card p-6 md:p-8 bg-card/30 border border-border/40 flex flex-col h-[380px]">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-foreground">
                  Diagnóstico: Exactitud de Entrenamiento vs. Prueba
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Comparación del ajuste y brecha (gap) para descartar sobreajuste y subajuste.
                </p>
              </div>

              <div className="flex-grow min-h-0 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={overfittingChartData}
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
                      domain={[40, 100]}
                      tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                      axisLine={false}
                      tickLine={false}
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
                      verticalAlign="top"
                      height={32}
                      iconType="circle"
                      iconSize={8}
                      wrapperStyle={{ fontSize: "11px" }}
                    />
                    <Bar
                      dataKey="Train Accuracy"
                      fill="hsl(var(--primary))"
                      radius={[4, 4, 0, 0]}
                      maxBarSize={35}
                    />
                    <Bar
                      dataKey="Test Accuracy"
                      fill="hsl(var(--info))"
                      radius={[4, 4, 0, 0]}
                      maxBarSize={35}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Overfitting Table */}
            <div className="glass-card overflow-hidden border border-border/40">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="bg-secondary/40 border-b border-border/40 text-muted-foreground font-semibold">
                    <th className="p-3">Configuración del Modelo</th>
                    <th className="p-3 text-center">Train Acc</th>
                    <th className="p-3 text-center">Test Acc</th>
                    <th className="p-3 text-center">Brecha (Gap)</th>
                    <th className="p-3">Diagnóstico Científico</th>
                  </tr>
                </thead>
                <tbody>
                  {overfittingData.map((row, index) => (
                    <tr
                      key={index}
                      className={cn(
                        "border-b border-border/20 hover:bg-secondary/10 transition-colors",
                        row.diagnostic.includes("Óptimo") && "bg-success/5"
                      )}
                    >
                      <td className="p-3 font-semibold text-foreground">{row.modelName}</td>
                      <td className="p-3 text-center mono text-muted-foreground">{row.trainAcc.toFixed(2)}%</td>
                      <td className="p-3 text-center mono text-foreground">{row.testAcc.toFixed(2)}%</td>
                      <td className="p-3 text-center mono font-bold text-primary">{row.gap.toFixed(2)}%</td>
                      <td className="p-3 font-medium">
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase",
                            row.diagnostic.includes("Óptimo")
                              ? "bg-success/15 text-success"
                              : row.diagnostic.includes("Extremo")
                              ? "bg-destructive/15 text-destructive"
                              : "bg-warning/15 text-warning"
                          )}
                        >
                          {row.diagnostic}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Model Descriptions Grid */}
      <div className="border-t border-border/40 pt-16 mt-6">
        <h2 className="text-xl sm:text-2xl font-bold text-foreground mb-8 text-center tracking-tight">
          Nuestras Arquitecturas de Ensamble
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {modelDescriptions.map((m, i) => (
            <div key={i} className="glass-card p-6 bg-card/25 border border-border/40 hover:border-primary/20 transition-all duration-300 flex items-start gap-4">
              <div className="rounded-lg bg-primary/10 border border-primary/30 p-2.5 shrink-0 text-primary">
                <m.icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-foreground mb-1.5">{m.name}</h3>
                <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">{m.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
