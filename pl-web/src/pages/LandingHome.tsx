import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { landingData } from "@/data/landingData";

export const LandingHome = () => {
  const { brand, hero, features, cta } = landingData;

  return (
    <div className="py-12 px-6 max-w-7xl mx-auto flex flex-col items-center justify-center min-h-[calc(100vh-8rem)]">
      {/* Hero Section */}
      <div className="text-center max-w-4xl relative z-10 my-auto">
        <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted px-4 py-1.5 text-xs font-medium text-muted-foreground mb-8 animate-fade-in">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          {hero.badge}
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black tracking-tighter mb-6 animate-fade-in text-foreground" style={{ animationDelay: "100ms", letterSpacing: "-0.04em" }}>
          {hero.headline[0]}
          <br />
          <span className="text-primary">{hero.headline[1]}</span>
        </h1>

        <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto mb-10 animate-fade-in leading-relaxed" style={{ animationDelay: "200ms" }}>
          {hero.subheadline}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-fade-in mb-16" style={{ animationDelay: "300ms" }}>
          <Link
            to="/dashboard"
            className="group flex items-center gap-2 rounded-md bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/10"
          >
            {brand.ctaPrimary}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
          <Link
            to="/technology"
            className="flex items-center gap-2 rounded-md border border-border px-8 py-3 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            {brand.ctaSecondary}
          </Link>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-slide-up" style={{ animationDelay: "400ms" }}>
          {hero.stats.map((s, i) => (
            <div key={i} className="glass-card p-5 text-center bg-card/40 backdrop-blur-sm border border-border/40 hover:border-primary/20 transition-all duration-300">
              <s.icon className="h-4 w-4 text-primary mx-auto mb-2" />
              <p className="text-2xl font-black text-foreground mono tracking-tight">{s.value}</p>
              <p className="text-[10px] text-muted-foreground mt-1 uppercase tracking-wider font-semibold">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Highlights Grid */}
      <div className="mt-28 w-full border-t border-border/40 pt-16">
        <div className="text-center mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">Plataforma de Analítica Premium</h2>
          <p className="text-sm text-muted-foreground max-w-xl mx-auto">
            Todas las herramientas necesarias para tomar decisiones basadas en datos e impulsadas por Machine Learning.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <div key={i} className="glass-card p-7 hover:border-primary/20 transition-colors group bg-card/20 border border-border/40">
              <div className="rounded-md bg-primary/10 p-2.5 w-fit mb-5 group-hover:bg-primary/20 transition-colors">
                <f.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-semibold text-foreground mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick CTA Bottom */}
      <div className="my-20 w-full text-center glass-card p-12 relative overflow-hidden bg-gradient-to-br from-primary/5 to-card/5 border border-border/40">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[200px] rounded-full bg-primary/5 blur-[80px] pointer-events-none" />
        <div className="relative z-10">
          <h2 className="text-2xl font-bold text-foreground mb-3 tracking-tight">{cta.title}</h2>
          <p className="text-sm text-muted-foreground mb-8 max-w-md mx-auto">{cta.subtitle}</p>
          <Link
            to="/dashboard"
            className="group inline-flex items-center gap-2 rounded-md bg-primary px-10 py-3.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/15"
          >
            {cta.button}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </div>
    </div>
  );
};
