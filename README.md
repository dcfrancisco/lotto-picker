# Lotto Analyzer & Smart Picker

A Python tool for analyzing Philippine lotto draw data (6/55 and others), generating smart number picks, and visualizing trends.

## Features
- Load and clean historical lotto data from CSV
- Analyze number frequency, gaps, and hot/cold trends
- Generate smart picks (top, cold, hot, random, hybrid)
- Match checker: compare picks against history
- Visualize frequency (bar chart) and co-occurrence (heatmap)
- Simulate win rate over time
- CLI flags for strategy, game, export, and visualization

## Usage
1. **Install dependencies:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run analyzer:**
   ```sh
   python lotto_analyzer.py --game GRAND_LOTTO_6-55 --strategy top --n_picks 5 --show-freq --plot-freq --simulate
   ```
   - Use `--game` to select a lotto game (see `games.json` for options)
   - Use `--strategy` to pick number selection method
   - Use `--plot-freq` for bar chart, `--heatmap` for co-occurrence heatmap
   - Use `--simulate` to test picks against history
   - Use `--export json|csv` to save results

## Example
```
python lotto_analyzer.py --game GRAND_LOTTO_6-55 --strategy top --n_picks 5 --show-freq --plot-freq --simulate
```

## Data
- Place your CSV data in `data/lotto_history.csv` (see sample format in repo)
- To list all available games:
  ```sh
  python extract_games.py
  cat games.json
  ```

## Optional
- (Planned) GUI with Tkinter or web interface


## Statistical Disclaimer

**No strategy, including "hybrid" or "smart" picks, can increase your odds of winning in a fair 6/55 lottery. All strategies (top, cold, hot, random, hybrid) have the same statistical chance over time. This tool is for analysis and curiosity only, not for predicting or improving your chances of winning.**

## License
MIT
