// ============================================================
// Extended mock data with full Team, Player, Referee profiles
// ============================================================

export interface Team {
  id: string;
  name: string;
  shortName: string;
  logo: string;
  colors: { primary: string; secondary: string };
  leaguePosition: number;
  stats: {
    played: number;
    won: number;
    drawn: number;
    lost: number;
    goalsFor: number;
    goalsAgainst: number;
    points: number;
    avgPossession: number;
    cleanSheets: number;
    over25Pct: number;
  };
  radar: { attack: number; defense: number; midfield: number; form: number; setPieces: number; discipline: number };
  formXg: { match: string; xgFor: number; xgAgainst: number }[];
  playerIds: string[];
}

export interface Player {
  id: string;
  name: string;
  teamId: string;
  position: string;
  number: number;
  nationality: string;
  stats: {
    appearances: number;
    goals: number;
    xG: number;
    assists: number;
    xA: number;
    shotsOnTargetPer90: number;
    foulsCommittedPer90: number;
    yellowCards: number;
    redCards: number;
    minutesPlayed: number;
  };
}

export interface Referee {
  id: string;
  name: string;
  matchesOfficiated: number;
  results: { homeWins: number; awayWins: number; draws: number };
  discipline: {
    avgYellowPerGame: number;
    totalYellows: number;
    totalReds: number;
    foulsPerTackle: number;
  };
}

export interface Match {
  id: string;
  homeTeam: Team;
  awayTeam: Team;
  date: string;
  time: string;
  stadium: string;
  refereeId: string;
  prediction: { homeWin: number; draw: number; awayWin: number };
  markets: MarketPrediction[];
  status: "upcoming" | "live" | "completed";
  score?: { home: number; away: number };
}

export interface MarketPrediction {
  category: "match-odds" | "goals" | "player-props" | "cards-corners";
  name: string;
  prediction: string;
  odds: number | null;
  fairOdds: number | null;
  confidence: number;
  edge: number | null;
  provider?: string;
  result?: "won" | "lost" | "pending";
}

export interface BotStats {
  totalPredictions: number;
  winRate: number;
  roi: number;
  totalProfit: number;
  streak: number;
}

export interface HistoryEntry {
  id: string;
  date: string;
  match: string;
  market: string;
  prediction: string;
  odds: number;
  stake: number;
  result: "won" | "lost";
  profit: number;
}

