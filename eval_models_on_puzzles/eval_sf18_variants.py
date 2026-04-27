"""
This program tests a variety of Stockfish configs on a sample of mate-in-X puzzles.

A move is treated as correct if it matches the best move recorded OR
yields a mate score equivalent to the best move (decreases the mate-in-X evaluation by 1).
ex) Mate in 2 -> Mate in 1

Please refer to puzzle_utils.py for documentation on the functions:
sample_puzzles() - handles puzzle sampling 
get_engine() - creates custom instances of Stockfish
check_position_accuracy() - checks if the response by a LLM/chess engine is the best move in a position
                            (including alternative solutions!)
"""

from __future__ import annotations # for some strange issue with function definitions

# imports
import os
import sys
import chess
import chess.engine
from puzzle_utils import sample_puzzles, get_engine, check_position_accuracy

# ============================
# CONFIG
# ============================

# constants
PUZZLES_DIR = 'puzzles' # for full puzzle sets
SAMPLE_DIR = 'sample'   # save sample of N puzzles for reuse/testing different models
N_PUZZLES = 100         # number of puzzles to test on for each theme
SF18_DEPTH = 20         # depth for Stockfish variants
SF18_TIMEOUT = 10.0     # 10s timeout for depth-gated Stockfish variants
SF18_FAST_THINKTIME = 0.05  # think time (seconds) for fast Stockfish variants

# dict to associate puzzle theme with (filepath, mate_depth) pairs
# filepath for filepath (duh)
# UNUSED: mate_depth as an arg to build "cheating" prompts
PUZZLE_FILES = {
    'mateIn1': (os.path.join(PUZZLES_DIR, 'validation_puzzles_mateIn1.txt'), 1),
    'mateIn2': (os.path.join(PUZZLES_DIR, 'validation_puzzles_mateIn2.txt'), 2),
    'mateIn3': (os.path.join(PUZZLES_DIR, 'validation_puzzles_mateIn3.txt'), 3),
}

# List of Stockfish configs
# Skill Levels 0-3 are roughly equivalent to 1347, 1444, 1566, 1729 Elo respectively
SF_MODELS = {
    # depth-gated configs
    'SF18 depth=20 (ground truth)':       {'skill': None, 'depth': 20},
    'SF18 Skill Level 0':                 {'skill': 0,    'depth': SF18_DEPTH},
    # fast configs
    'SF18 Base - Fast (0.05s)':           {'skill': None, 'thinktime': SF18_FAST_THINKTIME},
    'SF18 Skill 0 - Fast (0.05s)':        {'skill': 0,    'thinktime': SF18_FAST_THINKTIME},
}


# ============================
# PUZZLE STUFF
# ============================

'''
Helper function used to save sample of N puzzles to a separate .txt file.

filepath - filepath to save to
puzzles - list of puzzles
'''
def save_sample_puzzles(filepath: str, puzzles: list) -> None:
    # Write each puzzle to output file (following the same format as input puzzle files)
    with open(filepath, 'w', encoding='utf-8') as f:
        for puzzle in puzzles:
            f.write('<|puzzle-start|>\n')
            for (fen, uci, san) in puzzle:
                f.write('<|position-start|>\n')
                f.write(f'FEN: {fen}\n')
                f.write(f'Best move (UCI): {uci}\n')
                f.write(f'Best move (SAN): {san}\n')
                f.write('<|position-end|>\n')
            f.write('<|puzzle-end|>\n')

'''
Helper function used to sample N puzzles from each theme.

returns a dict, {puzzles_by_theme} containing keys:
puzzles - sample list of puzzles
mate_depth - info arg used for "cheating" prompts
'''
def fetch_puzzle_sample() -> dict:

    # make sample puzzles dir
    os.makedirs(SAMPLE_DIR, exist_ok=True)

    puzzles_by_theme = {}

    # For each puzzle theme...
    for theme, (source_filepath, mate_depth) in PUZZLE_FILES.items():

        # Either load an existing sample if it exists or write to a new file if no sample exists
        sample_filepath = os.path.join(SAMPLE_DIR, f'{theme}_sample.txt')

        # sample exists, load from existing
        if os.path.exists(sample_filepath):
            print(f'  {theme}: loading existing sample from {sample_filepath}')
            puzzles = sample_puzzles(sample_filepath, N_PUZZLES)
        # sample doesn't exist, sample and write to new file
        else:
            print(f'  {theme}: sampling {N_PUZZLES} puzzle(s) from source and saving to {sample_filepath}')
            # sample N puzzles for theme
            puzzles = sample_puzzles(source_filepath, N_PUZZLES)
            # write new sample to file
            save_sample_puzzles(sample_filepath, puzzles)
        puzzles_by_theme[theme] = (puzzles, mate_depth)

    # (puzzles, mate_depth)
    return puzzles_by_theme

