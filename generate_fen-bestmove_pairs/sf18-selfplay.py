"""
This program generates self-play games between the base version of Stockfish 18 (without any adjustments) and weaker
versions of the Stockfish 18 engine (using the option Skill Level at https://official-stockfish.github.io/docs/stockfish-wiki/UCI-&-Commands.html).

SF18 Base plays 50 games (25 W / 25 B) vs SF18 Skill Level 0-20.
I did not use an opening book (since the original paper ChessLLM didn't use an opening book), but
someone should definitely explore it since it gives a wider variety of positions/openings 
(and likely better generalization for chess-focused LLMs).

Outputs:
 - output/games.pgn - All self-play games in PGN format
 - output/summary.txt - W/D/L results per skill level
 - output/positions.parquet - All unique positions from every game with FEN, best move, evaluation tuples
 - output/finetune.txt - Filtered subset of unique FEN + best move pairs for LLM finetuning
"""

# imports (enter funny/relevant bit on existing US political situation here)
import os, time, datetime
import chess, chess.engine, chess.pgn
import pandas as pd # subham777 is goated btw

HERE = os.path.dirname(__file__) # current directory
SF_PATH = os.path.join(HERE, "stockfish-18.exe") # THE BIG FISH
OUTPUT_DIR = os.path.join(HERE, "output") # output directory

# Stockfish engine depth, we say this is good enough (although depth=20-25 would give more accurate synthetic data)
# For mate-in-X positions, depth=15 should cover a vast majority of puzzles
# except for extreme cases where the correct move is being pruned somehow
DEPTH = 15 
# For completness sake:
# engine depth != game length
# they are two seperate metrics, engine depth is an indicator of how "deep" the engine searches on any given move

GAMES_PER_LEVEL = 50 # number of games of self-play (per level)

# This function plays a single chess game between SF18 Base and its opponent.
# base and opp point to engine instances
# base_is_white, opp_skill_level, and game_num are all descriptive args for saving the game
def play_game(base, opp, base_is_white, opp_skill_level, game_num):

    board = chess.Board() # board (board)
    game  = chess.pgn.Game() # game (game)
    evals = {} # eval (expected score) for each position

    # Add desc headers to game PGN file
    game.headers.update({
        "Event":  f"SF18 Base vs SF18 Skill Level {opp_skill_level}",
        "Date":   datetime.date.today().strftime("%Y.%m.%d"),
        "Round":  str(game_num),
        "White":  "SF18 Base" if base_is_white else f"SF18 L{opp_skill_level}",
        "Black":  f"SF18 L{opp_skill_level}" if base_is_white else "SF18 Base",
    })

    limit = chess.engine.Limit(depth=DEPTH) # search depth limit
    node = game # tracks current position of PGN game tree - used to record game into PGN
    
    # While the game is ongoing...
    while not board.is_game_over():

        # this one liner is disgusting but it just chooses the correct engine to use to search for the next move
        engine = (base if base_is_white else opp) if board.turn == chess.WHITE else (opp if base_is_white else base)

        # Get the next move
        # on base turns, the score comes free (yippee!)
        # on opp turns, ask base to analyse at depth=20
        is_base_turn = (engine is base)
        result = engine.play(board, limit, info=chess.engine.INFO_SCORE if is_base_turn else chess.engine.INFO_NONE)
        move = result.move
        assert move is not None

        # Get the current evaluation of the position (using base SF18 at depth=20)
        score = result.info.get("score") if is_base_turn else base.analyse(board, limit).get("score")
        if score is not None:
            white_score = score.white()
            evals[board.fen()] = str(white_score) if white_score.is_mate() else white_score.score()

        # Record and make the move on the board
        node = node.add_variation(move)
        board.push(move)

    # Record the outcome of the game and return it (along with evals for each position)
    outcome = board.outcome()
    game.headers["Result"] = outcome.result() if outcome else "*"
    return game, evals

# Yields (fen, uci, san, eval_cp) for ALL moves in the game, both colors.
# Used to build the positions parquet.
# The evals are for anyone who wants to add it to FEN + best move pairs for finetuning LLMs
def collect_all_positions(game, evals):
    board = game.board()
    node = game
    # Play through each node/half-move in the game and extract delicious tuples
    while node.variations:
        node = node.variations[0]
        fen = board.fen()
        yield fen, node.move.uci(), board.san(node.move), evals.get(fen)
        board.push(node.move)

# Yields (fen, uci, san, eval_cp) for moves made by the given color only.
# Used to build the filtered finetune text file.
# Filter is necessary to ensure we are not recording FEN + best move pairs made by weak versions of Stockfish
# who were annihilated by the standard Stockfish 18 instance at depth=20 with no handicap
def collect_positions_for_color(game, color, evals):
    board = game.board()
    node = game
    # Play through each node/half-move in the game and extract delicious tuples
    while node.variations:
        node = node.variations[0]
        fen = board.fen()
        if board.turn == color:
            yield fen, node.move.uci(), board.san(node.move), evals.get(fen)
        board.push(node.move)

