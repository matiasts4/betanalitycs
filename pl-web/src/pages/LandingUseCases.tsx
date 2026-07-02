import { Link } from "react-router-dom";
import {
  TrendingUp,
  Target,
  Shield,
  Zap,
  Brain,
  Database,
  Calculator,
  ArrowRight,
} from "lucide-react";

export const LandingUseCases = () => {
  const polymarketBenefits = [
    {
      icon: TrendingUp,
      title: "ROI +12.8%",
      description: "Superando consistentemente el benchmark del mercado",
    },
    {
      icon: Target,
      title: "67.3% de acierto",
      description: "Tasa de acierto calibrada sobre 1,247 predicciones",
    },
    {
      icon: Shield,
      title: "Riesgo controlado",
      description:
        "Gestión de bankroll con Kelly fraccional, max drawdown -8.4%",
    },
    {
      icon: Zap,
      title: "Decisión en tiempo real",
      description: "Probabilidades actualizadas al instante para cada partido",
    },
  ];

  const steps = [
    {
      icon: Brain,
      title: "Nuestro modelo analiza",
      description:
        "27 variables de rendimiento por partido: ELO, xG, goles, tiros, forma reciente",
    },
    {
      icon: Calculator,
      title: "Calculamos probabilidad",
      description:
        "Comparamos la probabilidad del modelo vs la cuota del mercado para detectar valor",
    },
    {
      icon: TrendingUp,
      title: "Tú decides",
      description:
        "Usa la señal como herramienta complementaria para tomar decisiones informadas en Polymarket u otros mercados",
    },
  ];

  const gallery = [
    {
      src: "/poly/probability_arsenalvscity.png",
      caption: "Probabilidad calibrada: Arsenal vs Manchester City",
    },
    {
      src: "/poly/fotoporfatdajuagdores.png",
      caption: "Análisis de jugadores de Premier League",
    },
    {
      src: "/poly/fotoporfatdajuagdores2.png.png",
      caption: "Estadísticas de rendimiento individual",
    },
    {
      src: "/poly/polygrafico.png",
      caption: "Gráfica de mercado de predicción",
    },
  ];

  const realBenefits = [
    {
      icon: Database,
      title: "3,420 partidos analizados",
      description: "Dataset sanitizado con datos reales de la Premier League",
    },
    {
      icon: Brain,
      title: "4 modelos ensemble",
      description:
        "Logistic Regression, Random Forest, HistGradientBoosting y XGBoost",
    },
    {
      icon: Target,
      title: "8 mercados cubiertos",
      description:
        "1X2, Over/Under 2.5, BTTS, Doble Oportunidad, Valla Invicta",
    },
    {
      icon: Shield,
      title: "Pipeline anti-fugas",
      description:
        "Eliminamos cuotas del bookmaker y goles previos para evitar data leakage",
    },
    {
      icon: Calculator,
      title: "Kelly fraccional",
      description:
        "Recomendación de stake matemática basada en Expected Value",
    },
    {
      icon: TrendingUp,
      title: "+$3,842 beneficio",
      description: "Retorno neto probado sobre $1,000 de banco inicial",
    },
  ];

  return (
    <div className="py-12 px-6 max-w-7xl mx-auto animate-fade-in">
      {/* Hero Section */}
      <section className="text-center mb-20 mt-6">
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted px-4 py-1.5 text-xs font-medium text-muted-foreground mb-6">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          BetAnalytics · Casos de Uso
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tighter mb-4 text-foreground" style={{ letterSpacing: "-0.04em" }}>
          Casos de <span className="text-primary">Uso</span>
        </h1>
        <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          De la cancha al mercado: una herramienta para tomar mejores decisiones
        </p>
      </section>

      {/* Polymarket Section */}
      <section className="mb-24">
        <div className="flex flex-col items-center text-center mb-10">
          <img
            src="/poly/logopoly.png"
            alt="Polymarket"
            className="h-[60px] w-auto object-contain mb-6"
          />
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-4 tracking-tight">
            Predicciones para Polymarket
          </h2>
          <p className="text-sm sm:text-base text-muted-foreground max-w-3xl leading-relaxed">
            Polymarket es un mercado de predicción descentralizado donde los
            usuarios apuestan sobre eventos del mundo real. Nuestro motor de IA
            proporciona probabilidades calibradas que pueden usarse como señal
            para tomar decisiones informadas en estos mercados. El ROI habla por
            sí solo:{" "}
            <span className="text-primary font-semibold">+12.8%</span> promedio
            frente al{" "}
            <span className="text-foreground font-semibold">
              +3.2%
            </span>{" "}
            del benchmark del mercado.
          </p>
        </div>

        {/* Polymarket chart */}
        <div className="glass-card p-2 bg-black/40 border border-border/40 rounded-xl max-w-md mx-auto mb-12 h-[260px] flex items-center justify-center overflow-hidden">
          <img
            src="/poly/polygrafico.png"
            alt="Gráfica de Polymarket"
            className="max-w-full max-h-full object-contain rounded-lg transition-transform duration-300 hover:scale-102"
          />
        </div>

        {/* Benefits grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {polymarketBenefits.map((b, i) => (
            <div
              key={i}
              className="glass-card p-6 bg-card/20 border border-border/40 hover:border-primary/20 transition-all duration-300 group"
            >
              <div className="rounded-md bg-primary/10 p-2.5 w-fit mb-4 group-hover:bg-primary/20 transition-colors">
                <b.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-semibold text-foreground mb-2">
                {b.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {b.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Cómo funciona — 3 step flow */}
      <section className="mb-24">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">
            Cómo funciona
          </h2>
          <p className="text-sm text-muted-foreground max-w-xl mx-auto">
            Del dato crudo a la decisión informada, en tres pasos.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-4 relative">
          {steps.map((s, i) => (
            <div key={i} className="relative">
              <div className="glass-card p-7 bg-card/20 border border-border/40 hover:border-primary/20 transition-all duration-300 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <div className="rounded-md bg-primary/10 p-2.5 group-hover:bg-primary/20 transition-colors">
                    <s.icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    Paso {i + 1}
                  </span>
                </div>
                <h3 className="text-base font-semibold text-foreground mb-2">
                  {s.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {s.description}
                </p>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-2 z-10 text-muted-foreground/40">
                  <ArrowRight className="h-5 w-5" />
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Gallery 2x2 */}
      <section className="mb-24">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">
            Visualizaciones
          </h2>
          <p className="text-sm text-muted-foreground max-w-xl mx-auto">
            Gráficas y análisis generados por el motor de BetAnalytics.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
          {gallery.map((img, i) => (
            <div
              key={i}
              className="glass-card bg-card/40 border border-border/40 hover:border-primary/20 transition-all duration-300 overflow-hidden flex flex-col justify-between"
              style={{ borderRadius: "16px" }}
            >
              <div className="w-full bg-black/40 flex items-center justify-center p-2 h-[260px] overflow-hidden">
                <img
                  src={img.src}
                  alt={img.caption}
                  className="max-w-full max-h-full object-contain rounded-lg transition-transform duration-300 hover:scale-105"
                  loading="lazy"
                />
              </div>
              <p className="text-xs sm:text-sm font-medium text-muted-foreground text-center px-4 py-3.5 border-t border-border/30 bg-muted/20">
                {img.caption}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Real benefits grid */}
      <section className="mb-24">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">
            Beneficios reales
          </h2>
          <p className="text-sm text-muted-foreground max-w-xl mx-auto">
            Lo que BetAnalytics aporta, respaldado por datos y pruebas reales.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {realBenefits.map((b, i) => (
            <div
              key={i}
              className="glass-card p-7 bg-card/20 border border-border/40 hover:border-primary/20 transition-all duration-300 group"
            >
              <div className="rounded-md bg-primary/10 p-2.5 w-fit mb-5 group-hover:bg-primary/20 transition-colors">
                <b.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-semibold text-foreground mb-2">
                {b.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {b.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer + CTA */}
      <section className="mb-12">
        <div className="glass-card p-10 sm:p-12 relative overflow-hidden bg-gradient-to-br from-primary/5 to-card/5 border border-border/40 text-center">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[200px] rounded-full bg-primary/5 blur-[80px] pointer-events-none" />
          <div className="relative z-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-4 tracking-tight">
              Empieza a tomar mejores decisiones
            </h2>
            <p className="text-sm text-muted-foreground max-w-md mx-auto mb-8">
              Accede al panel interactivo y explora las predicciones en tiempo
              real.
            </p>
            <Link
              to="/dashboard"
              className="group inline-flex items-center gap-2 rounded-md bg-primary px-10 py-3.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/15"
            >
              Abrir Panel
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <p className="text-[11px] sm:text-xs text-muted-foreground mt-8 max-w-xl mx-auto leading-relaxed">
              ⚠️ Esta herramienta es para fines educativos y de investigación.
              No constituye consejo financiero. Apueste responsablemente.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingUseCases;