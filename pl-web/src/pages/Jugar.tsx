import { useState } from "react";
import { useAPITeamList, fetchPlay, APIPlayResponse } from "@/lib/api";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Loader2, Zap, Trophy, RotateCcw, Home, Plane, Target, Brain, CheckCircle2, XCircle, AlertTriangle, Swords, X } from "lucide-react";

// ---- Stickers config (posiciones desordenadas, hardcodeadas) ----
const STICKERS = [
  "Captura de pantalla 2026-06-29 a la(s) 2.39.41 p.m..png",
  "Captura de pantalla 2026-06-29 a la(s) 3.46.33 p.m..png",
  "btebueno.png",
  "fondo.png",
  "gatobet.png",
  "kdb.png",
  "klop.png",
  "livebueno.png",
  "perrito.png",
  "sk12.png",
  "skt5.png",
  "skt6.png",
  "skt8.png",
  "skt9.png",
  "stk1.png",
  "stk4.png",
];

type StickerConfig = {
  src: string;
  top: string;
  left: string;
  rotate: number;
  size: number;
};

const STICKER_CONFIGS: StickerConfig[] = [
  { src: STICKERS[0], top: "2%", left: "3%", rotate: -15, size: 180 },
  { src: STICKERS[1], top: "5%", left: "68%", rotate: 10, size: 160 },
  { src: STICKERS[2], top: "18%", left: "35%", rotate: -8, size: 200 },
  { src: STICKERS[3], top: "35%", left: "8%", rotate: 18, size: 190 },
  { src: STICKERS[4], top: "42%", left: "78%", rotate: -12, size: 150 },
  { src: STICKERS[5], top: "55%", left: "45%", rotate: 6, size: 175 },
  { src: STICKERS[6], top: "8%", left: "22%", rotate: -22, size: 140 },
  { src: STICKERS[7], top: "65%", left: "18%", rotate: 14, size: 165 },
  { src: STICKERS[8], top: "72%", left: "62%", rotate: -10, size: 185 },
  { src: STICKERS[9], top: "25%", left: "85%", rotate: 25, size: 130 },
  { src: STICKERS[10], top: "82%", left: "35%", rotate: -18, size: 170 },
  { src: STICKERS[11], top: "48%", left: "1%", rotate: 8, size: 195 },
  { src: STICKERS[12], top: "0%", left: "48%", rotate: 20, size: 135 },
  { src: STICKERS[13], top: "60%", left: "88%", rotate: -28, size: 155 },
  { src: STICKERS[14], top: "88%", left: "5%", rotate: 12, size: 180 },
  { src: STICKERS[15], top: "12%", left: "12%", rotate: -6, size: 205 },
  { src: STICKERS[0], top: "30%", left: "55%", rotate: 16, size: 145 },
  { src: STICKERS[3], top: "78%", left: "75%", rotate: -14, size: 160 },
  { src: STICKERS[8], top: "92%", left: "50%", rotate: 22, size: 140 },
  { src: STICKERS[5], top: "15%", left: "90%", rotate: -20, size: 170 },
  { src: STICKERS[11], top: "68%", left: "40%", rotate: 10, size: 150 },
  { src: STICKERS[2], top: "95%", left: "15%", rotate: -16, size: 165 },
  { src: STICKERS[7], top: "38%", left: "30%", rotate: 28, size: 135 },
  { src: STICKERS[13], top: "52%", left: "65%", rotate: -8, size: 175 },
];

// ---- Confetti pieces ----
const CONFETTI_COLORS = ["#3b82f6", "#22d3ee", "#a855f7", "#f59e0b", "#ef4444", "#10b981"];
const CONFETTI_PIECES = Array.from({ length: 80 }, (_, i) => ({
  id: i,
  left: Math.random() * 100,
  delay: Math.random() * 1.5,
  duration: 2 + Math.random() * 2,
  color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
  rotate: Math.random() * 360,
}));

type Pick = "home" | "away" | "draw";

