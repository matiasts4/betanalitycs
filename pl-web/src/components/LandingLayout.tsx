import { Outlet, Link, useLocation } from "react-router-dom";
import { Bot } from "lucide-react";
import { landingData } from "@/data/landingData";
import { cn } from "@/lib/utils";

export const LandingLayout = () => {
  const { brand, footer } = landingData;
  const location = useLocation();

  const navItems = [
    { label: "Inicio", path: "/" },
    { label: "Modelos e IA", path: "/technology" },
    { label: "Rendimiento", path: "/backtesting" },
    { label: "Pipeline de Datos", path: "/pipeline" },
    { label: "Casos de Uso", path: "/use-cases" },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden flex flex-col">
      {/* Immersive radial glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] rounded-full bg-primary/5 blur-[120px] pointer-events-none z-0" />
      
      {/* Sticky Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 hover:opacity-90 transition-opacity">
            <Bot className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold tracking-tight text-foreground">{brand.name}</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-1.5 bg-secondary/30 p-1 rounded-full border border-border/40">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "text-xs font-semibold px-4 py-1.5 rounded-full transition-all duration-200",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-sm shadow-primary/20"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>

          <Link
            to="/dashboard"
            className="rounded-md bg-primary/10 border border-primary/30 px-5 py-2 text-xs font-bold text-primary hover:bg-primary hover:text-primary-foreground transition-all duration-200"
          >
            {brand.ctaPrimary}
          </Link>
        </div>
      </nav>

      {/* Main presentation content */}
      <main className="flex-grow pt-16 relative z-10">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-background/90 py-8 px-6 relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold text-foreground">{brand.name}</span>
          </div>
          <p className="text-xs text-muted-foreground text-center sm:text-right">
            {footer.tagline}
          </p>
        </div>
      </footer>
    </div>
  );
};
