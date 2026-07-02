import { landingData } from "@/data/landingData";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Shield, Brain, Layers, Cpu, CheckCircle } from "lucide-react";

export const LandingPipeline = () => {
  const { pipeline } = landingData;

  const layers = [
    {
      title: "Capa 1: Predicción Primaria (Recall)",
      subtitle: "Modelos Predictivos Base",
      desc: "Clasificadores optimizados por Optuna (XGBoost, Regresión Logística y MLP PyTorch) entrenados dinámicamente con validación cruzada temporal para estimar probabilidades brutas de eventos deportivos.",
      icon: Cpu,
      color: "border-primary/30 bg-primary/5 text-primary",
    },
    {
      title: "Capa 2: Calibración Post-Hoc (EV exacto)",
      subtitle: "Calibración Isotónica y Sigmoide",
      desc: "Alinea las estimaciones de probabilidad brutas con las frecuencias reales observadas en el set de calibración de datos out-of-fold. Indispensable para contrarrestar el overround comercial de la casa.",
      icon: Layers,
      color: "border-info/30 bg-info/5 text-info",
    },
    {
      title: "Capa 3: Motor de Meta-Decisión (Precision)",
      subtitle: "Meta-Labeling y Filtro de EV Dinámico",
      desc: "Modelo Random Forest que actúa como gatekeeper filtrando falsos positivos. Decide si vale la pena invertir basándose en variables contextuales de fatiga (descanso) y disparidad de ELO.",
      icon: Shield,
      color: "border-success/30 bg-success/5 text-success",
    },
  ];

  return (
    <div className="py-12 px-6 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-8rem)]">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-foreground mb-4">
          Pipeline de Datos y Arquitectura de 3 Capas
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Para lograr rentabilidad consistente frente a las cuotas de Bet365, BetAnalytics utiliza una arquitectura de control cuantitativo modular de tres capas, aislando los descriptores tácticos del ruido mercantil.
        </p>
      </div>

      {/* Three-Layer Architecture visual blocks */}
      <h2 className="text-xl font-bold text-foreground mb-6 tracking-tight text-center">
        Arquitectura Predictiva Cuantitativa
      </h2>
      <div className="grid md:grid-cols-3 gap-6 mb-16">
        {layers.map((layer, i) => {
          const Icon = layer.icon;
          return (
            <div key={i} className={`glass-card p-6 border rounded-xl flex flex-col justify-between hover:scale-[1.01] transition-transform duration-300 ${layer.color}`}>
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                    Capa {i + 1}
                  </span>
                  <div className="p-2.5 rounded-lg border border-border/40 bg-card/60">
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
                <div>
                  <h3 className="text-base font-bold text-foreground mb-1">{layer.title}</h3>
                  <p className="text-xs font-semibold text-primary mb-3 uppercase tracking-wider">{layer.subtitle}</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">{layer.desc}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Importance & Preprocessing Grid */}
      <div className="grid lg:grid-cols-5 gap-8 items-start mb-16">
        {/* Left Column: Data Sanitization V9 & Resampling */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-foreground tracking-tight mb-2">
            Sanitización del Dataset
          </h2>
          <div className="space-y-4 text-xs sm:text-sm text-muted-foreground leading-relaxed">
            <div className="flex gap-3 items-start">
              <CheckCircle className="h-4 w-4 text-primary mt-1 shrink-0" />
              <p>
                <strong>Preprocesamiento y Outliers:</strong> Se aplicó winsorización y KNNImputer en las variables de Expected Goals para tratar nulos y evitar distorsiones por goleadas históricas atípicas.
              </p>
            </div>
            <div className="flex gap-3 items-start">
              <CheckCircle className="h-4 w-4 text-primary mt-1 shrink-0" />
              <p>
                <strong>Remuestreo Tomek Links:</strong> Para los mercados de 1X2 (concentración de empates) y Valla Invicta Local se limpiaron las fronteras de decisión difusas en el set de entrenamiento, reduciendo falsos positivos.
              </p>
            </div>
            <div className="flex gap-3 items-start">
              <CheckCircle className="h-4 w-4 text-primary mt-1 shrink-0" />
              <p>
                <strong>Prevención estricta de Leakage:</strong> Validación cruzada temporal (TimeSeriesSplit) para garantizar que el modelo no entrene con datos del futuro, y separación de calibración out-of-fold.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Recharts Horizontal Bar Chart (Feature Importance) */}
        <div className="lg:col-span-3 glass-card p-6 md:p-8 bg-card/30 border border-border/40 flex flex-col h-[400px]">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-foreground">
              Importancia de las Variables en el Meta-Modelo
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Ponderación relativa (%) de las características predictivas en la toma de decisión final.
            </p>
          </div>

          <div className="flex-grow min-h-0 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={pipeline.featureImportance}
                layout="vertical"
                margin={{ top: 10, right: 10, left: 30, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                <XAxis
                  type="number"
                  domain={[0, 35]}
                  tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(val) => `${val}%`}
                />
                <YAxis
                  type="category"
                  dataKey="feature"
                  tick={{ fontSize: 11, fill: "hsl(var(--foreground))", fontWeight: 500 }}
                  axisLine={false}
                  tickLine={false}
                  width={140}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "hsl(var(--foreground))",
                  }}
                  formatter={(value) => [`${value}%`, "Importancia Relativa"]}
                />
                <Bar
                  dataKey="importance"
                  fill="hsl(var(--primary))"
                  radius={[0, 4, 4, 0]}
                  maxBarSize={22}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Honest Academic Justification & Limitations */}
      <div className="border-t border-border/40 pt-12 mt-6">
        <h2 className="text-xl sm:text-2xl font-bold text-foreground mb-6 tracking-tight text-center">
          Justificación Metodológica para Defensa de Tesis
        </h2>
        <div className="grid md:grid-cols-2 gap-8 text-xs sm:text-sm text-muted-foreground leading-relaxed">
          <div className="space-y-3">
            <h3 className="text-base font-bold text-foreground">
              A. El Sesgo del Solver Poisson Bivariado
            </h3>
            <p>
              En la simulación histórica ampliada a 8 mercados, se observaron retornos teóricos masivos (llegando a cifras multimillonarias bajo el criterio Kelly en mercados como BTTS y Home Clean Sheet). Es imperativo aclarar al jurado evaluador que <strong>estos números están inflados por el modelo de cuotas sintéticas de goles</strong>.
            </p>
            <p>
              Debido a la ausencia de bases de datos públicas de cuotas históricas de BTTS y Vallas Invictas en Bet365, estas se simularon resolviendo numéricamente una distribución Poisson Bivariada Independiente. Este modelo asume independencia matemática entre los goles del local y visitante. En la realidad táctica, los goles están correlacionados (un gol altera el comportamiento del rival).
            </p>
            <p>
              Esta asunción subestima sistemáticamente la probabilidad de que ambos anoten, lo que deriva en <strong>cuotas sintéticas promedio infladas</strong> (promedio calculado de 2.55 en BTTS Yes, cuando en el mercado real promedian 1.70-2.00). Al tener cuotas infladas de partida, el ROI simulado resulta artificialmente alto.
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="text-base font-bold text-foreground">
              B. Límites de Liquidez y Restricciones Reales (Gubbing)
            </h3>
            <p>
              Bajo la estrategia Kelly, el crecimiento geométrico exponencial asume que el mercado puede absorber stakes infinitos. En la realidad de la inversión deportiva cuantitativa, existen dos fuertes límites operativos:
            </p>
            <ol className="list-decimal pl-4 space-y-2">
              <li>
                <strong>Capping de Stakes:</strong> Las casas de apuestas imponen límites máximos de aceptación de stake (de $2,000 a $5,000 USD por partido en ligas secundarias o mercados colaterales), lo que aplana la curva logarítmica a un crecimiento lineal en producción.
              </li>
              <li>
                <strong>Limitación de Cuentas (Limitation/Gubbing):</strong> Los operadores comerciales utilizan algoritmos de riesgo que identifican cuentas con valor esperado positivo sistemático, restringiendo de forma casi inmediata su stake máximo permitido a centavos de dólar o suspendiendo el servicio.
              </li>
            </ol>
            <p>
              <strong>Conclusión Académica:</strong> Por lo tanto, el ROI real neto estabilizado en producción real se espera que descienda a un rango de <strong>3% al 8%</strong>. Esto sigue representando un rendimiento excepcional de inversión cuantitativa ajustada por riesgo.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
