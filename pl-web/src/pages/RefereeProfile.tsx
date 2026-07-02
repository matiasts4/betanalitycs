import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Scale } from "lucide-react";
import { refereesData } from "@/data/mockData";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const RefereeProfile = () => {
  const { id } = useParams();
  const referee = id ? refereesData[id] : undefined;

  if (!referee) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p>Árbitro no encontrado</p>
        <Link to="/dashboard" className="text-primary hover:underline text-sm mt-2 inline-block">Volver</Link>
      </div>
    );
  }

  const total = referee.results.homeWins + referee.results.awayWins + referee.results.draws;
  const pieData = [
    { name: "Victorias Locales", value: referee.results.homeWins, color: "hsl(217 91% 60%)" },
    { name: "Victorias Visitantes", value: referee.results.awayWins, color: "hsl(199 89% 48%)" },
    { name: "Empates", value: referee.results.draws, color: "hsl(215 20% 50%)" },
  ];

  const disciplineStats = [
    { label: "Tarjetas Amarillas Medias / Partido", value: referee.discipline.avgYellowPerGame.toFixed(1), warn: referee.discipline.avgYellowPerGame > 4 },
    { label: "Total Tarjetas Amarillas", value: referee.discipline.totalYellows, warn: false },
    { label: "Total Tarjetas Rojas", value: referee.discipline.totalReds, warn: referee.discipline.totalReds >= 3 },
    { label: "Faltas Pitadas / Entrada", value: referee.discipline.foulsPerTackle.toFixed(2), warn: referee.discipline.foulsPerTackle > 0.30 },
    { label: "Partidos Arbitrados", value: referee.matchesOfficiated, warn: false },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <Link to="/dashboard" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="h-4 w-4" /> Volver
      </Link>

      {/* Header */}
      <div className="glass-card p-6 gradient-blue">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-xl bg-secondary flex items-center justify-center border border-border">
            <Scale className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">{referee.name}</h1>
            <p className="text-sm text-muted-foreground mt-1">{referee.matchesOfficiated} partidos de la Premier League esta temporada</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Results Pie Chart */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4">Distribución de Resultados de Partidos</h2>
          <div className="h-64 relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", fontSize: "12px", color: "hsl(213 31% 91%)" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2">
            {pieData.map((d, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-muted-foreground">{d.name} ({((d.value / total) * 100).toFixed(0)}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Disciplinary Stats */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4">Historial Disciplinario</h2>
          <div className="space-y-4">
            {disciplineStats.map((s, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                <span className="text-sm text-muted-foreground">
                  <span
                    title={s.label.includes("Faltas") ? "Proporción de faltas pitadas por entrada realizada" : ""}
                    className={s.label.includes("Faltas") ? "cursor-help border-b border-dotted border-muted-foreground" : ""}
                  >
                    {s.label}
                  </span>
                </span>
                <span className={`text-lg font-bold ${s.warn ? "text-warning" : "text-foreground"}`}>
                  {s.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RefereeProfile;