// ===================== TEAMS =====================
export const teamsData: Record<string, Team> = {
  arsenal: {
    id: "arsenal", name: "Arsenal", shortName: "ARS", logo: "🔴",
    colors: { primary: "#EF0107", secondary: "#063672" },
    leaguePosition: 1,
    stats: { played: 29, won: 22, drawn: 4, lost: 3, goalsFor: 62, goalsAgainst: 22, points: 70, avgPossession: 58.3, cleanSheets: 14, over25Pct: 69 },
    radar: { attack: 88, defense: 85, midfield: 82, form: 90, setPieces: 78, discipline: 72 },
    formXg: [
      { match: "vs BHA", xgFor: 2.1, xgAgainst: 0.8 },
      { match: "vs LIV", xgFor: 1.4, xgAgainst: 1.1 },
      { match: "vs WHU", xgFor: 2.8, xgAgainst: 0.5 },
      { match: "vs CHE", xgFor: 1.9, xgAgainst: 1.3 },
      { match: "vs NEW", xgFor: 2.3, xgAgainst: 0.9 },
    ],
    playerIds: ["saka", "odegaard", "havertz", "rice", "saliba", "raya"],
  },
  manCity: {
    id: "manCity", name: "Manchester City", shortName: "MCI", logo: "🔵",
    colors: { primary: "#6CABDD", secondary: "#1C2C5B" },
    leaguePosition: 2,
    stats: { played: 29, won: 20, drawn: 5, lost: 4, goalsFor: 65, goalsAgainst: 28, points: 65, avgPossession: 62.1, cleanSheets: 11, over25Pct: 72 },
    radar: { attack: 92, defense: 80, midfield: 90, form: 82, setPieces: 75, discipline: 76 },
    formXg: [
      { match: "vs WHU", xgFor: 3.1, xgAgainst: 0.4 },
      { match: "vs TOT", xgFor: 2.0, xgAgainst: 1.5 },
      { match: "vs AVL", xgFor: 1.8, xgAgainst: 1.2 },
      { match: "vs BHA", xgFor: 2.5, xgAgainst: 0.7 },
      { match: "vs MUN", xgFor: 2.2, xgAgainst: 1.0 },
    ],
    playerIds: ["haaland", "kdb", "foden", "rodri", "dias", "ederson"],
  },
  liverpool: {
    id: "liverpool", name: "Liverpool", shortName: "LIV", logo: "🔴",
    colors: { primary: "#C8102E", secondary: "#00B2A9" },
    leaguePosition: 3,
    stats: { played: 29, won: 19, drawn: 6, lost: 4, goalsFor: 58, goalsAgainst: 25, points: 63, avgPossession: 56.8, cleanSheets: 13, over25Pct: 65 },
    radar: { attack: 85, defense: 84, midfield: 80, form: 78, setPieces: 82, discipline: 70 },
    formXg: [
      { match: "vs TOT", xgFor: 1.6, xgAgainst: 1.3 },
      { match: "vs NEW", xgFor: 2.0, xgAgainst: 0.9 },
      { match: "vs MUN", xgFor: 2.4, xgAgainst: 0.6 },
      { match: "vs AVL", xgFor: 1.3, xgAgainst: 1.5 },
      { match: "vs BHA", xgFor: 1.8, xgAgainst: 0.8 },
    ],
    playerIds: ["salah", "nunez", "macallister", "szoboszlai", "virgil", "alisson"],
  },
  chelsea: {
    id: "chelsea", name: "Chelsea", shortName: "CHE", logo: "🔵",
    colors: { primary: "#034694", secondary: "#DBA111" },
    leaguePosition: 5,
    stats: { played: 29, won: 15, drawn: 7, lost: 7, goalsFor: 50, goalsAgainst: 35, points: 52, avgPossession: 55.2, cleanSheets: 8, over25Pct: 62 },
    radar: { attack: 75, defense: 68, midfield: 74, form: 65, setPieces: 70, discipline: 60 },
    formXg: [
      { match: "vs NEW", xgFor: 2.0, xgAgainst: 0.6 },
      { match: "vs ARS", xgFor: 1.3, xgAgainst: 1.9 },
      { match: "vs WHU", xgFor: 1.7, xgAgainst: 1.0 },
      { match: "vs BHA", xgFor: 1.1, xgAgainst: 1.4 },
      { match: "vs TOT", xgFor: 1.9, xgAgainst: 1.2 },
    ],
    playerIds: ["palmer", "jackson", "caicedo", "enzo", "colwill", "sanchez"],
  },
  manUtd: {
    id: "manUtd", name: "Manchester United", shortName: "MUN", logo: "🔴",
    colors: { primary: "#DA291C", secondary: "#FBE122" },
    leaguePosition: 7,
    stats: { played: 29, won: 13, drawn: 5, lost: 11, goalsFor: 42, goalsAgainst: 40, points: 44, avgPossession: 52.1, cleanSheets: 7, over25Pct: 58 },
    radar: { attack: 65, defense: 58, midfield: 62, form: 50, setPieces: 68, discipline: 55 },
    formXg: [
      { match: "vs AVL", xgFor: 1.2, xgAgainst: 1.8 },
      { match: "vs LIV", xgFor: 0.6, xgAgainst: 2.4 },
      { match: "vs MCI", xgFor: 1.0, xgAgainst: 2.2 },
      { match: "vs BHA", xgFor: 1.5, xgAgainst: 1.1 },
      { match: "vs WHU", xgFor: 1.8, xgAgainst: 0.9 },
    ],
    playerIds: ["rashford", "bruno", "mainoo", "garnacho", "martinez", "onana"],
  },
  tottenham: {
    id: "tottenham", name: "Tottenham", shortName: "TOT", logo: "⚪",
    colors: { primary: "#132257", secondary: "#FFFFFF" },
    leaguePosition: 6,
    stats: { played: 29, won: 14, drawn: 6, lost: 9, goalsFor: 55, goalsAgainst: 38, points: 48, avgPossession: 54.5, cleanSheets: 6, over25Pct: 71 },
    radar: { attack: 78, defense: 60, midfield: 72, form: 62, setPieces: 74, discipline: 58 },
    formXg: [
      { match: "vs LIV", xgFor: 1.3, xgAgainst: 1.6 },
      { match: "vs MCI", xgFor: 1.5, xgAgainst: 2.0 },
      { match: "vs CHE", xgFor: 1.2, xgAgainst: 1.9 },
      { match: "vs NEW", xgFor: 2.1, xgAgainst: 1.0 },
      { match: "vs BHA", xgFor: 0.0, xgAgainst: 0.8 },
    ],
    playerIds: ["son", "maddison", "kulusevski", "bissouma", "romero", "vicario"],
  },
  newcastle: {
    id: "newcastle", name: "Newcastle", shortName: "NEW", logo: "⬛",
    colors: { primary: "#241F20", secondary: "#FFFFFF" },
    leaguePosition: 4,
    stats: { played: 29, won: 16, drawn: 7, lost: 6, goalsFor: 52, goalsAgainst: 30, points: 55, avgPossession: 51.3, cleanSheets: 10, over25Pct: 55 },
    radar: { attack: 74, defense: 82, midfield: 70, form: 75, setPieces: 80, discipline: 68 },
    formXg: [
      { match: "vs CHE", xgFor: 0.6, xgAgainst: 2.0 },
      { match: "vs LIV", xgFor: 0.9, xgAgainst: 2.0 },
      { match: "vs TOT", xgFor: 1.0, xgAgainst: 2.1 },
      { match: "vs WHU", xgFor: 2.3, xgAgainst: 0.7 },
      { match: "vs AVL", xgFor: 1.6, xgAgainst: 1.2 },
    ],
    playerIds: ["isak", "gordon", "guimaraes", "joelinton", "botman", "pope"],
  },
  brighton: {
    id: "brighton", name: "Brighton", shortName: "BHA", logo: "🔵",
    colors: { primary: "#0057B8", secondary: "#FFCD00" },
    leaguePosition: 8,
    stats: { played: 29, won: 12, drawn: 8, lost: 9, goalsFor: 48, goalsAgainst: 42, points: 44, avgPossession: 57.9, cleanSheets: 5, over25Pct: 68 },
    radar: { attack: 72, defense: 62, midfield: 78, form: 60, setPieces: 65, discipline: 74 },
    formXg: [
      { match: "vs ARS", xgFor: 0.8, xgAgainst: 2.1 },
      { match: "vs MCI", xgFor: 0.7, xgAgainst: 2.5 },
      { match: "vs TOT", xgFor: 0.8, xgAgainst: 0.0 },
      { match: "vs CHE", xgFor: 1.4, xgAgainst: 1.1 },
      { match: "vs LIV", xgFor: 0.8, xgAgainst: 1.8 },
    ],
    playerIds: ["mitoma", "joaoPedro", "march", "gross", "dunk", "verbruggen"],
  },
  astonVilla: {
    id: "astonVilla", name: "Aston Villa", shortName: "AVL", logo: "🟣",
    colors: { primary: "#670E36", secondary: "#95BFE5" },
    leaguePosition: 9,
    stats: { played: 29, won: 12, drawn: 6, lost: 11, goalsFor: 44, goalsAgainst: 40, points: 42, avgPossession: 53.8, cleanSheets: 7, over25Pct: 60 },
    radar: { attack: 70, defense: 64, midfield: 68, form: 55, setPieces: 72, discipline: 66 },
    formXg: [
      { match: "vs MUN", xgFor: 1.8, xgAgainst: 1.2 },
      { match: "vs MCI", xgFor: 1.2, xgAgainst: 1.8 },
      { match: "vs LIV", xgFor: 1.5, xgAgainst: 1.3 },
      { match: "vs NEW", xgFor: 1.2, xgAgainst: 1.6 },
      { match: "vs WHU", xgFor: 2.0, xgAgainst: 0.9 },
    ],
    playerIds: ["watkins", "rogers", "mcginn", "tielemans", "torres", "martinez_av"],
  },
  westHam: {
    id: "westHam", name: "West Ham", shortName: "WHU", logo: "🟤",
    colors: { primary: "#7A263A", secondary: "#1BB1E7" },
    leaguePosition: 10,
    stats: { played: 29, won: 10, drawn: 7, lost: 12, goalsFor: 38, goalsAgainst: 46, points: 37, avgPossession: 48.5, cleanSheets: 5, over25Pct: 62 },
    radar: { attack: 58, defense: 55, midfield: 60, form: 48, setPieces: 65, discipline: 52 },
    formXg: [
      { match: "vs MCI", xgFor: 0.4, xgAgainst: 3.1 },
      { match: "vs ARS", xgFor: 0.5, xgAgainst: 2.8 },
      { match: "vs CHE", xgFor: 1.0, xgAgainst: 1.7 },
      { match: "vs NEW", xgFor: 0.7, xgAgainst: 2.3 },
      { match: "vs MUN", xgFor: 0.9, xgAgainst: 1.8 },
    ],
    playerIds: ["bowen", "kudus", "paqueta", "ward_prowse", "zouma", "areola"],
  },
};

