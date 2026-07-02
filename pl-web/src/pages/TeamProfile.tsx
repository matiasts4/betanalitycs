import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Trophy, Shield, Target, ChevronDown, Calendar, Crosshair, ShieldCheck, TrendingUp, TrendingDown, Zap, BarChart2 } from "lucide-react";
import { useAPITeams } from "@/lib/api";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell
} from "recharts";

const TEAM_COLORS: Record<string, { primary: string; secondary: string }> = {
  "Arsenal":                     { primary: "#EF0107", secondary: "#9C824A" },
  "Chelsea":                     { primary: "#034694", secondary: "#DBA111" },
  "Liverpool":                   { primary: "#C8102E", secondary: "#F6EB61" },
  "Manchester City":             { primary: "#6CABDD", secondary: "#1C2C5B" },
  "Manchester United":           { primary: "#DA291C", secondary: "#FBE122" },
  "Tottenham Hotspur":           { primary: "#132257", secondary: "#FFFFFF" },
  "Newcastle United":            { primary: "#241F20", secondary: "#41B6E6" },
  "Brighton":                    { primary: "#0057B8", secondary: "#FFCD00" },
  "Aston Villa":                 { primary: "#95BFE5", secondary: "#670E36" },
  "West Ham United":             { primary: "#7A263A", secondary: "#1BB1E7" },
  "Fulham":                      { primary: "#CC0000", secondary: "#FFFFFF" },
  "Brentford":                   { primary: "#D20000", secondary: "#FBB800" },
  "Wolverhampton Wanderers":     { primary: "#FDB913", secondary: "#231F20" },
  "Nottingham Forest":           { primary: "#DD0000", secondary: "#FFFFFF" },
  "Crystal Palace":              { primary: "#1B458F", secondary: "#C4122E" },
  "Everton":                     { primary: "#003399", secondary: "#FFFFFF" },
  "Bournemouth":                 { primary: "#DA291C", secondary: "#000000" },
  "Luton Town":                  { primary: "#F78F1E", secondary: "#FFFFFF" },
  "Sheffield United":            { primary: "#EE2737", secondary: "#000000" },
  "Burnley":                     { primary: "#6C1D45", secondary: "#99D6EA" },
  "Leicester City":              { primary: "#003090", secondary: "#FDBE11" },
  "Ipswich Town":                { primary: "#0044CC", secondary: "#FFFFFF" },
  "Southampton":                 { primary: "#D71920", secondary: "#130C0E" },
  "Leeds United":                { primary: "#FFCD00", secondary: "#1D428A" },
  "Watford":                     { primary: "#FBEE23", secondary: "#ED2127" },
};

function getColors(name: string) {
  return TEAM_COLORS[name] ?? { primary: "#3b82f6", secondary: "#1e3a5f" };
}

// Format season code e.g. 2324 → "23/24"
function formatSeason(s: number | string): string {
  const str = String(s);
  if (str.length === 4) return `${str.slice(0, 2)}/${str.slice(2, 4)}`;
  return str;
}

function FormBadge({ result }: { result: string }) {
  const map: Record<string, { bg: string; label: string }> = {
    W: { bg: "bg-green-500", label: "V" },
    D: { bg: "bg-yellow-500", label: "E" },
    L: { bg: "bg-red-500",   label: "D" },
  };
  const style = map[result] ?? { bg: "bg-gray-500", label: "?" };
  return (
    <span className={`w-7 h-7 rounded-full ${style.bg} text-white text-xs flex items-center justify-center font-bold shadow`}>
      {style.label}
    </span>
  );
}

interface StatCard {
  label: string;
  value: string | number;
  accent: string;
  Icon: React.ElementType;
  iconColor: string;
}

const STAT_CARDS = (team: any): StatCard[] => {
  const played = team.played || 1;
  const gf = team.goalsFor ?? 0;
  const ga = team.goalsAgainst ?? 0;
  const diff = gf - ga;
  const pts = team.won * 3 + team.drawn;
  return [
    { label: "Puntos",             value: pts,                              accent: "from-yellow-500/25 to-yellow-900/10",    Icon: Trophy,      iconColor: "text-yellow-400" },
    { label: "Partidos",           value: played,                           accent: "from-blue-500/20 to-blue-900/10",        Icon: Calendar,    iconColor: "text-blue-400" },
    { label: "Goles / Partido",    value: (gf / played).toFixed(2),         accent: "from-green-500/25 to-green-900/10",     Icon: Crosshair,   iconColor: "text-green-400" },
    { label: "Recibidos / Partido",value: (ga / played).toFixed(2),         accent: "from-red-500/20 to-red-900/10",         Icon: Target,      iconColor: "text-red-400" },
    { label: "Porterías a 0",      value: team.cleanSheets,                 accent: "from-cyan-500/20 to-cyan-900/10",       Icon: ShieldCheck, iconColor: "text-cyan-400" },
    { label: "Diferencia Goles",   value: diff >= 0 ? `+${diff}` : diff,   accent: diff >= 0 ? "from-emerald-500/20 to-emerald-900/10" : "from-orange-500/20 to-orange-900/10", Icon: diff >= 0 ? TrendingUp : TrendingDown, iconColor: diff >= 0 ? "text-emerald-400" : "text-orange-400" },
    { label: "Rating Elo",         value: team.elo,                         accent: "from-purple-500/20 to-purple-900/10",   Icon: Zap,         iconColor: "text-purple-400" },
    { label: "V / E / D",          value: `${team.won} / ${team.drawn} / ${team.lost}`, accent: "from-indigo-500/20 to-indigo-900/10", Icon: BarChart2,   iconColor: "text-indigo-400" },
  ];
};

