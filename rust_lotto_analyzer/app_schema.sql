CREATE TABLE draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL,
    numbers TEXT NOT NULL,
    game_type TEXT NOT NULL
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE number_frequency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    number INTEGER NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, number)
);
CREATE TABLE pair_frequency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    number1 INTEGER NOT NULL,
    number2 INTEGER NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, number1, number2)
);