// ===================== PLAYERS =====================
export const playersData: Record<string, Player> = {
  saka: { id: "saka", name: "Bukayo Saka", teamId: "arsenal", position: "RW", number: 7, nationality: "England", stats: { appearances: 27, goals: 14, xG: 12.3, assists: 9, xA: 7.8, shotsOnTargetPer90: 1.8, foulsCommittedPer90: 0.9, yellowCards: 4, redCards: 0, minutesPlayed: 2340 } },
  odegaard: { id: "odegaard", name: "Martin Ødegaard", teamId: "arsenal", position: "CAM", number: 8, nationality: "Norway", stats: { appearances: 25, goals: 8, xG: 6.5, assists: 11, xA: 9.2, shotsOnTargetPer90: 1.2, foulsCommittedPer90: 1.1, yellowCards: 3, redCards: 0, minutesPlayed: 2100 } },
  havertz: { id: "havertz", name: "Kai Havertz", teamId: "arsenal", position: "CF", number: 29, nationality: "Germany", stats: { appearances: 28, goals: 12, xG: 10.8, assists: 5, xA: 4.2, shotsOnTargetPer90: 1.4, foulsCommittedPer90: 1.5, yellowCards: 6, redCards: 0, minutesPlayed: 2380 } },
  rice: { id: "rice", name: "Declan Rice", teamId: "arsenal", position: "CDM", number: 41, nationality: "England", stats: { appearances: 29, goals: 5, xG: 3.8, assists: 7, xA: 5.5, shotsOnTargetPer90: 0.6, foulsCommittedPer90: 1.8, yellowCards: 8, redCards: 1, minutesPlayed: 2610 } },
  saliba: { id: "saliba", name: "William Saliba", teamId: "arsenal", position: "CB", number: 2, nationality: "France", stats: { appearances: 28, goals: 2, xG: 1.5, assists: 1, xA: 0.8, shotsOnTargetPer90: 0.2, foulsCommittedPer90: 0.8, yellowCards: 5, redCards: 0, minutesPlayed: 2520 } },
  raya: { id: "raya", name: "David Raya", teamId: "arsenal", position: "GK", number: 22, nationality: "Spain", stats: { appearances: 29, goals: 0, xG: 0, assists: 0, xA: 0, shotsOnTargetPer90: 0, foulsCommittedPer90: 0.1, yellowCards: 1, redCards: 0, minutesPlayed: 2610 } },

  haaland: { id: "haaland", name: "Erling Haaland", teamId: "manCity", position: "ST", number: 9, nationality: "Norway", stats: { appearances: 28, goals: 25, xG: 22.1, assists: 4, xA: 3.2, shotsOnTargetPer90: 2.1, foulsCommittedPer90: 0.7, yellowCards: 3, redCards: 0, minutesPlayed: 2380 } },
  kdb: { id: "kdb", name: "Kevin De Bruyne", teamId: "manCity", position: "CAM", number: 17, nationality: "Belgium", stats: { appearances: 22, goals: 6, xG: 5.2, assists: 14, xA: 12.5, shotsOnTargetPer90: 1.0, foulsCommittedPer90: 0.8, yellowCards: 2, redCards: 0, minutesPlayed: 1760 } },
  foden: { id: "foden", name: "Phil Foden", teamId: "manCity", position: "LW", number: 47, nationality: "England", stats: { appearances: 26, goals: 10, xG: 8.9, assists: 8, xA: 7.1, shotsOnTargetPer90: 1.5, foulsCommittedPer90: 0.6, yellowCards: 2, redCards: 0, minutesPlayed: 2100 } },
  rodri: { id: "rodri", name: "Rodri", teamId: "manCity", position: "CDM", number: 16, nationality: "Spain", stats: { appearances: 27, goals: 4, xG: 3.1, assists: 6, xA: 4.8, shotsOnTargetPer90: 0.5, foulsCommittedPer90: 1.6, yellowCards: 7, redCards: 0, minutesPlayed: 2430 } },
  dias: { id: "dias", name: "Rúben Dias", teamId: "manCity", position: "CB", number: 3, nationality: "Portugal", stats: { appearances: 28, goals: 1, xG: 1.2, assists: 1, xA: 0.5, shotsOnTargetPer90: 0.2, foulsCommittedPer90: 0.9, yellowCards: 4, redCards: 0, minutesPlayed: 2500 } },
  ederson: { id: "ederson", name: "Ederson", teamId: "manCity", position: "GK", number: 31, nationality: "Brazil", stats: { appearances: 28, goals: 0, xG: 0, assists: 1, xA: 0.8, shotsOnTargetPer90: 0, foulsCommittedPer90: 0.1, yellowCards: 1, redCards: 0, minutesPlayed: 2520 } },

  salah: { id: "salah", name: "Mohamed Salah", teamId: "liverpool", position: "RW", number: 11, nationality: "Egypt", stats: { appearances: 28, goals: 18, xG: 15.6, assists: 12, xA: 10.1, shotsOnTargetPer90: 1.9, foulsCommittedPer90: 0.5, yellowCards: 1, redCards: 0, minutesPlayed: 2420 } },
  nunez: { id: "nunez", name: "Darwin Núñez", teamId: "liverpool", position: "ST", number: 9, nationality: "Uruguay", stats: { appearances: 25, goals: 11, xG: 13.2, assists: 3, xA: 2.5, shotsOnTargetPer90: 1.6, foulsCommittedPer90: 1.2, yellowCards: 5, redCards: 1, minutesPlayed: 1800 } },
  macallister: { id: "macallister", name: "Alexis Mac Allister", teamId: "liverpool", position: "CM", number: 10, nationality: "Argentina", stats: { appearances: 27, goals: 5, xG: 4.1, assists: 6, xA: 5.3, shotsOnTargetPer90: 0.8, foulsCommittedPer90: 1.4, yellowCards: 6, redCards: 0, minutesPlayed: 2290 } },
  szoboszlai: { id: "szoboszlai", name: "Dominik Szoboszlai", teamId: "liverpool", position: "CAM", number: 8, nationality: "Hungary", stats: { appearances: 26, goals: 4, xG: 3.5, assists: 5, xA: 4.8, shotsOnTargetPer90: 0.9, foulsCommittedPer90: 1.3, yellowCards: 5, redCards: 0, minutesPlayed: 2050 } },
  virgil: { id: "virgil", name: "Virgil van Dijk", teamId: "liverpool", position: "CB", number: 4, nationality: "Netherlands", stats: { appearances: 29, goals: 3, xG: 2.8, assists: 1, xA: 0.6, shotsOnTargetPer90: 0.3, foulsCommittedPer90: 0.7, yellowCards: 4, redCards: 0, minutesPlayed: 2610 } },
  alisson: { id: "alisson", name: "Alisson Becker", teamId: "liverpool", position: "GK", number: 1, nationality: "Brazil", stats: { appearances: 27, goals: 0, xG: 0, assists: 1, xA: 0.5, shotsOnTargetPer90: 0, foulsCommittedPer90: 0, yellowCards: 0, redCards: 0, minutesPlayed: 2430 } },

  son: { id: "son", name: "Son Heung-min", teamId: "tottenham", position: "LW", number: 7, nationality: "South Korea", stats: { appearances: 28, goals: 15, xG: 12.8, assists: 7, xA: 6.2, shotsOnTargetPer90: 1.7, foulsCommittedPer90: 0.6, yellowCards: 2, redCards: 0, minutesPlayed: 2380 } },
  maddison: { id: "maddison", name: "James Maddison", teamId: "tottenham", position: "CAM", number: 10, nationality: "England", stats: { appearances: 25, goals: 7, xG: 5.9, assists: 8, xA: 7.4, shotsOnTargetPer90: 1.1, foulsCommittedPer90: 1.0, yellowCards: 4, redCards: 0, minutesPlayed: 2050 } },

  palmer: { id: "palmer", name: "Cole Palmer", teamId: "chelsea", position: "RW", number: 20, nationality: "England", stats: { appearances: 28, goals: 19, xG: 16.5, assists: 10, xA: 8.8, shotsOnTargetPer90: 2.0, foulsCommittedPer90: 0.4, yellowCards: 1, redCards: 0, minutesPlayed: 2450 } },
  jackson: { id: "jackson", name: "Nicolas Jackson", teamId: "chelsea", position: "ST", number: 15, nationality: "Senegal", stats: { appearances: 27, goals: 12, xG: 10.5, assists: 5, xA: 4.1, shotsOnTargetPer90: 1.3, foulsCommittedPer90: 1.1, yellowCards: 5, redCards: 0, minutesPlayed: 2160 } },

  isak: { id: "isak", name: "Alexander Isak", teamId: "newcastle", position: "ST", number: 14, nationality: "Sweden", stats: { appearances: 27, goals: 17, xG: 14.8, assists: 5, xA: 4.0, shotsOnTargetPer90: 1.8, foulsCommittedPer90: 0.5, yellowCards: 2, redCards: 0, minutesPlayed: 2300 } },
  gordon: { id: "gordon", name: "Anthony Gordon", teamId: "newcastle", position: "LW", number: 10, nationality: "England", stats: { appearances: 28, goals: 9, xG: 7.5, assists: 8, xA: 7.0, shotsOnTargetPer90: 1.1, foulsCommittedPer90: 1.0, yellowCards: 4, redCards: 0, minutesPlayed: 2350 } },

  rashford: { id: "rashford", name: "Marcus Rashford", teamId: "manUtd", position: "LW", number: 10, nationality: "England", stats: { appearances: 24, goals: 7, xG: 8.2, assists: 3, xA: 3.8, shotsOnTargetPer90: 1.2, foulsCommittedPer90: 0.8, yellowCards: 3, redCards: 0, minutesPlayed: 1800 } },
  bruno: { id: "bruno", name: "Bruno Fernandes", teamId: "manUtd", position: "CAM", number: 8, nationality: "Portugal", stats: { appearances: 29, goals: 8, xG: 7.1, assists: 7, xA: 8.5, shotsOnTargetPer90: 1.0, foulsCommittedPer90: 1.3, yellowCards: 8, redCards: 0, minutesPlayed: 2580 } },

  watkins: { id: "watkins", name: "Ollie Watkins", teamId: "astonVilla", position: "ST", number: 11, nationality: "England", stats: { appearances: 28, goals: 13, xG: 11.4, assists: 8, xA: 7.2, shotsOnTargetPer90: 1.4, foulsCommittedPer90: 0.9, yellowCards: 3, redCards: 0, minutesPlayed: 2400 } },

  bowen: { id: "bowen", name: "Jarrod Bowen", teamId: "westHam", position: "RW", number: 20, nationality: "England", stats: { appearances: 27, goals: 8, xG: 7.3, assists: 6, xA: 5.8, shotsOnTargetPer90: 1.3, foulsCommittedPer90: 0.7, yellowCards: 3, redCards: 0, minutesPlayed: 2250 } },

  mitoma: { id: "mitoma", name: "Kaoru Mitoma", teamId: "brighton", position: "LW", number: 22, nationality: "Japan", stats: { appearances: 24, goals: 7, xG: 5.8, assists: 5, xA: 4.5, shotsOnTargetPer90: 1.0, foulsCommittedPer90: 0.6, yellowCards: 2, redCards: 0, minutesPlayed: 1900 } },
};

