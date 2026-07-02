-- schema.sql

-- Tabla maestra de partidos
CREATE TABLE IF NOT EXISTS matches (
    game_id         TEXT PRIMARY KEY,
    season          INTEGER NOT NULL,        -- ej: 2023 = temporada 2023/24
    date            DATE,
    home_team       TEXT,
    away_team       TEXT,
    home_score      INTEGER,
    away_score      INTEGER,
    home_xg         FLOAT,
    away_xg         FLOAT,
    referee         TEXT,
    venue           TEXT,
    attendance      INTEGER,
    home_formation  TEXT,
    away_formation  TEXT,
    matchweek       INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Alineaciones por partido
CREATE TABLE IF NOT EXISTS lineups (
    id              SERIAL PRIMARY KEY,
    game_id         TEXT REFERENCES matches(game_id),
    season          INTEGER,
    team            TEXT,
    player          TEXT,
    jersey_number   INTEGER,
    position        TEXT,
    is_starter      BOOLEAN,
    minutes_played  INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (game_id, team, player)
);

-- Stats de jugador por partido (summary, shooting, passing, etc.)
CREATE TABLE IF NOT EXISTS player_match_stats (
    id              SERIAL PRIMARY KEY,
    game_id         TEXT REFERENCES matches(game_id),
    season          INTEGER,
    team            TEXT,
    player          TEXT,
    stat_type       TEXT,       -- 'summary' | 'shooting' | 'passing' | etc.
    data            JSONB,      -- todas las columnas del stat_type
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (game_id, team, player, stat_type)
);

-- Eventos por partido (goles, tarjetas, subs)
CREATE TABLE IF NOT EXISTS match_events (
    id              SERIAL PRIMARY KEY,
    game_id         TEXT REFERENCES matches(game_id),
    season          INTEGER,
    team            TEXT,
    minute          INTEGER,
    event_type      TEXT,       -- 'goal' | 'yellow_card' | 'red_card' | 'sub'
    player1         TEXT,
    player2         TEXT,       -- asistencia o jugador que sale (en subs)
    score           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Disparos por partido con xG individual
CREATE TABLE IF NOT EXISTS shot_events (
    id              SERIAL PRIMARY KEY,
    game_id         TEXT REFERENCES matches(game_id),
    season          INTEGER,
    team            TEXT,
    minute          INTEGER,
    player          TEXT,
    xg              FLOAT,
    psxg            FLOAT,
    outcome         TEXT,
    distance        FLOAT,
    body_part       TEXT,
    sca1_player     TEXT,
    sca1_type       TEXT,
    sca2_player     TEXT,
    sca2_type       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Índices de performance para queries de predicción
CREATE INDEX IF NOT EXISTS idx_matches_season   ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_teams    ON matches(home_team, away_team);
CREATE INDEX IF NOT EXISTS idx_matches_referee  ON matches(referee);
CREATE INDEX IF NOT EXISTS idx_lineups_game     ON lineups(game_id);
CREATE INDEX IF NOT EXISTS idx_shots_game       ON shot_events(game_id);
CREATE INDEX IF NOT EXISTS idx_events_game      ON match_events(game_id);
CREATE INDEX IF NOT EXISTS idx_pms_game_player  ON player_match_stats(game_id, player);
