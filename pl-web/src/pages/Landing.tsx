import { Link } from "react-router-dom";
import { Bot, ArrowRight, ChevronRight } from "lucide-react";
import { landingData } from "@/data/landingData";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs";

const Landing = () => {
  const { brand, hero, features, modelResults, decisionFlow, markets, cta, footer } = landingData;

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Bot className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold text-foreground">{brand.name}</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Características</a>
            <a href="#models" className="hover:text-foreground transition-colors">Modelos</a>
            <a href="#flow" className="hover:text-foreground transition-colors">Proceso</a>
            <a href="#markets" className="hover:text-foreground transition-colors">Mercados</a>
          </div>
          <Link
            to="/dashboard"
            className="rounded-md bg-primary px-5 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            {brand.ctaPrimary}
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-6">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[500px] rounded-full bg-primary/5 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[400px] rounded-full bg-info/5 blur-[100px] pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
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

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-fade-in" style={{ animationDelay: "300ms" }}>
            <Link
              to="/dashboard"
              className="group flex items-center gap-2 rounded-md bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all"
            >
              {brand.ctaPrimary}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <a
              href="#features"
              className="flex items-center gap-2 rounded-md border border-border px-8 py-3 text-sm font-medium text-foreground hover:bg-muted transition-colors"
            >
              {brand.ctaSecondary}
            </a>
          </div>
        </div>

        {/* Stats bar */}
        <div className="max-w-3xl mx-auto mt-20 grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" style={{ animationDelay: "400ms" }}>
          {hero.stats.map((s, i) => (
            <div key={i} className="glass-card p-5 text-center">
              <s.icon className="h-4 w-4 text-primary mx-auto mb-2" />
              <p className="text-xl font-bold text-foreground mono">{s.value}</p>
              <p className="text-[11px] text-muted-foreground mt-1 uppercase tracking-wide">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">Plataforma de Analítica Premium</h2>
            <p className="text-sm text-muted-foreground max-w-xl mx-auto">
              Todas las herramientas que necesitas para tomar decisiones de apuestas basadas en datos, impulsadas por modelos avanzados de aprendizaje automático.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((f, i) => (
              <div key={i} className="glass-card p-7 hover:border-primary/20 transition-colors group">
                <div className="rounded-md bg-primary/10 p-2.5 w-fit mb-5 group-hover:bg-primary/20 transition-colors">
                  <f.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="text-base font-semibold text-foreground mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Model Results */}
      <section id="models" className="py-24 px-6 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">{modelResults.title}</h2>
            <p className="text-sm text-muted-foreground max-w-2xl mx-auto">{modelResults.subtitle}</p>
          </div>

          <div className="glass-card p-6 md:p-8">
            <Tabs defaultValue={modelResults.markets[0].id} className="w-full">
              <TabsList className="w-full flex flex-wrap h-auto gap-2 bg-transparent p-0 mb-6">
                {modelResults.markets.map((market) => (
                  <TabsTrigger
                    key={market.id}
                    value={market.id}
                    className="flex-1 min-w-[120px] rounded-lg border border-border bg-muted/50 px-3 py-2 text-xs data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:border-primary"
                  >
                    {market.shortLabel}
                  </TabsTrigger>
                ))}
              </TabsList>

              {modelResults.markets.map((market) => (
                <TabsContent key={market.id} value={market.id} className="animate-fade-in">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-foreground">{market.label}</h3>
                    <p className="text-xs text-muted-foreground">Comparativa de Accuracy, ROC-AUC y F1 por modelo.</p>
                  </div>
                  <div className="overflow-x-auto rounded-lg border border-border">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent">
                          <TableHead className="text-muted-foreground">Modelo</TableHead>
                          <TableHead className="text-right text-muted-foreground">Accuracy</TableHead>
                          <TableHead className="text-right text-muted-foreground">ROC-AUC</TableHead>
                          <TableHead className="text-right text-muted-foreground">F1</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {market.models.map((model, idx) => (
                          <TableRow
                            key={idx}
                            className={cn(
                              model.isBest && "bg-success/10 hover:bg-success/15"
                            )}
                          >
                            <TableCell className="font-medium">
                              <div className="flex items-center gap-2">
                                {model.isBest && (
                                  <span className="inline-flex items-center rounded-full bg-success/20 px-2 py-0.5 text-[10px] font-bold text-success">
                                    BEST
                                  </span>
                                )}
                                {model.name}
                              </div>
                            </TableCell>
                            <TableCell className={cn("text-right mono", model.isBest ? "text-success font-bold" : "text-foreground")}>
                              {model.accuracy.toFixed(2)}%
                            </TableCell>
                            <TableCell className="text-right mono text-muted-foreground">
                              {model.rocAuc ? `${model.rocAuc.toFixed(2)}%` : "N/A"}
                            </TableCell>
                            <TableCell className="text-right mono text-muted-foreground">
                              {model.f1.toFixed(2)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </TabsContent>
              ))}
            </Tabs>

            <p className="mt-6 text-[11px] text-muted-foreground leading-relaxed">
              {modelResults.source}
            </p>
          </div>
        </div>
      </section>

      {/* Decision Flow */}
      <section id="flow" className="py-24 px-6 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">{decisionFlow.title}</h2>
            <p className="text-sm text-muted-foreground max-w-2xl mx-auto">{decisionFlow.subtitle}</p>
          </div>

          <div className="relative">
            {/* Connector line */}
            <div className="absolute left-12 top-12 bottom-12 w-px bg-gradient-to-b from-primary/50 via-primary/20 to-transparent hidden md:block" />

            <div className="space-y-6">
              {decisionFlow.steps.map((step, i) => (
                <div
                  key={i}
                  className="relative flex flex-col md:flex-row gap-4 md:gap-8 animate-fade-in"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <div className="flex items-center md:justify-center gap-4 md:w-24 shrink-0">
                    <div className="relative z-10 rounded-xl bg-background border border-primary/30 overflow-hidden">
                      <div className="bg-primary/10 p-3">
                        <step.icon className="h-6 w-6 text-primary" />
                      </div>
                    </div>
                    <span className="md:hidden text-xs font-bold text-muted-foreground">Paso {i + 1}</span>
                  </div>
                  <div className="glass-card p-6 flex-1 hover:border-primary/20 transition-colors">
                    <h3 className="text-base font-semibold text-foreground mb-2">
                      {step.title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Markets Section */}
      <section id="markets" className="py-24 px-6 border-t border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3 tracking-tight">{markets.title}</h2>
            <p className="text-sm text-muted-foreground">{markets.subtitle}</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {markets.items.map((market, i) => (
              <div key={i} className="glass-card p-4 flex items-center gap-3 group hover:border-primary/20 transition-colors">
                <ChevronRight className="h-4 w-4 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="text-sm font-medium text-foreground">{market}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center glass-card p-12 relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[200px] rounded-full bg-primary/10 blur-[80px] pointer-events-none" />
          <div className="relative z-10">
            <h2 className="text-2xl font-bold text-foreground mb-3 tracking-tight">{cta.title}</h2>
            <p className="text-sm text-muted-foreground mb-8">{cta.subtitle}</p>
            <Link
              to="/dashboard"
              className="group inline-flex items-center gap-2 rounded-md bg-primary px-10 py-3.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-all"
            >
              {cta.button}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold text-foreground">{brand.name}</span>
          </div>
          <p className="text-xs text-muted-foreground text-center sm:text-right">{footer.tagline}</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