// ===================== REFEREES =====================
export const refereesData: Record<string, Referee> = {
  "michael-oliver": { id: "michael-oliver", name: "Michael Oliver", matchesOfficiated: 25, results: { homeWins: 11, awayWins: 8, draws: 6 }, discipline: { avgYellowPerGame: 4.2, totalYellows: 105, totalReds: 3, foulsPerTackle: 0.32 } },
  "anthony-taylor": { id: "anthony-taylor", name: "Anthony Taylor", matchesOfficiated: 23, results: { homeWins: 10, awayWins: 7, draws: 6 }, discipline: { avgYellowPerGame: 4.8, totalYellows: 110, totalReds: 5, foulsPerTackle: 0.35 } },
  "craig-pawson": { id: "craig-pawson", name: "Craig Pawson", matchesOfficiated: 20, results: { homeWins: 9, awayWins: 6, draws: 5 }, discipline: { avgYellowPerGame: 3.6, totalYellows: 72, totalReds: 1, foulsPerTackle: 0.28 } },
  "simon-hooper": { id: "simon-hooper", name: "Simon Hooper", matchesOfficiated: 18, results: { homeWins: 8, awayWins: 5, draws: 5 }, discipline: { avgYellowPerGame: 3.9, totalYellows: 70, totalReds: 2, foulsPerTackle: 0.30 } },
  "robert-jones": { id: "robert-jones", name: "Robert Jones", matchesOfficiated: 16, results: { homeWins: 7, awayWins: 5, draws: 4 }, discipline: { avgYellowPerGame: 4.1, totalYellows: 66, totalReds: 2, foulsPerTackle: 0.31 } },
};

