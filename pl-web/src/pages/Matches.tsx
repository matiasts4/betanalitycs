import { useState, useMemo } from "react";
import { Search, Loader2, CalendarDays, History } from "lucide-react";
import { useAPIMatches, useAPIUpcomingMatches, mapAPIMatchToMockMatch, mapAPIUpcomingToMockMatch } from "@/lib/api";
import { MatchCard } from "@/components/MatchCard";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type TabType = "upcoming" | "recent";

const Matches = () => {
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<TabType>("upcoming");

  const { data: apiRecentMatches, isLoading: recentLoading } = useAPIMatches();
  const { data: apiUpcomingMatches, isLoading: upcomingLoading } = useAPIUpcomingMatches();

  const recentMatches = useMemo(() => {
    if (!apiRecentMatches) return [];
    return apiRecentMatches.map(mapAPIMatchToMockMatch);
  }, [apiRecentMatches]);

  const upcomingMatches = useMemo(() => {
    if (!apiUpcomingMatches) return [];
    return apiUpcomingMatches.map(mapAPIUpcomingToMockMatch);
  }, [apiUpcomingMatches]);

  const isLoading = activeTab === "upcoming" ? upcomingLoading : recentLoading;
  const matches = activeTab === "upcoming" ? upcomingMatches : recentMatches;

  const filtered = matches.filter((m) => {
    if (!search) return true;
    return (
      m.homeTeam.name.toLowerCase().includes(search.toLowerCase()) ||
      m.awayTeam.name.toLowerCase().includes(search.toLowerCase())
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-1">Partidos</h1>
        <p className="text-sm text-muted-foreground">Partidos y predicciones de la Premier League</p>
      </div>

      {/* Tabs — Simulator-style */}
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab("upcoming")}
          className={cn(
            "flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
            activeTab === "upcoming"
              ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
              : "bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground"
          )}
        >
          <CalendarDays className="h-4 w-4" />
          Test / Demo
          {apiUpcomingMatches && (
            <span className={cn(
              "ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full",
              activeTab === "upcoming" ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground"
            )}>
              {apiUpcomingMatches.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("recent")}
          className={cn(
            "flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
            activeTab === "recent"
              ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
              : "bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground"
          )}
        >
          <History className="h-4 w-4" />
          Recientes
          {apiRecentMatches && (
            <span className={cn(
              "ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full",
              activeTab === "recent" ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground"
            )}>
              {apiRecentMatches.length}
            </span>
          )}
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Buscar equipos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 bg-card border-border"
        />
      </div>

      {/* Content */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          <div className="col-span-full flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          filtered.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))
        )}
      </div>

      {!isLoading && filtered.length === 0 && (
        <div className="text-center py-12 text-muted-foreground glass-card p-10">
          <Search className="h-8 w-8 mx-auto mb-3 opacity-20" />
          <p className="text-sm font-medium">
            {search ? "No se encontraron partidos con ese nombre" : `No hay partidos ${activeTab === "upcoming" ? "de test" : "recientes"}`}
          </p>
        </div>
      )}
    </div>
  );
};

export default Matches;
