mod models;
mod db;
mod logic;
mod cli;

use cli::CliArgs;
use clap::Parser;
use db::{init_db, import_csv_if_needed, recreate_db, is_draws_table_empty};
use logic::*;
use rusqlite::Connection;

fn main() -> anyhow::Result<()> {
    let args = CliArgs::parse();
    let db_path = "lotto.db";
    if args.recreate_db {
        println!("Recreating database...");
        recreate_db(db_path)?;
    } else {
        init_db(db_path)?;
    }
    if is_draws_table_empty(db_path)? {
        import_csv_if_needed(db_path, "../data/lotto_history.csv")?;
    } else {
        println!("Database already populated. Skipping CSV import.");
    }
    let conn = Connection::open(db_path)?;
    run_cli(&conn, &args)?;
    Ok(())
}
