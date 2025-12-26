use clap::{Parser, ValueEnum};

#[derive(Parser, Debug)]
#[command(author, version, about)]
pub struct CliArgs {
    #[arg(long, default_value = "GRAND_LOTTO_6-55")]
    pub game: String,
    #[arg(long, value_enum, default_value = "top")]
    pub strategy: Strategy,
    #[arg(long, default_value_t = 5)]
    pub n_picks: usize,
    #[arg(long, default_value_t = 10)]
    pub top_n: usize,
    #[arg(long, default_value_t = 20)]
    pub hot_x: usize,
    #[arg(long, default_value_t = false)]
    pub show_freq: bool,
    #[arg(long, default_value_t = false)]
    pub simulate: bool,
    #[arg(long, default_value_t = false)]
    pub play: bool,
    #[arg(long, default_value_t = false)]
    pub recreate_db: bool,
}

#[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, ValueEnum, Debug)]
pub enum Strategy {
    Top,
    Cold,
    Hot,
    Random,
    Hybrid,
}