const resultColors: Record<string, string> = {
  W: "#10b981",
  D: "#f59e0b",
  L: "#ef4444",
};

export default function Jugar() {
  const { data: teams, isLoading: teamsLoading } = useAPITeamList();
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [loading, setLoading] = useState(false);
  const [playData, setPlayData] = useState<APIPlayResponse | null>(null);
  const [userPick, setUserPick] = useState<Pick | null>(null);
  const [result, setResult] = useState<"win" | "lose" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [deciding, setDeciding] = useState(false);
  const [showWinModal, setShowWinModal] = useState(false);

  const handleLoad = async () => {
    if (!homeTeam || !awayTeam) return;
    if (homeTeam === awayTeam) {
      setError("Selecciona dos equipos diferentes");
      return;
    }
    setError(null);
    setLoading(true);
    setPlayData(null);
    setUserPick(null);
    setResult(null);
    try {
      const data = await fetchPlay(homeTeam, awayTeam);
      setPlayData(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al cargar el partido");
    } finally {
      setLoading(false);
    }
  };

  const handlePick = (pick: Pick) => {
    if (!playData || result || deciding) return;
    setUserPick(pick);
    setDeciding(true);
    setTimeout(() => {
      if (pick === playData.modelPrediction.pick) {
        setResult("win");
        setShowWinModal(true);
      } else {
        setResult("lose");
      }
      setDeciding(false);
    }, 2000);
  };

  const handleReset = () => {
    setPlayData(null);
    setUserPick(null);
    setResult(null);
    setError(null);
    setShowWinModal(false);
  };

  return (
    <div
      style={{
        position: "relative",
        minHeight: "100vh",
        width: "100%",
        background: "radial-gradient(circle at top right, hsl(228 40% 12%), hsl(228 40% 4%) 40%)",
        color: "hsl(var(--foreground))",
        overflow: "hidden",
        fontFamily: "inherit",
      }}
    >
      {/* Stickers de fondo */}
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", zIndex: 0 }}>
        {STICKER_CONFIGS.map((s, i) => (
          <img
            key={i}
            src={`/stickers/${encodeURIComponent(s.src)}`}
            alt=""
            style={{
              position: "absolute",
              top: s.top,
              left: s.left,
              width: `${s.size}px`,
              transform: `rotate(${s.rotate}deg)`,
              opacity: 0.50,
              pointerEvents: "none",
              userSelect: "none",
            }}
          />
        ))}
      </div>

      {/* Overlay de celebración */}
      {result === "win" && showWinModal && (
        <div className="celebration-overlay" style={{
          position: "fixed",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(0,0,0,0.55)",
          zIndex: 9999,
        }}>
          {/* Confetti */}
          <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
            {CONFETTI_PIECES.map((c) => (
              <div
                key={c.id}
                className="confetti"
                style={{
                  position: "absolute",
                  left: `${c.left}%`,
                  top: "-10px",
                  width: "10px",
                  height: "18px",
                  background: c.color,
                  transform: `rotate(${c.rotate}deg)`,
                  animation: `confettiFall ${c.duration}s ${c.delay}s linear forwards`,
                }}
              />
            ))}
          </div>
          <div style={{
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "24px",
            padding: "48px 56px",
            textAlign: "center",
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
            zIndex: 1,
            position: "relative",
            minWidth: "320px",
          }}>
            {/* Botón cerrar modal */}
            <button
              onClick={() => setShowWinModal(false)}
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                color: "hsl(var(--muted-foreground))",
                cursor: "pointer",
                padding: "4px",
                borderRadius: "50%",
                transition: "all 0.2s",
              }}
              className="hover:bg-muted hover:text-foreground"
            >
              <X size={20} />
            </button>

            <h1 style={{
              fontSize: "48px",
              fontWeight: 900,
              color: "hsl(var(--foreground))",
              margin: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "12px",
            }}>
              <Trophy size={52} style={{ color: "#f59e0b" }} />
              ¡WINNER!
            </h1>
            <p style={{ fontSize: "18px", color: "hsl(var(--muted-foreground))", marginTop: "12px" }}>
              Acertaste la predicción del modelo
            </p>
            <Button onClick={handleReset} style={{ marginTop: "24px", background: "hsl(var(--primary))", color: "hsl(var(--primary-foreground))" }}>
              <RotateCcw size={18} style={{ marginRight: 8 }} />
              Jugar de nuevo
            </Button>
          </div>
        </div>
      )}

      {/* Contenido principal */}
      <div style={{ position: "relative", zIndex: 1, maxWidth: "1100px", margin: "0 auto", padding: "40px 24px 80px" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "36px" }}>
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "12px",
            background: "rgba(59,130,246,0.1)",
            borderRadius: "999px",
            padding: "8px 20px",
            marginBottom: "16px",
          }}>
            <Zap size={20} style={{ color: "hsl(var(--primary))" }} />
            <span style={{ fontWeight: 600, color: "hsl(var(--primary))" }}>FERIA DE CIENCIA · PL-WEB</span>
          </div>
          <h1 style={{
            fontSize: "44px",
            fontWeight: 900,
            color: "hsl(var(--foreground))",
            margin: 0,
            letterSpacing: "-1px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "14px",
          }}>
            <Swords size={40} style={{ color: "hsl(var(--primary))" }} />
            Adivina al Modelo
          </h1>
          <p style={{ fontSize: "17px", color: "hsl(var(--muted-foreground))", marginTop: "8px" }}>
            ¿Qué equipo <strong>predice el modelo</strong> que ganará? Acerta su predicción y gana el premio.
          </p>
        </div>

        {/* Selector de equipos */}
        <div style={{
          background: "linear-gradient(135deg, hsl(var(--card)/0.92), hsl(var(--card)/0.88))",
          backdropFilter: "blur(16px)",
          borderRadius: "20px",
          padding: "28px",
          boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
          border: "1px solid hsl(var(--border)/0.8)",
          marginBottom: "24px",
        }}>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "20px",
            alignItems: "flex-end",
            justifyContent: "center",
          }}>
            <div style={{ flex: "1 1 200px", minWidth: "200px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", fontWeight: 700, color: "#1e40af", marginBottom: "8px" }}>
                <Home size={14} />
                EQUIPO LOCAL
              </label>
              <Select value={homeTeam} onValueChange={setHomeTeam}>
                <SelectTrigger style={{ background: "hsl(var(--muted)/0.5)", borderColor: "hsl(var(--border))", height: "44px", color: "hsl(var(--foreground))", fontWeight: 600 }}>
                  <SelectValue placeholder="Selecciona local" />
                </SelectTrigger>
                <SelectContent style={{ background: "hsl(var(--popover))", color: "hsl(var(--foreground))", borderColor: "hsl(var(--border))" }}>
                  {teamsLoading ? (
                    <SelectItem value="__loading" disabled>Cargando equipos…</SelectItem>
                  ) : (
                    teams?.map((t: string) => (
                      <SelectItem key={t} value={t} style={{ color: "hsl(var(--foreground))" }}>{t}</SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "0 4px" }}>
              <div style={{
                background: "hsl(var(--primary))",
                color: "hsl(var(--primary-foreground))",
                borderRadius: "50%",
                width: "40px",
                height: "40px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
                fontSize: "14px",
              }}>
                VS
              </div>
            </div>

            <div style={{ flex: "1 1 200px", minWidth: "200px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", fontWeight: 700, color: "#1e40af", marginBottom: "8px" }}>
                <Plane size={14} />
                EQUIPO VISITANTE
              </label>
              <Select value={awayTeam} onValueChange={setAwayTeam}>
                <SelectTrigger style={{ background: "hsl(var(--muted)/0.5)", borderColor: "hsl(var(--border))", height: "44px", color: "hsl(var(--foreground))", fontWeight: 600 }}>
                  <SelectValue placeholder="Selecciona visitante" />
                </SelectTrigger>
                <SelectContent style={{ background: "hsl(var(--popover))", color: "hsl(var(--foreground))", borderColor: "hsl(var(--border))" }}>
                  {teamsLoading ? (
                    <SelectItem value="__loading" disabled>Cargando equipos…</SelectItem>
                  ) : (
                    teams?.map((t: string) => (
                      <SelectItem key={t} value={t} style={{ color: "hsl(var(--foreground))" }}>{t}</SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleLoad}
              disabled={loading || !homeTeam || !awayTeam}
              style={{
                background: "linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary)/0.8))",
                color: "hsl(var(--primary-foreground))",
                height: "44px",
                padding: "0 28px",
                fontSize: "15px",
                fontWeight: 700,
              }}
            >
              {loading ? <Loader2 size={18} className="animate-spin" style={{ marginRight: 8 }} /> : <Zap size={18} style={{ marginRight: 8 }} />}
              Cargar Partido
            </Button>
          </div>

          {error && (
            <p style={{ color: "#dc2626", textAlign: "center", marginTop: "16px", fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
              <AlertTriangle size={16} /> {error}
            </p>
          )}
        </div>

        {/* Datos del partido */}
        {playData && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {/* ELO + título del partido */}
            <div style={{
              background: "linear-gradient(135deg, hsl(var(--card)/0.92), hsl(var(--card)/0.88))",
              backdropFilter: "blur(16px)",
              borderRadius: "20px",
              padding: "24px 28px",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
              border: "1px solid hsl(var(--border)/0.8)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "16px",
            }}>
              <div style={{ textAlign: "center", flex: "1" }}>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "hsl(var(--muted-foreground))" }}>LOCAL</div>
                <div style={{ fontSize: "22px", fontWeight: 800, color: "hsl(var(--foreground))" }}>{playData.homeTeam}</div>
                <div style={{
                  display: "inline-block",
                  marginTop: "6px",
                  background: "hsl(var(--muted))",
                  color: "hsl(var(--primary))",
                  fontWeight: 800,
                  padding: "4px 14px",
                  borderRadius: "999px",
                  fontSize: "15px",
                  border: "1px solid hsl(var(--border))",
                }}>
                  ELO {playData.homeElo}
                </div>
              </div>

              <div style={{
                background: "hsl(var(--primary))",
                color: "hsl(var(--primary-foreground))",
                borderRadius: "50%",
                width: "48px",
                height: "48px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
              }}>
                VS
              </div>

              <div style={{ textAlign: "center", flex: "1" }}>
                <div style={{ fontSize: "13px", fontWeight: 700, color: "hsl(var(--muted-foreground))" }}>VISITANTE</div>
                <div style={{ fontSize: "22px", fontWeight: 800, color: "hsl(var(--foreground))" }}>{playData.awayTeam}</div>
                <div style={{
                  display: "inline-block",
                  marginTop: "6px",
                  background: "hsl(var(--muted))",
                  color: "hsl(var(--primary))",
                  fontWeight: 800,
                  padding: "4px 14px",
                  borderRadius: "999px",
                  fontSize: "15px",
                  border: "1px solid hsl(var(--border))",
                }}>
                  ELO {playData.awayElo}
                </div>
              </div>
            </div>

            {/* Últimos 5 partidos */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "20px",
            }} className="jugar-last5-grid">
              <Last5Card title={`Últimos 5 · ${playData.homeTeam}`} matches={playData.homeLast5} />
              <Last5Card title={`Últimos 5 · ${playData.awayTeam}`} matches={playData.awayLast5} />
            </div>

            {/* Botones de predicción */}
            <div style={{
              background: "linear-gradient(135deg, hsl(var(--card)/0.92), hsl(var(--card)/0.88))",
              backdropFilter: "blur(16px)",
              borderRadius: "20px",
              padding: "28px",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
              border: "1px solid hsl(var(--border)/0.8)",
            }}>
              <h2 style={{ textAlign: "center", fontSize: "22px", fontWeight: 800, color: "hsl(var(--foreground))", marginBottom: "6px", display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
                <Target size={22} style={{ color: "hsl(var(--primary))" }} />
                ¿Qué predice el modelo?
              </h2>
              <p style={{ textAlign: "center", color: "hsl(var(--muted-foreground))", fontSize: "14px", marginBottom: "20px" }}>
                Analiza las estadísticas y adivina cuál será la predicción del modelo de Machine Learning
              </p>

              <div style={{ display: "flex", gap: "14px", justifyContent: "center", flexWrap: "wrap" }}>
                <PickButton
                  active={userPick === "home"}
                  disabled={!!result || deciding}
                  onClick={() => handlePick("home")}
                  color="#10b981"
                  label={`Gana ${playData.homeTeam}`}
                />
                <PickButton
                  active={userPick === "draw"}
                  disabled={!!result || deciding}
                  onClick={() => handlePick("draw")}
                  color="#f59e0b"
                  label="Empate"
                />
                <PickButton
                  active={userPick === "away"}
                  disabled={!!result || deciding}
                  onClick={() => handlePick("away")}
                  color="#3b82f6"
                  label={`Gana ${playData.awayTeam}`}
                />
              </div>

              {/* Barra de carga decidiendo */}
              {deciding && (
                <div style={{ marginTop: "24px", textAlign: "center" }}>
                  <div style={{
                    fontSize: "18px",
                    fontWeight: 700,
                    color: "hsl(var(--primary))",
                    marginBottom: "14px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                  }}>
                    <Brain size={20} style={{ color: "hsl(var(--primary))" }} />
                    Consultando los modelos de ML...
                  </div>
                  <div style={{
                    width: "100%",
                    maxWidth: "400px",
                    margin: "0 auto",
                    height: "12px",
                    background: "hsl(var(--muted))",
                    borderRadius: "999px",
                    overflow: "hidden",
                    border: "1px solid hsl(var(--border))",
                  }}>
                    <div style={{
                      height: "100%",
                      background: "linear-gradient(90deg, hsl(var(--primary)), hsl(var(--primary)/0.6), hsl(var(--primary)))",
                      backgroundSize: "200% 100%",
                      borderRadius: "999px",
                      animation: "loadingBar 2s linear forwards",
                    }} />
                  </div>
                </div>
              )}

              {/* Resultado */}
              {result && (
                <div style={{ marginTop: "24px", textAlign: "center" }}>
                  {result === "win" ? (
                    <div style={{
                      background: "linear-gradient(135deg, hsl(var(--success)), hsl(var(--success)/0.8))",
                      color: "hsl(var(--success-foreground))",
                      padding: "16px 24px",
                      borderRadius: "14px",
                      fontSize: "20px",
                      fontWeight: 800,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "12px",
                    }}>
                      <CheckCircle2 size={24} />
                      ¡Correcto! Adivinaste la predicción del modelo
                    </div>
                  ) : (
                    <div style={{
                      background: "linear-gradient(135deg, hsl(var(--destructive)), hsl(var(--destructive)/0.8))",
                      color: "hsl(var(--destructive-foreground))",
                      padding: "16px 24px",
                      borderRadius: "14px",
                      fontSize: "20px",
                      fontWeight: 800,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "12px",
                    }}>
                      <XCircle size={24} />
                      No coincidiste con el modelo
                    </div>
                  )}

                  <div style={{
                    marginTop: "14px",
                    background: "hsl(var(--muted)/0.5)",
                    padding: "12px 20px",
                    borderRadius: "12px",
                    display: "inline-block",
                    border: "1px solid hsl(var(--border))",
                  }}>
                    <span style={{ fontWeight: 700, color: "hsl(var(--primary))" }}>
                      El modelo predice:{" "}
                    </span>
                    <span style={{ fontWeight: 800, color: "hsl(var(--foreground))" }}>
                      {playData.modelPrediction.pick === "home" && `Gana ${playData.homeTeam}`}
                      {playData.modelPrediction.pick === "away" && `Gana ${playData.awayTeam}`}
                      {playData.modelPrediction.pick === "draw" && "Empate"}
                    </span>
                    <span style={{ color: "hsl(var(--muted-foreground))", marginLeft: "8px", fontSize: "13px" }}>
                      ({playData.modelPrediction.probability}% confianza)
                    </span>
                  </div>

                  <div style={{ marginTop: "20px" }}>
                    <Button onClick={handleReset} variant="outline" style={{ borderColor: "hsl(var(--primary))", color: "hsl(var(--primary))", fontWeight: 700 }}>
                      <RotateCcw size={18} style={{ marginRight: 8 }} />
                      Jugar de nuevo
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Placeholder cuando no hay datos */}
        {!playData && !loading && (
          <div style={{
            background: "linear-gradient(135deg, hsl(var(--card)/0.92), hsl(var(--card)/0.88))",
            backdropFilter: "blur(16px)",
            borderRadius: "20px",
            padding: "60px 24px",
            textAlign: "center",
            border: "2px dashed hsl(var(--border))",
          }}>
            <div style={{ display: "flex", justifyContent: "center", marginBottom: "16px" }}>
              <Swords size={56} style={{ color: "hsl(var(--muted-foreground)/0.4)" }} />
            </div>
            <p style={{ fontSize: "18px", color: "hsl(var(--muted-foreground))", fontWeight: 600 }}>
              Selecciona dos equipos y carga el partido para empezar a jugar
            </p>
          </div>
        )}
      </div>

      {/* CSS para animación de confetti */}
      <style>{`
        @keyframes confettiFall {
          0% { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        @keyframes loadingBar {
          0% { width: 0%; background-position: 0% 0%; }
          50% { width: 70%; background-position: 100% 0%; }
          100% { width: 100%; background-position: 200% 0%; }
        }
        @media (max-width: 768px) {
          .jugar-last5-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}

// ---- Sub-componente: tarjeta últimos 5 ----
function Last5Card({ title, matches }: {
  title: string;
  matches: APIPlayResponse["homeLast5"];
}) {
  return (
    <div style={{
      background: "linear-gradient(135deg, hsl(var(--card)/0.6), hsl(var(--card)/0.4))",
      backdropFilter: "blur(12px)",
      borderRadius: "20px",
      padding: "20px",
      boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
      border: "1px solid hsl(var(--border)/0.6)",
    }}>
      <h3 style={{ fontSize: "15px", fontWeight: 800, color: "hsl(var(--primary))", marginBottom: "14px" }}>
        {title}
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {matches.map((m, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              background: "hsl(var(--muted)/0.4)",
              borderRadius: "12px",
              padding: "10px 14px",
              border: "1px solid hsl(var(--border)/0.3)",
            }}
          >
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 900,
              color: "white",
              fontSize: "14px",
              background: resultColors[m.result],
              flexShrink: 0,
            }}>
              {m.result}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: "14px", fontWeight: 700, color: "hsl(var(--foreground))", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                vs {m.opponent}
              </div>
              <div style={{ fontSize: "12px", color: "hsl(var(--muted-foreground))" }}>
                {m.date} · {m.venue}
              </div>
            </div>
            <div style={{
              fontSize: "13px",
              fontWeight: 700,
              color: "hsl(var(--foreground))",
              flexShrink: 0,
            }}>
              {m.teamGoals}–{m.oppGoals}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---- Sub-componente: botón de predicción ----
function PickButton({ label, color, active, disabled, onClick }: {
  label: string;
  color: string;
  active: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        background: active ? color : "hsl(var(--card))",
        color: active ? "white" : color,
        border: `2px solid ${color}`,
        borderRadius: "14px",
        padding: "14px 28px",
        fontSize: "16px",
        fontWeight: 800,
        cursor: disabled ? "default" : "pointer",
        transition: "all 0.2s",
        boxShadow: active ? `0 8px 24px ${color}55` : "0 2px 8px rgba(0,0,0,0.4)",
        opacity: disabled && !active ? 0.3 : 1,
      }}
    >
      {label}
    </button>
  );
}
