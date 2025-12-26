pub fn is_draws_table_empty(db_path: &str) -> anyhow::Result<bool> {
    let conn = Connection::open(db_path)?;
    let mut stmt = conn.prepare("SELECT COUNT(*) FROM draws")?;
    let count: i64 = stmt.query_row([], |row| row.get(0))?;
    Ok(count == 0)
}
pub fn recreate_db(db_path: &str) -> anyhow::Result<()> {
    let mut conn = Connection::open(db_path)?;
    conn.execute_batch(
        "DROP TABLE IF EXISTS draws;"
    )?;
    init_db(db_path)?;
    Ok(())
}

use crate::models::Draw;
use rusqlite::{params, Connection};
use chrono::NaiveDate;
use serde::Deserialize;

pub fn init_db(db_path: &str) -> anyhow::Result<()> {
    let conn = Connection::open(db_path)?;
    conn.execute_batch(
        "CREATE TABLE IF NOT EXISTS draws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT NOT NULL,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_draws_game_date ON draws(game, draw_date);"
    )?;
    Ok(())
}

pub fn import_csv_if_needed(db_path: &str, csv_path: &str) -> anyhow::Result<()> {
    let mut conn = Connection::open(db_path)?;
    let mut rdr = csv::Reader::from_path(csv_path)?;
    let mut count = 0;
    let tx = conn.transaction()?;
    for result in rdr.deserialize() {
        let record: CsvDraw = result?;
        let numbers = record.combinations.replace('[', "").replace(']', "");
        // Check if this draw already exists (by game and draw_date)
        let mut stmt = tx.prepare("SELECT id, numbers FROM draws WHERE game = ?1 AND draw_date = ?2")?;
        let mut rows = stmt.query(params![record.game, record.drawDate])?;
        if let Some(row) = rows.next()? {
            let id: i64 = row.get(0)?;
            let existing_numbers: String = row.get(1)?;
            if existing_numbers != numbers {
                tx.execute(
                    "UPDATE draws SET numbers = ?1 WHERE id = ?2",
                    params![numbers, id],
                )?;
            }
        } else {
            tx.execute(
                "INSERT INTO draws (game, draw_date, numbers) VALUES (?1, ?2, ?3)",
                params![record.game, record.drawDate, numbers],
            )?;
        }
        count += 1;
        if count % 1000 == 0 {
            println!("Imported/updated {} rows...", count);
        }
    }
    tx.commit()?;
    println!("Import/update complete. Total rows processed: {}", count);
    Ok(())
}

#[derive(Debug, Deserialize)]
struct CsvDraw {
    game: String,
    drawDate: String,
    combinations: String,
}

pub fn get_draws(conn: &Connection, game: &str) -> anyhow::Result<Vec<Draw>> {
    let mut stmt = conn.prepare("SELECT id, game, draw_date, numbers FROM draws WHERE game = ?1")?;
    let draws = stmt.query_map(params![game], |row| {
        let numbers_str: String = row.get(3)?;
        let numbers: Vec<u8> = numbers_str
            .split(',')
            .filter_map(|s| s.trim().parse().ok())
            .collect();
        Ok(Draw {
            id: row.get(0)?,
            game: row.get(1)?,
            draw_date: NaiveDate::parse_from_str(&row.get::<_, String>(2)?, "%Y-%m-%d").unwrap_or(NaiveDate::from_ymd_opt(1970,1,1).unwrap()),
            numbers,
        })
    })?;
    Ok(draws.filter_map(Result::ok).collect())
}
