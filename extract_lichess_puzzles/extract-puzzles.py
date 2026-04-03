'''
This program reads puzzles from the Lichess open-source puzzle database (as a CSV file) and writes them into separate
training/validation .txt files. 
It also checks to make sure that the training set of puzzle positions does not share any position (FEN) with the validation set.

Lichess open-source puzzle DB: https://database.lichess.org/#puzzles
Accessed on 4/2/2026
'''

# imports
import csv
import chess
import random
import os
from collections import defaultdict


'''
This function does exactly what the head comment says the program does:
1. Extracts puzzle positions from input CSV.
2. Separates them into train/val sets, saving at least N validation puzzles.
3. Checks and filters positions to make sure no val positions are in the train set.
4. Writes training positions to one single text file.
5. Writes puzzles to separate text files based on theme, with separators for each puzzle.
6. Writes log file with info about train/val sets and theme distributions.
'''
def extract_puzzle_positions(csv_file, output_file, validation_dir=None, validation_sample_size=100):

    count = 0 # puzzle count
    validation_count = 0 # number of validation puzzles
    total_puzzles_by_theme = defaultdict(int)  # total puzzles per theme

    # If validation sampling is requested, collect all puzzles by theme
    validation_puzzles = set()  # Store puzzle IDs to exclude from main file
    puzzles_by_theme = defaultdict(list)

    # Prepare log file for sampling output
    sampling_log = []

    # If validation sampling is requested, collect all puzzles by theme
    if validation_dir:
        print("Collecting puzzles by theme for validation sampling...")
        sampling_log.append("Collecting puzzles by theme for validation sampling...\n")

        # Open the puzzle CSV
        with open(csv_file, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            # Store each puzzle ID with its themes
            for row in reader:
                puzzle_id = row['PuzzleId']
                themes_str = row['Themes']
                themes = themes_str.split()
                for theme in themes:
                    puzzles_by_theme[theme].append(puzzle_id)

        # Sample puzzles for each theme
        os.makedirs(validation_dir, exist_ok=True)
        msg = f"\nFound {len(puzzles_by_theme)} unique themes"
        print(msg)
        sampling_log.append(msg + "\n")
        msg = f"Sampling {validation_sample_size} puzzles per theme...\n"
        print(msg)
        sampling_log.append(msg + "\n")

        # For each theme, sample N puzzle IDs
        for theme, puzzle_ids in puzzles_by_theme.items():
            sample_ids = set(random.sample(puzzle_ids, min(validation_sample_size, len(puzzle_ids))))
            validation_puzzles.update(sample_ids)
            # Log number of puzzles sampled for validation set out of total
            msg = f"Theme '{theme}': sampled {len(sample_ids)} puzzles (out of {len(puzzle_ids)} total)"
            print(msg)
            sampling_log.append(msg + "\n")

        # Confirmation msg for puzzle sampling
        msg = f"\nTotal unique puzzles selected for validation: {len(validation_puzzles)}"
        print(msg)
        sampling_log.append(msg + "\n")

    # Write training/validation puzzles to their respective files
    print("Writing puzzles to files...\n")
    sampling_log.append("Writing puzzles to files...\n")
    validation_files = {}
    validation_theme_counts = defaultdict(int)

    # Open the puzzle CSV again
    with open(csv_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        # For each puzzle, save it to the train/validation set
        for row in reader:
            puzzle_id = row['PuzzleId']
            fen = row['FEN']
            moves_str = row['Moves']
            themes_str = row['Themes']
            themes = themes_str.split()

            # Track total puzzles processed per theme
            for theme in themes:
                total_puzzles_by_theme[theme] += 1

            # Split moves into a list
            moves = moves_str.split()

            # Create a chess board from the FEN
            board = chess.Board(fen)

            # Check if this puzzle is in validation set
            is_validation = validation_dir and puzzle_id in validation_puzzles

            # The first move (index 0) is the opponent's setup move
            # We want to extract the player's responses: index 1, 3, 5, ...
            # But first we need to play the opponent's move to get the position
            if len(moves) < 2:
                continue  # Skip puzzles with too few moves (this shouldn't happen)

            # Play the opponent's first move to set up the position
            board.push(chess.Move.from_uci(moves[0]))

            # Write puzzle start tag if it is in the validation set
            if is_validation:
                for theme in themes:
                    if theme not in validation_files:
                        assert validation_dir is not None
                        validation_files[theme] = open(
                            os.path.join(validation_dir, f"validation_puzzles_{theme}.txt"),
                            'w',
                            encoding='utf-8'
                        )
                    validation_files[theme].write("<|puzzle-start|>\n")

            # Extract every other move starting from index 1 (the player's responses)
            # Index 1, 3, 5, ... are the moves the player needs to find
            for i in range(1, len(moves), 2):

                # Get the best move for this position
                best_move_uci = moves[i] # UCI
                best_move_san = board.san(chess.Move.from_uci(best_move_uci)) # SAN
                # Create the FEN for the current position
                current_fen = board.fen()

                # If the puzzle is in the validation set, write to each of its respective files
                # Since puzzles can have multiple themes
                if is_validation:
                    # Write puzzle to validation file for each theme
                    for theme in themes:
                        if theme not in validation_files:
                            assert validation_dir is not None
                            validation_files[theme] = open(
                                os.path.join(validation_dir, f"validation_{theme}.txt"),
                                'w',
                                encoding='utf-8'
                            )
                        f = validation_files[theme] # temporary writer for a specific theme file
                        f.write(f"<|position-start|>\n")
                        f.write(f"FEN: {current_fen}\n")
                        f.write(f"Best move (UCI): {best_move_uci}\n")
                        f.write(f"Best move (SAN): {best_move_san}\n")
                        f.write(f"<|position-end|>\n")
                        validation_theme_counts[theme] += 1
                    validation_count += 1

                # If the puzzle is in the training set, just write the position (FEN) and best move (UCI)
                else:
                    # Write to main output file
                    f_out.write(f"<|position-start|>\n")
                    f_out.write(f"FEN: {current_fen}\n")
                    f_out.write(f"Best move (UCI): {best_move_uci}\n")
                    f_out.write(f"Best move (SAN): {best_move_san}\n")
                    f_out.write(f"<|position-end|>\n")
                    f_out.write(f"\n")
                    count += 1

                # Print progress every 1000 puzzles
                if (count + validation_count) % 1000 == 0:
                    print(f"Processed {count + validation_count} puzzle positions...")

                # Make the player's move (index i) and opponent's response (index i+1)
                # to advance to the next position
                board.push(chess.Move.from_uci(moves[i]))
                if i + 1 < len(moves):
                    board.push(chess.Move.from_uci(moves[i + 1]))

            # Write puzzle end tag for validation puzzles
            if is_validation:
                for theme in themes:
                    validation_files[theme].write("<|puzzle-end|>\n")

    # Close validation puzzle files
    for f in validation_files.values():
        f.close()

    # Print confirmation message with puzzle counts for train/val files
    print(f"\nExtracted {count} FEN-move pairs to {output_file}")
    if validation_dir:
        print(f"Extracted {validation_count} validation FEN-move pairs to {validation_dir}/")
        print(f"\nValidation puzzles by theme:")
        for theme in sorted(validation_theme_counts.keys()):
            print(f"  {theme}: {validation_theme_counts[theme]} positions")

    # Save sampling log if validation directory was used
    if validation_dir:
        sampling_log_file = os.path.join(validation_dir, "sampling_log.txt")
        with open(sampling_log_file, 'w', encoding='utf-8') as f:
            f.writelines(sampling_log)
        print(f"Sampling log saved to {sampling_log_file}")

    # return (return)
    return count

'''
This method filters out any positions (FENs) shared between the training and validation set of puzzle positions.
'''
def check_for_no_train_val_overlap_positions(train_file, validation_dir):
    # Collect all FENs that appear in any validation file
    val_fens = set() # set of all validation FENs
    for fname in os.listdir(validation_dir):
        # Filter out invalid files
        if not fname.endswith('.txt') or fname == 'sampling_log.txt':
            continue
        # Write all puzzle position FENs from the validation set of a specific theme to the set of validation fens
        with open(os.path.join(validation_dir, fname), 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('FEN: '):
                    val_fens.add(line[5:].strip())
    print(f"Found {len(val_fens)} unique FENs in validation set. Scanning training file for overlaps...")

    # Read and filter training file blocks
    kept = []
    removed = 0
    with open(train_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Split training file into blocks on the position delimiter
    text = ''.join(lines)
    blocks = text.split('<|position-start|>\n')
    header = blocks[0]  # anything before the first block (should be empty)

    # Keep only blocks whose FEN does not appear in the validation set
    kept_blocks = [header]
    for block in blocks[1:]:
        fen_line = next((line for line in block.splitlines() if line.startswith('FEN: ')), None)
        fen = fen_line[5:] if fen_line else None
        # Check that the current FEN is not in the validation set and remove it if it is.
        if fen in val_fens:
            removed += 1
        else:
            kept_blocks.append('<|position-start|>\n' + block)

    kept = kept_blocks

    # Write all disjoint FENs from validation set back to training set of puzzle positions
    with open(train_file, 'w', encoding='utf-8') as f:
        f.write(''.join(kept))

    # Confirmation message for number of FENs filtered from train set
    print(f"Removed {removed} training positions that overlapped with validation set.")
    print(f"Training file now contains {len(kept_blocks) - 1} positions.")


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Extract puzzles and write to train/val .txt files
    csv_file = os.path.join(script_dir, "lichess_db_puzzle.csv")
    train_file = os.path.join(script_dir, "training-puzzle-positions.txt")
    validation_dir = os.path.join(script_dir, "validation-puzzles")  # Set to None to disable validation sampling

    # Save at least N=1000 puzzles from each theme to use for validation
    extract_puzzle_positions(csv_file, output_file=train_file, validation_dir=validation_dir, validation_sample_size=1000)
    # Check that the training set of positions does not contain positions in the validation set of puzzles
    # If it does, remove the offender (take it out back)
    check_for_no_train_val_overlap_positions(train_file=train_file, validation_dir=validation_dir)

if __name__ == "__main__":
    main()