# ============================
# THE BIG FISH
# ============================

'''
Helper function to return a configured version of Stockfish 18.

Returns the configured engine as a chess.engine.SimpleEngine object.
'''
def get_sf_player_engine(skill: int | None) -> chess.engine.SimpleEngine:
    engine = get_engine()
    if skill is not None:
        engine.configure({'Skill Level': skill})
    return engine

'''
Helper function to return the best move in a given position.
Using Stockfish 18 at depth=20.

Returns the best move in UCI format as a string.
'''
def get_ground_truth_move(engine: chess.engine.SimpleEngine, fen: str) -> str:
    board = chess.Board(fen)
    result = engine.play(board, chess.engine.Limit(depth=20,time=SF18_TIMEOUT))
    return result.move.uci() if result.move else ''

'''
Helper function to return the best move in a given position.
Using Stockfish 18 at a very low thinktime THINKTIME

Returns the best move in UCI format as a string.
'''
def get_fast_fish_move(engine: chess.engine.SimpleEngine, fen: str, thinktime: float = SF18_FAST_THINKTIME) -> str:
    board = chess.Board(fen)
    result = engine.play(board, chess.engine.Limit(time=thinktime))
    return result.move.uci() if result.move else ''

'''
Helper function to return the best move in a given position.
Using the provided engine at N depth.
engine - chess engine to use
fen - chess position
depth - chess engine depth to search

Returns the best move (according to the engine) in UCI format as a string.
'''
def get_engine_move(engine: chess.engine.SimpleEngine, fen: str, depth: int) -> str:
    board = chess.Board(fen)
    result = engine.play(board, chess.engine.Limit(depth=depth,time=SF18_TIMEOUT))
    return result.move.uci() if result.move else ''

'''
Helper function to evaluate a SF18 model variant on a sample of puzzles from X theme.
model_name - SF18 variant name
depth - depth used by variant
thinktime - thinktime used by variant
puzzles_by_theme - sample of N puzzles from X themes
judge_engine - ground truth engine, used to check for alternative solutions for mate-in-X puzzles
               (since multiple moves can lead to mate)
'''
def evaluate_sf_model(model_name: str, skill: int | None, depth: int | None, thinktime: float | None, puzzles_by_theme: dict, judge_engine: chess.engine.SimpleEngine):
    
    # SF variant name
    print(f'\n{"=" * 70}')
    print(f'MODEL: {model_name}')
    print(f'{"=" * 70}')

    # initialize engine
    player_engine = get_sf_player_engine(skill)

    # position/puzzle-wide results
    total_positions_correct = 0
    total_positions = 0
    total_puzzles_solved = 0
    total_puzzles = 0

    # For each puzzle theme...
    for theme, (puzzles, _mate_depth) in puzzles_by_theme.items():

        # print out theme being evaluated and number of puzzles in sample
        print(f'\n  Theme: {theme} ({len(puzzles)} puzzles)')
        print(f'  {"-" * 60}')

        # theme-wide results
        theme_positions_correct = 0
        theme_positions_total = 0
        theme_puzzles_solved = 0

        # For each puzzle...
        for puzzle_idx, puzzle in enumerate(puzzles):

            # puzzle-wide results
            puzzle_positions_correct = 0

            print(f'\n  Puzzle {puzzle_idx + 1}/{len(puzzles)}:')

            # For each puzzle position...
            for pos_idx, (fen, best_uci, best_san) in enumerate(puzzle):

                # get the 'best' move from the SF18 variant being evaluated
                # fast variants
                if thinktime is not None:
                    response = get_fast_fish_move(player_engine, fen, thinktime)
                # depth-gated variants
                else:
                    assert depth is not None, 'SF_MODELS entry must have either depth or thinktime'
                    response = get_engine_move(player_engine, fen, depth)
                
                # check if the move is actually accurate
                correct = check_position_accuracy(response, fen, best_uci, best_san, judge_engine)
                status = 'CORRECT' if correct else 'WRONG'

                # print out position-specific results
                print(f'    Position {pos_idx + 1}:')
                print(f'      FEN:           {fen}')
                print(f'      Best move UCI: {best_uci}')
                print(f'      Engine played: {response}')
                print(f'      Result:        [{status}]')

                # update results if the position was solved correctly by the variant
                if correct:
                    puzzle_positions_correct += 1
                    theme_positions_correct += 1
                    total_positions_correct += 1
                theme_positions_total += 1
                total_positions += 1

            # check if the variant solved the puzzle correctly (100% accuracy for all puzzle positions)
            puzzle_solved = puzzle_positions_correct == len(puzzle)

            # update results if the puzzle was solved correctly
            if puzzle_solved:
                theme_puzzles_solved += 1
                total_puzzles_solved += 1
            total_puzzles += 1

            # print final puzzle-wide result and position-wide accuracy
            puzzle_status = 'SOLVED' if puzzle_solved else 'FAILED'
            print(f'    Puzzle result: [{puzzle_status}] ({puzzle_positions_correct}/{len(puzzle)} positions correct)')

        # calculate position and puzzle-wide accuracy for all puzzles for the theme being evaluated
        theme_pos_acc = theme_positions_correct / theme_positions_total * 100 if theme_positions_total > 0 else 0
        theme_puzzle_acc = theme_puzzles_solved / len(puzzles) * 100 if puzzles else 0

        # print out theme-wide statistics
        print(f'\n  {theme} summary:')
        print(f'    Puzzles solved:    {theme_puzzles_solved}/{len(puzzles)} ({theme_puzzle_acc:.1f}%)')
        print(f'    Positions correct: {theme_positions_correct}/{theme_positions_total} ({theme_pos_acc:.1f}%)')

    # calculate overall positionn and puzzle-wide accuracy for all puzzles across all themes
    overall_pos_acc = total_positions_correct / total_positions * 100 if total_positions > 0 else 0
    overall_puzzle_acc = total_puzzles_solved / total_puzzles * 100 if total_puzzles > 0 else 0

    # print overall statistics
    print(f'\n  OVERALL ({model_name}):')
    print(f'    Puzzles solved:    {total_puzzles_solved}/{total_puzzles} ({overall_puzzle_acc:.1f}%)')
    print(f'    Positions correct: {total_positions_correct}/{total_positions} ({overall_pos_acc:.1f}%)')

    # IMPORTANT: close the engine!
    player_engine.quit()

    # return overall results for display
    return (total_puzzles_solved, total_puzzles, total_positions_correct, total_positions, None)

