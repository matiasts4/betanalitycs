import { useAPIPerformance } from "@/lib/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const Performance = () => {
  const { data: perf, isLoading } = useAPIPerformance();

  if (isLoading || !perf) {
    return (
      <div className="flex items-center justify-center p-24">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  const { performanceSummary, profitChartData, historyData } = perf;
  const { totalWins, totalLosses, totalProfit } = {
    totalWins: performanceSummary.wins,
    totalLosses: performanceSummary.losses,
    totalProfit: performanceSummary.totalProfit
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-1">Rendimiento</h1>
        <p className="text-sm text-muted-foreground">Historial de predicciones y ROI del bot</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-4 text-center gradient-blue">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Victorias</p>
          <p className="text-2xl font-bold text-success">{totalWins}</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Derrotas</p>
          <p className="text-2xl font-bold text-destructive">{totalLosses}</p>
        </div>
        <div className="glass-card p-4 text-center gradient-blue">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Beneficio Neto</p>
          <p className={cn("text-2xl font-bold", totalProfit >= 0 ? "text-success" : "text-destructive")}>
            {totalProfit >= 0 ? "+" : ""}£{totalProfit.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="glass-card p-6">
        <h2 className="text-sm font-semibold text-foreground mb-4">Beneficio Acumulado (£)</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={profitChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ backgroundColor: "hsl(var(--popover))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "12px", color: "hsl(var(--foreground))" }} />
              <Line type="monotone" dataKey="profit" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 3, fill: "hsl(var(--primary))" }} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-semibold text-foreground">Predicciones Recientes</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground uppercase tracking-wider">
                <th className="text-left p-3 font-medium">Fecha</th>
                <th className="text-left p-3 font-medium">Partido</th>
                <th className="text-left p-3 font-medium">Mercado / Pick</th>
                <th className="text-right p-3 font-medium">Cuota</th>
                <th className="text-center p-3 font-medium">Resultado</th>
                <th className="text-right p-3 font-medium">B/P</th>
              </tr>
            </thead>
            <tbody>
              {historyData.map((h, idx) => (
                <tr key={idx} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                  <td className="p-3 text-muted-foreground whitespace-nowrap">{h.date}</td>
                  <td className="p-3 text-foreground font-medium whitespace-nowrap">{h.match}</td>
                  <td className="p-3 text-muted-foreground font-medium">{h.prediction}</td>
                  <td className="p-3 text-right font-semibold text-foreground">{h.odds.toFixed(2)}</td>
                  <td className="p-3 text-center">
                    <span className={cn(
                      "inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold uppercase",
                      h.result === "Won" ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"
                    )}>
                      {h.result}
                    </span>
                  </td>
                  <td className={cn("p-3 text-right font-bold", h.profit >= 0 ? "text-success" : "text-destructive")}>
                    {h.profit >= 0 ? "+" : ""}£{h.profit.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Performance;
