

import os
import csv
import ast
import random
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt


CSV_PATH = os.path.join('data', 'lotto_history.csv')

# 1. Load and clean the CSV, filter by game, parse numbers from 'combinations'
def load_lotto_history(csv_path=CSV_PATH, game="GRAND_LOTTO_6-55"):
    draws = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('game') != game:
                continue
            try:
                # Try multiple date formats
                date_str = row['drawDate']
                for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%m-%d-%Y', '%Y-%d-%m'):
                    try:
                        draw_date = datetime.strptime(date_str, fmt)
                        break
                    except Exception:
                        continue
                else:
                    draw_date = date_str  # fallback: keep as string
                # Parse numbers from combinations column
                numbers = ast.literal_eval(row['combinations'])
                if isinstance(numbers, int):
                    numbers = [numbers]
                draws.append({'date': draw_date, 'numbers': numbers})
            except Exception as e:
                continue  # skip malformed rows
    return draws

# 2. Count frequency of each number (1–55)
def count_number_frequency(draws):
    freq = Counter()
    for draw in draws:
        freq.update(draw['numbers'])
    return freq

# 3. Generate picks based on strategy
def generate_picks(strategy, draws, n_picks=5, top_n=10, hot_x=20):
    freq = count_number_frequency(draws)
    all_numbers = list(range(1, 56))
    picks = []
    if strategy == 'top':
        top_numbers = [num for num, _ in freq.most_common(top_n)]
        for _ in range(n_picks):
            picks.append(sorted(random.sample(top_numbers, 6)))
    elif strategy == 'cold':
        cold_numbers = [num for num, _ in freq.most_common()[-top_n:]]
        for _ in range(n_picks):
            picks.append(sorted(random.sample(cold_numbers, 6)))
    elif strategy == 'hot':
        recent_draws = draws[-hot_x:]
        recent_freq = count_number_frequency(recent_draws)
        hot_numbers = [num for num, _ in recent_freq.most_common(top_n)]
        for _ in range(n_picks):
            picks.append(sorted(random.sample(hot_numbers, 6)))
    elif strategy == 'random':
        for _ in range(n_picks):
            picks.append(sorted(random.sample(all_numbers, 6)))
    elif strategy == 'hybrid':
        # 3 from top, 3 random
        top_numbers = [num for num, _ in freq.most_common(top_n)]
        for _ in range(n_picks):
            pick = random.sample(top_numbers, 3) + random.sample(all_numbers, 3)
            picks.append(sorted(set(pick)))
    else:
        raise ValueError('Unknown strategy')
    return picks

# 4. Match checker
def check_picks_against_history(picks, draws):
    results = []
    for pick in picks:
        best_match = 0
        match_dates = []
        exact_match = False
        for draw in draws:
            match_count = len(set(pick) & set(draw['numbers']))
            if match_count > best_match:
                best_match = match_count
                match_dates = [draw['date'].strftime('%Y-%m-%d')]
            elif match_count == best_match:
                match_dates.append(draw['date'].strftime('%Y-%m-%d'))
            if set(pick) == set(draw['numbers']):
                exact_match = True
        results.append({
            'pick': pick,
            'best_match': best_match,
            'match_dates': match_dates,
            'exact_match': exact_match
        })
    return results

