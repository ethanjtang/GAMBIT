# Taken directly from https://en.wikipedia.org/wiki/Performance_rating_(chess), accessed on 4/28/2026
# All calculations use Zhang et. al.'s reported figures in https://arxiv.org/abs/2501.17186v2, accessed on 4/28/2026

def expected_score(opponent_ratings: list[float], own_rating: float) -> float:
    """How many points we expect to score in a tourney with these opponents"""
    return sum(1 / (1 + 10**((opponent_rating - own_rating) / 400)) for opponent_rating in opponent_ratings)

def performance_rating(opponent_ratings: list[float], score: float) -> int:
    """Calculate mathematically perfect performance rating with binary search"""
    lo, hi = 0, 4000

    while hi - lo > 0.001:
        mid = (lo + hi) / 2
        if expected_score(opponent_ratings, mid) < score:
            lo = mid
        else:
            hi = mid
    return round(mid)


# Caculating the performance rating of Zhang et. al. 2025's ChessLLM
# Use estimated Elos provided in Zhang et. al.'s paper "Complete Chess Games Enable LLM Become Chess Master"
# Assume Stockfish Level 0 is (1350+1440)/2 = ~1395 Elo
# vs. Level 0, ChessLLM scored 61W 29L 10D -> 66/100 points
sf_lvl0 = (1350+1440)*0.5
lvl0_score = 61 + 10*(0.5) + 0 # Wins + Draws + Losses
assert sf_lvl0 == 1395
assert lvl0_score == 66
# Assume Stockfish Level 1 is (1450+1560)/2 = ~1505 Elo 
# vs. Level 1, ChessLLM scored 56W 37L 7D -> 59.5/100 points
sf_lvl1 = (1450+1560)*0.5
lvl1_score = 56 + 7*(0.5) + 0 # Wins + Draws + Losses
assert sf_lvl1 == 1505
assert lvl1_score == 59.5
# Assume Stockfish Level 2 is (1570+1720)/2 = ~1645 Elo 
# vs. Level 2, ChessLLM scored 30W 69L 1D -> 30.5/100 points
sf_lvl2 = (1570+1720)*0.5
lvl2_score = 30 + 1*(0.5) + 0 # Wins + Draws + Losses
assert sf_lvl2 == 1645
assert lvl2_score == 30.5

# set performance rating args
total_score = lvl0_score + lvl1_score + lvl2_score
assert total_score == 156
opponents = [1395]*100 + [1505]*100 + [1645]*100

# calculate performance rating
chessLLMperf = performance_rating(opponents, total_score)
print(f"ChessLLM performance: {chessLLMperf}")
assert chessLLMperf == 1788


