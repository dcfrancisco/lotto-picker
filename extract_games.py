import csv
import json
import os

CSV_PATH = os.path.join('data', 'lotto_history.csv')
OUTPUT_PATH = 'games.json'

def extract_games(csv_path=CSV_PATH, output_path=OUTPUT_PATH):
    games = set()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            game = row.get('game')
            if game:
                games.add(game)
    games = sorted(games)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2)
    print(f"Extracted {len(games)} games to {output_path}")

if __name__ == '__main__':
    extract_games()