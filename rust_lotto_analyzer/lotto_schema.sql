CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT NOT NULL,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        );
CREATE INDEX idx_draws_game_date ON draws(game, draw_date);