const TeamProfile = () => {
  const { id } = useParams();
  const [season, setSeason] = useState<string | undefined>(undefined);
  const { data: teams, isLoading } = useAPITeams(season);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32 text-muted-foreground animate-pulse">
        Cargando datos del equipo...
      </div>
    );
  }

  const team = teams?.find(
    t => t.id === id || t.name === id || t.name.toLowerCase().replace(/\s+/g, "-") === id
  );

  // Pull available seasons from first result in list
  const availableSeasons: number[] = (teams?.[0] as any)?.availableSeasons ?? [];

  if (!team) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p className="text-lg font-semibold">Equipo no encontrado en esta temporada: <span className="text-primary">{id}</span></p>
        <p className="text-sm mt-1">Es posible que el equipo no haya participado en la temporada seleccionada.</p>
        <Link to="/dashboard" className="text-primary hover:underline text-sm mt-3 inline-block">
          Volver al Panel
        </Link>
      </div>
    );
  }

  const colors = getColors(team.name);
  const formArr: string[] = Array.isArray((team as any).form?.last5)
    ? (team as any).form.last5
    : Array.isArray((team as any).form) ? (team as any).form : [];
  const played = team.played || 1;

  // Radar derived from real stats
  const radarData = [
    { metric: "Ataque",   value: Math.min(100, Math.round((team.goalsFor / played) * 40)),   avg: 55 },
    { metric: "Defensa",  value: Math.min(100, Math.round(100 - (team.goalsAgainst / played) * 40)), avg: 55 },
    { metric: "Elo",      value: Math.min(100, Math.round((team.elo / 2000) * 100)),           avg: 70 },
    { metric: "Forma",    value: formArr.length ? Math.round((formArr.filter(r => r === "W").length / formArr.length) * 100) : 50, avg: 55 },
    { metric: "Portería", value: Math.min(100, Math.round((team.cleanSheets / played) * 200)), avg: 30 },
  ];

  const barData = [
    { name: "Victorias", value: team.won,   color: "#22c55e" },
    { name: "Empates",   value: team.drawn, color: "#eab308" },
    { name: "Derrotas",  value: team.lost,  color: "#ef4444" },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in pb-10">
      {/* Back + Season selector */}
      <div className="flex items-center justify-between">
        <Link to="/dashboard" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" /> Volver
        </Link>

        {availableSeasons.length > 0 && (
          <div className="relative">
            <select
              value={season ?? ""}
              onChange={e => setSeason(e.target.value || undefined)}
              className="appearance-none text-sm bg-card border border-border rounded-lg pl-3 pr-8 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer"
            >
              <option value="">Todas las temporadas</option>
              {availableSeasons.map(s => (
                <option key={s} value={String(s)}>Temporada {formatSeason(s)}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          </div>
        )}
      </div>

      {/* Hero banner */}
      <div className="glass-card overflow-hidden">
        <div className="h-28 relative" style={{ background: `linear-gradient(135deg, ${colors.primary}60, ${colors.secondary}30, hsl(220 40% 9%))` }}>
          <div className="absolute inset-0 bg-gradient-to-t from-card/90 to-transparent" />
        </div>
        <div className="px-6 pb-6 -mt-10 relative z-10">
          <div className="flex items-end gap-4">
            <div
              className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl font-black border-2 shadow-lg"
              style={{ background: `${colors.primary}22`, borderColor: `${colors.primary}55`, color: colors.primary }}
            >
              {team.name.charAt(0)}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">{team.name}</h1>
              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground flex-wrap">
                <span className="flex items-center gap-1">
                  <Trophy className="h-3.5 w-3.5 text-yellow-400" />
                  {team.won * 3 + team.drawn} pts
                </span>
                <span>Elo: <strong className="text-foreground">{team.elo}</strong></span>
                <span>{team.won}V · {team.drawn}E · {team.lost}D</span>
                {season && (
                  <span className="px-2 py-0.5 rounded-full text-xs font-medium" style={{ background: `${colors.primary}30`, color: colors.primary }}>
                    Temporada {formatSeason(season)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Colored stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {STAT_CARDS(team).map((s, i) => (
          <div
            key={i}
            className={`relative glass-card p-4 text-center overflow-hidden bg-gradient-to-br ${s.accent} border border-white/5`}
          >
            <s.Icon className={`absolute top-2 right-2 h-4 w-4 opacity-30 ${s.iconColor}`} />
            <p className="text-xs text-muted-foreground uppercase tracking-wider leading-tight">{s.label}</p>
            <p className="text-2xl font-bold text-foreground mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Forma reciente */}
      {formArr.length > 0 && (
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-3">Forma Reciente (últimos {Math.min(formArr.length, 10)} partidos)</h2>
          <div className="flex gap-2 flex-wrap">
            {[...formArr].reverse().slice(0, 10).map((r, i) => (
              <FormBadge key={i} result={r} />
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Radar */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
            <Shield className="h-4 w-4 text-primary" /> Perfil del Equipo
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="hsl(220 25% 18%)" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: "hsl(215 20% 55%)" }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  name="Equipo" dataKey="value"
                  stroke={colors.primary} fill={colors.primary} fillOpacity={0.2} strokeWidth={2}
                />
                <Radar
                  name="Media" dataKey="avg"
                  stroke="hsl(215 20% 50%)" fill="hsl(215 20% 50%)" fillOpacity={0.07}
                  strokeWidth={1} strokeDasharray="4 4"
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Results bar chart */}
        <div className="glass-card p-6">
          <h2 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" /> Distribución de Resultados
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 25% 15%)" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: "hsl(215 20% 55%)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "hsl(215 20% 55%)" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(220 40% 9%)",
                    border: "1px solid hsl(220 25% 18%)",
                    borderRadius: "8px",
                    fontSize: "12px"
                  }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {barData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamProfile;