# ============================
# MAIN (MAIN [MAIN {MAIN}])
# ============================

'''
Custom class to write output to both stdout and log file simultaneously.
Pogger == Program logger
'''
class Pogger:
    '''Writes all output to both stdout and a log file simultaneously.'''
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, 'w', encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    def close(self):
        self.log.close()

'''
i have run out of jokes to put in the comments of this program
because my brain is being atrophied due to excessive AI use
help help help help me helpo me hek,pemm me ejsjkoadosln
'''
def main():
    # Set up logging
    LOG_FILE = 'results.txt'
    poggee = Pogger(LOG_FILE)
    sys.stdout = poggee

    # Get a sample of N puzzles from each theme
    print('Sampling puzzles...')
    puzzles_by_theme = fetch_puzzle_sample()
    for theme, (puzzles, _) in puzzles_by_theme.items():
        print(f'  {theme}: {len(puzzles)} puzzle(s) ready')

    # domain expansion: deadly sentencing
    print('\nOpening judge engine (SF18 depth=20)...')
    judge_engine = get_engine()

    # results summary
    summary = {}

    # evaluate SF models on all puzzles
    for model_name, config in SF_MODELS.items():
        summary[model_name] = evaluate_sf_model(model_name, config['skill'], config.get('depth'), config.get('thinktime'), puzzles_by_theme, judge_engine)

    # IMPORTANT: call engine.quit() so you don't use up all of the memory
    judge_engine.quit()

    # Print final summary table across SF/LLM models
    print(f'\n\n{"=" * 95}')
    print('FINAL SUMMARY')
    print(f'{"=" * 95}')
    print(f'{"Model":<48} {"Puzzles":>17} {"Positions":>17} {"Invalid Parses":>10}')
    print(f'{"-" * 95}')
    for model_name, (psolved, ptotal, poscorrect, postotal, parse_failed) in summary.items():
        puzzle_acc = psolved / ptotal * 100 if ptotal > 0 else 0
        pos_acc = poscorrect / postotal * 100 if postotal > 0 else 0
        parse_str = f'{parse_failed}/{postotal}' if parse_failed is not None else 'N/A'
        print(f'{model_name:<48} {f"{psolved}/{ptotal} ({puzzle_acc:.1f}%)":>17} {f"{poscorrect}/{postotal} ({pos_acc:.1f}%)":>17} {parse_str:>10}')

# Make sure stdout doesn't break for fun
if __name__ == '__main__':
    try:
        main()
    finally:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