// Helper to get referee name from id
export function getRefereeName(id: string): string {
  return refereesData[id]?.name ?? id;
}

// ===================== MATCHES =====================
export const matches: Match[] = [
  {
    id: "1", homeTeam: teamsData.arsenal, awayTeam: teamsData.manCity,
    date: "2026-03-21", time: "15:00", stadium: "Emirates Stadium", refereeId: "michael-oliver",
    prediction: { homeWin: 0.42, draw: 0.28, awayWin: 0.30 }, status: "upcoming",
    markets: [
      { category: "match-odds", name: "Match Winner", prediction: "Arsenal Win", odds: 2.40, fairOdds: 2.38, confidence: 78, edge: 4.2 },
      { category: "match-odds", name: "Asian Handicap", prediction: "Arsenal -0.5", odds: 2.55, fairOdds: 2.50, confidence: 72, edge: 3.1 },
      { category: "goals", name: "Over/Under 2.5", prediction: "Over 2.5 Goals", odds: 1.85, fairOdds: 1.72, confidence: 82, edge: 7.6 },
      { category: "goals", name: "BTTS", prediction: "Yes", odds: 1.72, fairOdds: 1.65, confidence: 80, edge: 5.8 },
      { category: "player-props", name: "Saka Shots on Target", prediction: "Over 0.5 SoT", odds: 1.55, fairOdds: 1.40, confidence: 85, edge: 10.7 },
      { category: "player-props", name: "Haaland Anytime Scorer", prediction: "Yes", odds: 2.20, fairOdds: 2.10, confidence: 68, edge: 4.8 },
      { category: "cards-corners", name: "Total Cards", prediction: "Over 3.5", odds: 1.80, fairOdds: 1.70, confidence: 76, edge: 5.9 },
      { category: "cards-corners", name: "Total Corners", prediction: "Over 9.5", odds: 1.90, fairOdds: 1.82, confidence: 71, edge: 4.4 },
    ],
  },
  {
    id: "2", homeTeam: teamsData.liverpool, awayTeam: teamsData.chelsea,
    date: "2026-03-21", time: "17:30", stadium: "Anfield", refereeId: "anthony-taylor",
    prediction: { homeWin: 0.55, draw: 0.24, awayWin: 0.21 }, status: "upcoming",
    markets: [
      { category: "match-odds", name: "Match Winner", prediction: "Liverpool Win", odds: 1.75, fairOdds: 1.82, confidence: 84, edge: 3.9 },
      { category: "goals", name: "Over/Under 2.5", prediction: "Over 2.5 Goals", odds: 1.80, fairOdds: 1.70, confidence: 79, edge: 5.9 },
      { category: "player-props", name: "Salah Anytime Scorer", prediction: "Yes", odds: 2.10, fairOdds: 1.95, confidence: 74, edge: 7.7 },
      { category: "cards-corners", name: "Total Cards", prediction: "Over 4.5", odds: 2.10, fairOdds: 1.95, confidence: 73, edge: 7.7 },
    ],
  },
  {
    id: "3", homeTeam: teamsData.tottenham, awayTeam: teamsData.manUtd,
    date: "2026-03-22", time: "14:00", stadium: "Tottenham Hotspur Stadium", refereeId: "craig-pawson",
    prediction: { homeWin: 0.45, draw: 0.27, awayWin: 0.28 }, status: "upcoming",
    markets: [
      { category: "match-odds", name: "Match Winner", prediction: "Tottenham Win", odds: 2.20, fairOdds: 2.22, confidence: 70, edge: 0.9 },
      { category: "goals", name: "Over/Under 2.5", prediction: "Under 2.5 Goals", odds: 2.05, fairOdds: 1.95, confidence: 65, edge: 5.1 },
      { category: "player-props", name: "Son Anytime Scorer", prediction: "Yes", odds: 2.80, fairOdds: 2.60, confidence: 62, edge: 7.7 },
      { category: "cards-corners", name: "Total Corners", prediction: "Over 10.5", odds: 2.00, fairOdds: 1.88, confidence: 68, edge: 6.4 },
    ],
  },
  {
    id: "4", homeTeam: teamsData.newcastle, awayTeam: teamsData.brighton,
    date: "2026-03-22", time: "16:30", stadium: "St James' Park", refereeId: "simon-hooper",
    prediction: { homeWin: 0.50, draw: 0.26, awayWin: 0.24 }, status: "upcoming",
    markets: [
      { category: "match-odds", name: "Match Winner", prediction: "Newcastle Win", odds: 1.95, fairOdds: 2.00, confidence: 75, edge: 2.5 },
      { category: "goals", name: "BTTS", prediction: "Yes", odds: 1.80, fairOdds: 1.72, confidence: 77, edge: 4.7 },
      { category: "cards-corners", name: "Total Cards", prediction: "Over 3.5", odds: 1.85, fairOdds: 1.78, confidence: 72, edge: 3.9 },
    ],
  },
  {
    id: "5", homeTeam: teamsData.astonVilla, awayTeam: teamsData.westHam,
    date: "2026-03-23", time: "15:00", stadium: "Villa Park", refereeId: "robert-jones",
    prediction: { homeWin: 0.52, draw: 0.25, awayWin: 0.23 }, status: "upcoming",
    markets: [
      { category: "match-odds", name: "Match Winner", prediction: "Aston Villa Win", odds: 1.85, fairOdds: 1.92, confidence: 76, edge: 3.7 },
      { category: "goals", name: "Over/Under 2.5", prediction: "Over 2.5 Goals", odds: 1.90, fairOdds: 1.80, confidence: 73, edge: 5.6 },
    ],
  },
];

