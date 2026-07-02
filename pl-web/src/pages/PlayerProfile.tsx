import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Shirt, Flag } from "lucide-react";
import { playersData, teamsData } from "@/data/mockData";
import { EntityLink } from "@/components/EntityLink";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

const PlayerProfile = () => {
  const { id } = useParams();
  const player = id ? playersData[id] : undefined;
  const team = player ? teamsData[player.teamId] : undefined;

  if (!player || !team) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p>Jugador no encontrado</p>
        <Link to="/dashboard" className="text-primary hover:underline text-sm mt-2 inline-block">Volver</Link>
      </div>
    );
  }

  const goalData = [
    { name: "Goles", value: player.stats.goals, color: "hsl(217 91% 60%)" },
    { name: "xG", value: player.stats.xG, color: "hsl(199 89% 48%)" },
    { name: "Asistencias", value: player.stats.assists, color: "hsl(142 71% 45%)" },
    { name: "xA", value: player.stats.xA, color: "hsl(252 60% 55%)" },
  ];

  const bettingStats = [
    { label: "Tiros a Puerta / 90", value: player.stats.shotsOnTargetPer90.toFixed(1), highlight: player.stats.shotsOnTargetPer90 > 1.5 },
    { label: "Faltas Cometidas / 90", value: player.stats.foulsCommittedPer90.toFixed(1), highlight: player.stats.foulsCommittedPer90 > 1.2 },
    { label: "Tarjetas Amarillas", value: player.stats.yellowCards, highlight: player.stats.yellowCards >= 6 },
    { label: "Tarjetas Rojas", value: player.stats.redCards, highlight: player.stats.redCards > 0 },
    { label: "Minutos Jugados", value: player.stats.minutesPlayed.toLocaleString(), highlight: false },
    { label: "Partidos Jugados", value: player.stats.appearances, highlight: false },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <Link to={`/team/${team.id}`} className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="h-4 w-4" /> Volver a {team.shortName}
      </Link>

      {/* Player Header */}
      <div className="glass-card overflow-hidden">
        <div className="h-24 relative" style={{ background: `linear-gradient(135deg, ${team.colors.primary}30, ${team.colors.secondary}20, hsl(220 40% 9%))` }}>
          <div className="absolute inset-0 bg-gradient-to-t from-card/90 to-transparent" />
        </div>
        <div className="px-6 pb-6 -mt-8 relative z-10">
          <div className="flex items-end gap-4">
            <div className="w-16 h-16 rounded-xl bg-secondary flex items-center justify-center text-2xl font-bold text-primary border border-border">
              {player.number}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-foreground">{player.name}</h1>
              <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><Shirt className="h-3.5 w-3.5" /> {player.position}</span>
                <span className="flex items-center gap-1"><Flag className="h-3.5 w-3.5" /> {player.nationality}</span>
                <EntityLink type="team" id={team.id}>
                  <span className="flex items-center gap-1">{team.logo} {team.name}</span>
                </EntityLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Goals & Assists Chart */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4">Goles y Asistencias vs Esperados</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={goalData} barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "hsl(215 20% 55%)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 55%)" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: "hsl(220 40% 9%)", border: "1px solid hsl(220 25% 18%)", borderRadius: "8px", fontSize: "12px", color: "hsl(213 31% 91%)" }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {goalData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Betting Stats */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4">Métricas de Apuestas</h2>
          <div className="space-y-3">
            {bettingStats.map((s, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                <span className="text-sm text-muted-foreground">
                  <span title={s.label === "Tiros a Puerta / 90" ? "Tiros a puerta promedio cada 90 minutos" : s.label === "Faltas Cometidas / 90" ? "Faltas cometidas promedio cada 90 minutos" : ""} className={s.label.includes("/") ? "cursor-help border-b border-dotted border-muted-foreground" : ""}>
                    {s.label}
                  </span>
                </span>
                <span className={`text-sm font-bold ${s.highlight ? "text-warning" : "text-foreground"}`}>
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

export default PlayerProfile;
