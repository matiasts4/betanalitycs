import { useState } from "react";
import { ChevronDown, ChevronUp, Database } from "lucide-react";
import { useAPIDetailedHistory } from "@/lib/api";

const DetailedHistory = () => {
  const { data, isLoading, error } = useAPIDetailedHistory(100);
  const [expandedMatch, setExpandedMatch] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        <p>No se pudo cargar el registro detallado.</p>
      </div>
    );
  }

  const toggleMatch = (matchId: string) => {
    setExpandedMatch(expandedMatch === matchId ? null : matchId);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in pb-10">
      <div className="flex flex-col gap-2">
         <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
           <Database className="w-8 h-8 text-primary" />
           Registro Detallado de Predicciones
         </h1>
         <p className="text-muted-foreground">
           Datos matemáticos exactos (Features imputados a los modelos) y resultados probados de los 16 algoritmos de apuesta.
         </p>
      </div>

      <div className="space-y-4">
        {data.map((match, idx) => {
          const matchId = `${match.date}-${match.home}-${match.away}`;
          const isExpanded = expandedMatch === matchId;

          return (
            <div key={idx} className="glass-card overflow-hidden transition-all duration-300">
               {/* Header Row */}
               <div 
                 className="p-4 flex items-center justify-between cursor-pointer hover:bg-secondary/20"
                 onClick={() => toggleMatch(matchId)}
               >
                 <div className="flex items-center gap-4">
                   <span className="text-sm text-muted-foreground w-28">{match.date}</span>
                   <span className="font-semibold text-foreground flex-1 text-right">{match.home}</span>
                   <span className="bg-secondary/50 px-3 py-1 rounded text-sm font-bold border border-border min-w-[60px] text-center">
                     {match.homeGoals} - {match.awayGoals}
                   </span>
                   <span className="font-semibold text-foreground flex-1">{match.away}</span>
                 </div>
                 <div className="text-muted-foreground ml-4">
                   {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                 </div>
               </div>

               {/* Expanded Details */}
               {isExpanded && (
                 <div className="p-4 border-t border-border/50 bg-secondary/10 grid lg:grid-cols-2 gap-6 animate-fade-in">
                    
                    {/* Features Table */}
                    <div>
                      <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">Features del Modelo (Input)</h3>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
                        {Object.entries(match.features).map(([key, val], i) => (
                          <div key={i} className="flex justify-between border-b border-border/30 pb-1">
                            <span className="text-muted-foreground font-mono truncate mr-2" title={key}>{key}</span>
                            <span className="font-mono text-foreground font-semibold">
                              {typeof val === 'number' ? val.toFixed(2).replace(/\.00$/, '') : val}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Predictions List */}
                    <div>
                      <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">Modelos Analíticos (Output)</h3>
                      <div className="space-y-2">
                        {match.predictions.map((pred, i) => (
                           <div key={i} className="flex items-center justify-between p-2 rounded bg-background/50 border border-border/50 hover:border-primary/50 transition-colors">
                             <span className="text-sm font-medium">{pred.market}</span>
                             <div className="flex items-center gap-3">
                               <span className="text-xs text-muted-foreground">Cuota: <span className="text-foreground">{pred.odds.toFixed(2)}</span></span>
                               <span className="text-xs text-primary font-mono">{pred.probability.toFixed(1)}%</span>
                               <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded font-bold ${pred.won ? "bg-success/20 text-success" : "bg-destructive/20 text-destructive"}`}>
                                 {pred.won ? "Acierto" : "Fallo"}
                               </span>
                             </div>
                           </div>
                        ))}
                      </div>
                    </div>
                 </div>
               )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DetailedHistory;