export const hotPicks: MarketPrediction[] = [
  { category: "player-props", name: "Saka Más 0.5 Tiros", prediction: "Arsenal vs Man City", odds: 1.55, fairOdds: 1.40, confidence: 85, edge: 10.7 },
  { category: "goals", name: "Más 2.5 Goles", prediction: "Arsenal vs Man City", odds: 1.85, fairOdds: 1.72, confidence: 82, edge: 7.6 },
  { category: "player-props", name: "Salah Anota (90')", prediction: "Liverpool vs Chelsea", odds: 2.10, fairOdds: 1.95, confidence: 74, edge: 7.7 },
  { category: "cards-corners", name: "Más 4.5 Tarjetas", prediction: "Liverpool vs Chelsea", odds: 2.10, fairOdds: 1.95, confidence: 73, edge: 7.7 },
  { category: "goals", name: "Ambos Marcan (Sí)", prediction: "Newcastle vs Brighton", odds: 1.80, fairOdds: 1.72, confidence: 77, edge: 4.7 },
];

export const botStats: BotStats = {
  totalPredictions: 1247,
  winRate: 67.3,
  roi: 12.8,
  totalProfit: 3842,
  streak: 5,
};

export const performanceHistory: HistoryEntry[] = [
  { id: "h1", date: "2026-03-18", match: "Arsenal 2-1 Brighton", market: "Match Winner", prediction: "Arsenal Win", odds: 1.65, stake: 10, result: "won", profit: 6.50 },
  { id: "h2", date: "2026-03-18", match: "Arsenal 2-1 Brighton", market: "Over 2.5 Goals", prediction: "Over 2.5", odds: 1.90, stake: 10, result: "won", profit: 9.00 },
  { id: "h3", date: "2026-03-17", match: "Man City 3-0 West Ham", market: "Haaland Scorer", prediction: "Yes", odds: 1.80, stake: 10, result: "won", profit: 8.00 },
  { id: "h4", date: "2026-03-17", match: "Man City 3-0 West Ham", market: "Over 3.5 Cards", prediction: "Over 3.5", odds: 1.75, stake: 10, result: "lost", profit: -10 },
  { id: "h5", date: "2026-03-16", match: "Liverpool 1-1 Tottenham", market: "BTTS", prediction: "Yes", odds: 1.72, stake: 10, result: "won", profit: 7.20 },
  { id: "h6", date: "2026-03-16", match: "Liverpool 1-1 Tottenham", market: "Match Winner", prediction: "Liverpool", odds: 1.55, stake: 10, result: "lost", profit: -10 },
  { id: "h7", date: "2026-03-15", match: "Chelsea 2-0 Newcastle", market: "Under 2.5", prediction: "Under 2.5", odds: 2.00, stake: 10, result: "won", profit: 10.00 },
  { id: "h8", date: "2026-03-14", match: "Man Utd 1-2 Aston Villa", market: "Aston Villa Win", prediction: "Away Win", odds: 3.10, stake: 10, result: "won", profit: 21.00 },
  { id: "h9", date: "2026-03-13", match: "Brighton 0-0 Tottenham", market: "BTTS", prediction: "Yes", odds: 1.65, stake: 10, result: "lost", profit: -10 },
  { id: "h10", date: "2026-03-12", match: "Arsenal 1-0 Liverpool", market: "Under 2.5", prediction: "Under 2.5", odds: 2.15, stake: 10, result: "won", profit: 11.50 },
];