def main():

    parser = argparse.ArgumentParser(description='Lotto Analyzer & Smart Picker (6/55)')
    parser.add_argument('--strategy', choices=['top', 'cold', 'hot', 'random', 'hybrid'], default='top', help='Strategy for number picking')
    parser.add_argument('--n_picks', type=int, default=5, help='Number of picks to generate')
    parser.add_argument('--top_n', type=int, default=10, help='Top N numbers for top/cold/hot strategies')
    parser.add_argument('--hot_x', type=int, default=20, help='Number of recent draws for hot strategy')
    parser.add_argument('--export', choices=['json', 'csv'], default=None, help='Export results to file')
    parser.add_argument('--show-freq', action='store_true', help='Show number frequency table')
    parser.add_argument('--game', type=str, default='GRAND_LOTTO_6-55', help='Game name to analyze (e.g., GRAND_LOTTO_6-55)')
    parser.add_argument('--plot-freq', action='store_true', help='Show bar chart of number frequencies')
    parser.add_argument('--simulate', action='store_true', help='Simulate win rate of generated picks over history')
    parser.add_argument('--heatmap', action='store_true', help='Show heatmap of number co-occurrence')
    parser.add_argument('--auto-best', action='store_true', help='Automatically find the best strategy and pick by simulation')
    parser.add_argument('--compare-strategies', action='store_true', help='Compare all strategies side by side')
    parser.add_argument('--play', action='store_true', help='Generate 10 balanced random lines (each number appears roughly equally)')
    args = parser.parse_args()

    if args.play:
        # Generate 10 lines, each with 6 unique numbers, all numbers 1-55 distributed as evenly as possible
        all_numbers = list(range(1, 56))
        picks = []
        pool = all_numbers * 1  # Start with 1 of each number
        random.shuffle(pool)
        for i in range(10):
            # If pool is too small, refill and shuffle
            if len(pool) < 6:
                pool += all_numbers
                random.shuffle(pool)
            pick = set()
            while len(pick) < 6:
                num = pool.pop()
                pick.add(num)
            picks.append(sorted(pick))
        print("\n-- PLAY MODE: 10 Balanced Random Lines --")
        for idx, pick in enumerate(picks, 1):
            print(f"Line {idx:2d}: {pick}")
        print("---------------------------------------\n")

        # Analysis: check each line against history
        draws = load_lotto_history(game=args.game)
        if not draws:
            print(f"No draws found for game: {args.game}")
            return
        results = check_picks_against_history(picks, draws)
        print("-- PLAY MODE ANALYSIS --")
        win_stats = {6: 0, 5: 0, 4: 0, 3: 0}
        for idx, res in enumerate(results, 1):
            print(f"Line {idx:2d}: Best match: {res['best_match']} | Dates: {res['match_dates'][:3]}{' ...' if len(res['match_dates'])>3 else ''} | Exact match: {res['exact_match']}")
            if res['best_match'] in win_stats:
                win_stats[res['best_match']] += 1
        print(f"Win Stats (across all lines): {win_stats}")
        print("---------------------------\n")
        return

    draws = load_lotto_history(game=args.game)

    if not draws:
        print(f"No draws found for game: {args.game}")
        return

    freq = count_number_frequency(draws)
    if args.show_freq:
        print("Number Frequency (1-55):")
        for num in range(1, 56):
            print(f"{num:2d}: {freq[num]}")
        print()
    if args.plot_freq:
        plt.figure(figsize=(12, 6))
        plt.bar(range(1, 56), [freq[n] for n in range(1, 56)], color='skyblue')
        plt.xlabel('Number')
        plt.ylabel('Frequency')
        plt.title(f'Number Frequency for {args.game}')
        plt.xticks(range(1, 56))
        plt.tight_layout()
        plt.show()

    if args.heatmap:
        import numpy as np
        co_matrix = np.zeros((55, 55), dtype=int)
        for draw in draws:
            nums = draw['numbers']
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    a, b = nums[i] - 1, nums[j] - 1
                    co_matrix[a, b] += 1
                    co_matrix[b, a] += 1
        plt.figure(figsize=(10, 8))
        plt.imshow(co_matrix, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Co-occurrence Count')
        plt.title(f'Number Co-occurrence Heatmap for {args.game}')
        plt.xlabel('Number')
        plt.ylabel('Number')
        plt.xticks(np.arange(0, 55), np.arange(1, 56))
        plt.yticks(np.arange(0, 55), np.arange(1, 56))
        plt.tight_layout()
        plt.show()

    if args.compare_strategies:
        strategies = ['top', 'cold', 'hot', 'random', 'hybrid']
        print("\n=== STRATEGY COMPARISON ===")
        for strategy in strategies:
            picks = generate_picks(strategy, draws, args.n_picks, args.top_n, args.hot_x)
            results = check_picks_against_history(picks, draws)
            win_stats = {6: 0, 5: 0, 4: 0, 3: 0}
            for draw in draws:
                draw_set = set(draw['numbers'])
                for pick in picks:
                    pick_set = set(pick)
                    match_count = len(pick_set & draw_set)
                    if match_count in win_stats:
                        win_stats[match_count] += 1
            print(f"\nStrategy: {strategy}")
            for res in results:
                print(f"Pick: {res['pick']} | Best match: {res['best_match']} | Dates: {res['match_dates'][:3]}{' ...' if len(res['match_dates'])>3 else ''} | Exact match: {res['exact_match']}")
            print(f"Win Stats: {win_stats}")
        print("===========================\n")
        return

    if args.auto_best:
        strategies = ['top', 'cold', 'hot', 'random', 'hybrid']
        best_score = -1
        best_strategy = None
        best_pick = None
        best_stats = None
        for strategy in strategies:
            picks = generate_picks(strategy, draws, args.n_picks, args.top_n, args.hot_x)
            win_stats = {6: 0, 5: 0, 4: 0, 3: 0}
            for draw in draws:
                draw_set = set(draw['numbers'])
                for pick in picks:
                    pick_set = set(pick)
                    match_count = len(pick_set & draw_set)
                    if match_count in win_stats:
                        win_stats[match_count] += 1
            # Score: prioritize 6, then 5, then 4, then 3 matches
            score = (win_stats[6]*10000 + win_stats[5]*100 + win_stats[4]*10 + win_stats[3])
            if score > best_score:
                best_score = score
                best_strategy = strategy
                best_pick = picks[0] if picks else None
                best_stats = win_stats.copy()
        print("\n=== AUTO-BEST STRATEGY ===")
        print(f"Best Strategy: {best_strategy}")
        print(f"Best Pick: {best_pick}")
        print(f"Win Stats: {best_stats}")
        print("========================\n")
        return

    picks = generate_picks(args.strategy, draws, args.n_picks, args.top_n, args.hot_x)
    results = check_picks_against_history(picks, draws)

    print(f"Strategy: {args.strategy}")
    for res in results:
        print(f"Pick: {res['pick']} | Best match: {res['best_match']} | Dates: {res['match_dates'][:3]}{' ...' if len(res['match_dates'])>3 else ''} | Exact match: {res['exact_match']}")

    if args.simulate:
        print("\n--- Win Rate Simulation ---")
        win_stats = {6: 0, 5: 0, 4: 0, 3: 0}
        for draw in draws:
            draw_set = set(draw['numbers'])
            for pick in picks:
                pick_set = set(pick)
                match_count = len(pick_set & draw_set)
                if match_count in win_stats:
                    win_stats[match_count] += 1
        total_draws = len(draws)
        print(f"Simulated {len(picks)} picks over {total_draws} draws:")
        for n in [6, 5, 4, 3]:
            print(f"{n}/6 matches: {win_stats[n]} times ({win_stats[n]/total_draws:.4%} per draw)")
        print("--------------------------\n")

    if args.export == 'json':
        with open('picks_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print('Results exported to picks_results.json')
    elif args.export == 'csv':
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv('picks_results.csv', index=False)
        print('Results exported to picks_results.csv')

if __name__ == '__main__':
    main()
