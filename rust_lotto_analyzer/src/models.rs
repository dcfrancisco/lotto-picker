use chrono::NaiveDate;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Draw {
    pub id: i64,
    pub game: String,
    pub draw_date: NaiveDate,
    pub numbers: Vec<u8>,
}