export const profitChartData = [
  { date: "Mar 1", profit: 0, cumulative: 0 },
  { date: "Mar 3", profit: 15, cumulative: 15 },
  { date: "Mar 5", profit: -10, cumulative: 5 },
  { date: "Mar 7", profit: 22, cumulative: 27 },
  { date: "Mar 9", profit: 8, cumulative: 35 },
  { date: "Mar 11", profit: -5, cumulative: 30 },
  { date: "Mar 12", profit: 11.5, cumulative: 41.5 },
  { date: "Mar 13", profit: -10, cumulative: 31.5 },
  { date: "Mar 14", profit: 21, cumulative: 52.5 },
  { date: "Mar 15", profit: 10, cumulative: 62.5 },
  { date: "Mar 16", profit: -2.8, cumulative: 59.7 },
  { date: "Mar 17", profit: -2, cumulative: 57.7 },
  { date: "Mar 18", profit: 15.5, cumulative: 73.2 },
];

// ===================== HISTORICAL SEASONS =====================
export interface SeasonSummary {
  season: string;
  totalPredictions: number;
  wins: number;
  losses: number;
  winRate: number;
  roi: number;
  totalProfit: number;
  bestMonth: string;
  worstMonth: string;
  avgOdds: number;
  topMarket: string;
  topMarketWinRate: number;
}

export interface MonthlyPerformance {
  month: string;
  predictions: number;
  wins: number;
  losses: number;
  profit: number;
  cumulative: number;
  roi: number;
}

export interface SeasonData {
  summary: SeasonSummary;
  monthly: MonthlyPerformance[];
  highlights: HistoryEntry[];
}