# main (main)
def main():

    # Create output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Store (game, lvl, base_is_white) tuples so we can filter by player when writing LLM finetuning data
    all_games = []
    # tally ho
    tally = {} # used to keep score in matches
    game_num = 0

    print(f"Playing {GAMES_PER_LEVEL * 21} games (depth={DEPTH}, {GAMES_PER_LEVEL}/level)...\n")

    # Play a N-game match for each SF level
    for lvl in range(21):

        # Pre-match instantiation
        tally[lvl] = {"W": 0, "D": 0, "L": 0} # tally ho
        print(f"\n=== SF Base vs SF Level {lvl} ===")

        # Load engines and configure them
        base = chess.engine.SimpleEngine.popen_uci(SF_PATH)
        opp = chess.engine.SimpleEngine.popen_uci(SF_PATH)
        base.configure({"Skill Level": 20})
        opp.configure( {"Skill Level": lvl})

        # Play N games
        for i in range(GAMES_PER_LEVEL):
            game_num += 1
            base_is_white = i % 2 == 0 # Each side plays alternating colors

            # Progress indicator for current game
            print(f"Game {i+1}/{GAMES_PER_LEVEL} ({'Base=White' if base_is_white else 'Base=Black'})", end="", flush=True)

            # Record start time of game
            t = time.time()

            # Play and save the game + result
            game, evals = play_game(base, opp, base_is_white, lvl, game_num)
            result = game.headers["Result"]
            all_games.append((game, evals, lvl, base_is_white))
            
            # Update tally (overall match score) based on result
            if result == "1/2-1/2":
                tally[lvl]["D"] += 1
            elif (result == "1-0") == base_is_white:
                tally[lvl]["W"] += 1
            else:
                tally[lvl]["L"] += 1
            
            # Print result, move count, and time elapsed for game
            moves = game.end().board().fullmove_number - 1
            print(f" -> {result} in {moves} moves ({time.time()-t:.1f}s)")

        # After the match, stop both engines and record final match result
        base.quit(); opp.quit()
        r = tally[lvl]
        print(f"  Level {lvl}: W={r['W']} D={r['D']} L={r['L']}")

    # Save all games played to PGN file
    pgn_path = os.path.join(OUTPUT_DIR, "games.pgn")
    with open(pgn_path, "w", encoding="utf-8") as f:
        for g, _evals, _lvl, _biw in all_games:
            print(g, file=f, end="\n\n")
    print(f"\nSaved {len(all_games)} games to {pgn_path}")

    # Save summary log text file
    summary_path = os.path.join(OUTPUT_DIR, "summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"SF18 Base (depth={DEPTH}, Skill Level 20) vs SF18 Skill Levels 0-20\n")
        f.write(f"{'Level':<8} {'W':<6} {'D':<6} {'L':<6} Score%\n" + "-"*38 + "\n")
        for lvl in range(21):
            r = tally[lvl]
            f.write(f"{lvl:<8} {r['W']:<6} {r['D']:<6} {r['L']:<6} "
                    f"{(r['W'] + 0.5*r['D']) / GAMES_PER_LEVEL * 100:.1f}%\n")
    print(f"Summary saved to {summary_path}")

    # Save parquet containing ALL unique (position, eval) tuples from ALL games
    seen_parquet = set() # unique positions
    parquet_rows = []
    
    # For each game...
    for g, evals, _lvl, _biw in all_games:
        # Save tuples for every unique position encountered
        for fen, _uci, _san, eval_val in collect_all_positions(g, evals):
            if (fen, eval_val) not in seen_parquet:
                seen_parquet.add((fen, eval_val))
                parquet_rows.append({"fen": fen, "eval": str(eval_val) if eval_val is not None else None})

    parquet_path = os.path.join(OUTPUT_DIR, "selfplay-positions.parquet")
    pd.DataFrame(parquet_rows).to_parquet(parquet_path, index=False, row_group_size=10000) # save in chunks of 10000 for memory issues
    print(f"Saved {len(parquet_rows)} unique positions to {parquet_path}")

    # Save finetuning text file, filtering position + best move pairs based on game result
    # - Draw: save positions for both colors
    # - Decisive: only save winner's positions.
    seen_finetune = set() # unique positions
    finetune_path = os.path.join(OUTPUT_DIR, "finetune.txt")
    with open(finetune_path, "w", encoding="utf-8") as f:
        # For each game...
        for g, evals, lvl, _biw in all_games:
            # Get result of the game
            result = g.headers["Result"]
            if result == "1/2-1/2":
                colors = [chess.WHITE, chess.BLACK]
            elif result == "1-0":
                colors = [chess.WHITE]
            elif result == "0-1":
                colors = [chess.BLACK]
            else: # this continue op should never happen
                print("Unknown result WEE WOO WEE WOOO !!!!!!!!!!!!!!!!!")
                continue
            
            # Add position to finetune text data if it is unique and was played by a 
            # sensible opponent (aka someone who didn't lose the game and isn't a moron)
            for color in colors:
                # filter for moves played by reasonable opponents
                for fen, uci, san, _eval in collect_positions_for_color(g, color, evals):
                    # check uniqueness
                    if (fen, uci) not in seen_finetune:
                        seen_finetune.add((fen, uci))
                        f.write(f"<|position-start|>\n"
                                f"FEN: {fen}\n"
                                f"Best move (UCI): {uci}\n"
                                f"Best move (SAN): {san}\n"
                                f"<|position-end|>\n\n")
    
    print(f"Saved {len(seen_finetune)} unique positions to {finetune_path}")

# main (main [main])
if __name__ == "__main__":
    main()