export const historicalSeasons: Record<string, SeasonData> = {
  "2025-26": {
    summary: {
      season: "2025-26", totalPredictions: 412, wins: 277, losses: 135, winRate: 67.3, roi: 12.8,
      totalProfit: 842, bestMonth: "January", worstMonth: "November", avgOdds: 1.92, topMarket: "Over/Under Goals", topMarketWinRate: 72.1,
    },
    monthly: [
      { month: "Aug 25", predictions: 38, wins: 24, losses: 14, profit: 52, cumulative: 52, roi: 10.5 },
      { month: "Sep 25", predictions: 42, wins: 30, losses: 12, profit: 98, cumulative: 150, roi: 15.2 },
      { month: "Oct 25", predictions: 48, wins: 31, losses: 17, profit: 65, cumulative: 215, roi: 11.8 },
      { month: "Nov 25", predictions: 45, wins: 27, losses: 18, profit: -15, cumulative: 200, roi: -2.1 },
      { month: "Dec 25", predictions: 55, wins: 38, losses: 17, profit: 125, cumulative: 325, roi: 14.3 },
      { month: "Jan 26", predictions: 50, wins: 37, losses: 13, profit: 185, cumulative: 510, roi: 22.5 },
      { month: "Feb 26", predictions: 46, wins: 32, losses: 14, profit: 110, cumulative: 620, roi: 16.8 },
      { month: "Mar 26", predictions: 88, wins: 58, losses: 30, profit: 222, cumulative: 842, roi: 12.8 },
    ],
    highlights: [
      { id: "s1", date: "2026-01-15", match: "Arsenal 3-2 Man City", market: "BTTS + Over 2.5", prediction: "Yes", odds: 2.50, stake: 20, result: "won", profit: 30 },
      { id: "s2", date: "2025-12-26", match: "Liverpool 4-1 Leicester", market: "Liverpool -1.5 AH", prediction: "Liverpool", odds: 2.10, stake: 15, result: "won", profit: 16.50 },
      { id: "s3", date: "2026-02-08", match: "Chelsea 0-1 Newcastle", market: "Under 1.5 Goals", prediction: "Under 1.5", odds: 3.40, stake: 10, result: "won", profit: 24 },
    ],
  },
  "2024-25": {
    summary: {
      season: "2024-25", totalPredictions: 520, wins: 341, losses: 179, winRate: 65.6, roi: 11.2,
      totalProfit: 1580, bestMonth: "March", worstMonth: "September", avgOdds: 1.88, topMarket: "Match Winner", topMarketWinRate: 70.5,
    },
    monthly: [
      { month: "Aug 24", predictions: 40, wins: 25, losses: 15, profit: 42, cumulative: 42, roi: 8.5 },
      { month: "Sep 24", predictions: 48, wins: 28, losses: 20, profit: -25, cumulative: 17, roi: -4.2 },
      { month: "Oct 24", predictions: 52, wins: 35, losses: 17, profit: 88, cumulative: 105, roi: 12.1 },
      { month: "Nov 24", predictions: 50, wins: 33, losses: 17, profit: 72, cumulative: 177, roi: 10.5 },
      { month: "Dec 24", predictions: 60, wins: 42, losses: 18, profit: 165, cumulative: 342, roi: 16.2 },
      { month: "Jan 25", predictions: 55, wins: 38, losses: 17, profit: 142, cumulative: 484, roi: 15.8 },
      { month: "Feb 25", predictions: 50, wins: 34, losses: 16, profit: 118, cumulative: 602, roi: 14.2 },
      { month: "Mar 25", predictions: 55, wins: 40, losses: 15, profit: 210, cumulative: 812, roi: 22.8 },
      { month: "Apr 25", predictions: 52, wins: 33, losses: 19, profit: 85, cumulative: 897, roi: 9.8 },
      { month: "May 25", predictions: 58, wins: 33, losses: 25, profit: 683, cumulative: 1580, roi: 8.2 },
    ],
    highlights: [
      { id: "s4", date: "2025-03-22", match: "Man City 2-3 Arsenal", market: "Arsenal Win", prediction: "Arsenal", odds: 3.80, stake: 15, result: "won", profit: 42 },
      { id: "s5", date: "2024-12-21", match: "Liverpool 5-0 West Ham", market: "Over 3.5 Goals", prediction: "Over 3.5", odds: 2.30, stake: 20, result: "won", profit: 26 },
      { id: "s6", date: "2025-04-05", match: "Tottenham 1-0 Chelsea", market: "Under 2.5 + Tottenham Win", prediction: "Yes", odds: 4.20, stake: 10, result: "won", profit: 32 },
    ],
  },
  "2023-24": {
    summary: {
      season: "2023-24", totalPredictions: 485, wins: 306, losses: 179, winRate: 63.1, roi: 9.5,
      totalProfit: 1120, bestMonth: "April", worstMonth: "August", avgOdds: 1.85, topMarket: "BTTS", topMarketWinRate: 68.3,
    },
    monthly: [
      { month: "Aug 23", predictions: 35, wins: 19, losses: 16, profit: -18, cumulative: -18, roi: -4.1 },
      { month: "Sep 23", predictions: 42, wins: 26, losses: 16, profit: 55, cumulative: 37, roi: 10.2 },
      { month: "Oct 23", predictions: 48, wins: 30, losses: 18, profit: 72, cumulative: 109, roi: 11.5 },
      { month: "Nov 23", predictions: 45, wins: 29, losses: 16, profit: 68, cumulative: 177, roi: 11.8 },
      { month: "Dec 23", predictions: 58, wins: 38, losses: 20, profit: 110, cumulative: 287, roi: 12.5 },
      { month: "Jan 24", predictions: 50, wins: 33, losses: 17, profit: 95, cumulative: 382, roi: 13.2 },
      { month: "Feb 24", predictions: 48, wins: 30, losses: 18, profit: 78, cumulative: 460, roi: 11.0 },
      { month: "Mar 24", predictions: 52, wins: 34, losses: 18, profit: 125, cumulative: 585, roi: 15.5 },
      { month: "Apr 24", predictions: 55, wins: 40, losses: 15, profit: 235, cumulative: 820, roi: 25.2 },
      { month: "May 24", predictions: 52, wins: 27, losses: 25, profit: 300, cumulative: 1120, roi: 5.8 },
    ],
    highlights: [
      { id: "s7", date: "2024-04-14", match: "Arsenal 3-1 Aston Villa", market: "Arsenal -1 AH", prediction: "Arsenal", odds: 2.40, stake: 20, result: "won", profit: 28 },
      { id: "s8", date: "2024-02-11", match: "Man City 1-1 Chelsea", market: "BTTS", prediction: "Yes", odds: 1.65, stake: 25, result: "won", profit: 16.25 },
      { id: "s9", date: "2023-12-30", match: "Liverpool 2-0 Newcastle", market: "Liverpool Clean Sheet", prediction: "Yes", odds: 2.80, stake: 10, result: "won", profit: 18 },
    ],
  },
  "2022-23": {
    summary: {
      season: "2022-23", totalPredictions: 430, wins: 258, losses: 172, winRate: 60.0, roi: 7.2,
      totalProfit: 680, bestMonth: "February", worstMonth: "October", avgOdds: 1.82, topMarket: "Over/Under Goals", topMarketWinRate: 66.0,
    },
    monthly: [
      { month: "Aug 22", predictions: 32, wins: 18, losses: 14, profit: 15, cumulative: 15, roi: 3.8 },
      { month: "Sep 22", predictions: 38, wins: 22, losses: 16, profit: 32, cumulative: 47, roi: 6.5 },
      { month: "Oct 22", predictions: 42, wins: 22, losses: 20, profit: -30, cumulative: 17, roi: -5.8 },
      { month: "Nov 22", predictions: 20, wins: 12, losses: 8, profit: 28, cumulative: 45, roi: 10.5 },
      { month: "Dec 22", predictions: 48, wins: 30, losses: 18, profit: 82, cumulative: 127, roi: 12.8 },
      { month: "Jan 23", predictions: 50, wins: 32, losses: 18, profit: 95, cumulative: 222, roi: 13.5 },
      { month: "Feb 23", predictions: 45, wins: 32, losses: 13, profit: 155, cumulative: 377, roi: 22.0 },
      { month: "Mar 23", predictions: 50, wins: 30, losses: 20, profit: 68, cumulative: 445, roi: 9.8 },
      { month: "Apr 23", predictions: 52, wins: 32, losses: 20, profit: 95, cumulative: 540, roi: 12.2 },
      { month: "May 23", predictions: 53, wins: 28, losses: 25, profit: 140, cumulative: 680, roi: 4.5 },
    ],
    highlights: [
      { id: "s10", date: "2023-02-18", match: "Arsenal 1-1 Man City", market: "BTTS + Under 3.5", prediction: "Yes", odds: 2.60, stake: 15, result: "won", profit: 24 },
      { id: "s11", date: "2023-04-01", match: "Newcastle 2-0 Man Utd", market: "Newcastle Win", prediction: "Newcastle", odds: 2.20, stake: 20, result: "won", profit: 24 },
    ],
  },
};

// All-time cumulative profit by season for the overview chart
export const allTimeProfitData = [
  { season: "22-23", profit: 680, roi: 7.2, winRate: 60.0 },
  { season: "23-24", profit: 1120, roi: 9.5, winRate: 63.1 },
  { season: "24-25", profit: 1580, roi: 11.2, winRate: 65.6 },
  { season: "25-26", profit: 842, roi: 12.8, winRate: 67.3 },
];

