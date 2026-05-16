# GAMBIT

**arXiv link COMING SOON**

> <ins>G</ins>ener<ins>a</ins>lization or <ins>M</ins>emorization? <ins>B</ins>r<ins>i</ins>ttleness <ins>T</ins>esting for Chess-Trained Language Models

## Relevant Links

[![GitHub](https://img.shields.io/badge/GitHub-KinGPT-black.svg?style=for-the-badge)](https://github.com/ethanjtang/KinGPT) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-KinGPT-yellow?style=for-the-badge)](https://huggingface.co/ethanjtang/KinGPT) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-Puzzles-yellow?style=for-the-badge)](https://huggingface.co/datasets/ethanjtang/GAMBIT-lichess-puzzle-positions) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-SF18%20Selfplay-yellow?style=for-the-badge)](https://huggingface.co/datasets/ethanjtang/GAMBIT-stockfish18-selfplay) <br>

## TLDR

<p align="center">
  <img src="misc/pass@k.png" alt="pass@K=10" width="350">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="misc/llm-modulo.png" alt="llm-modulo" width="350">
</p>

## Code

### Dependencies

```bash
pip install torch transformers accelerate python-chess numpy sentencepiece protobuf
```

You also will need to download the appropiate [Stockfish 18 binary](https://stockfishchess.org/download/) to check for alternate puzzle solutions.

### Model Evaluation on Puzzles (`.\eval_models_on_puzzles`)

`eval_all_models_base.py` - Evaluate all OpenLLaMa, RedPajama, ChessGPT models on normal and cheating-style prompts for the n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`eval_all_models_modulo.py` - Evaluate all OpenLLaMa, RedPajama, ChessGPT models on pass@K=10 and modulo-style prompts for the (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`eval_sf18_variants.py` - Evaluate all SF variants (Base depth=20, Base thinktime=0.05s, Level 0 depth=20) for the (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`puzzle_utils.py` - Contain helper functions sample_puzzles(filepath, n), get_engine(), and check_position_accuracy(response, fen, best_move_uci, best_move_san, engine) used by all other eval files.

> KinGPT puzzle evaluation code is located in its [respective repository](https://github.com/ethanjtang/KinGPT)

### Generate FEN + Best Move Pairs (`.\generate_fen-bestmove_pairs`)

`extract-puzzles.py` - Read puzzles from the Lichess Puzzle Database CSV file into text format, **filtering out validation set puzzle positions (at FEN-level) from the training data set** for KinGPT-Woodpecker.

`sf18-selfplay.py` - Generate N=50 selfplay games between Stockfish 18 Base and Stockfish 18 variants from Levels 0-20. Each side plays 25W and 25B for a total of 1050 selfplay games at depth=15. Converts all unique position + best move pairs played by reasonable players (aka the game ended in a win/draw for the recorded side) to text as training data for KinGPT-Beaver.

### Results (`.\results`)

`base-model-results.txt` - Results from OpenLLaMa and ChessGPT for normal and cheating-style prompts on n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`kingpt-results.txt` - Results from KinGPT variants for normal-style prompts on (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`modulo-pass@k-results.txt` - Results from OpenLLaMa and ChessGPT for pass@K=10 and modulo-style prompts on (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`sf-variant-results.txt` - Results from Stockfish 18 variants (Base @ depth=20, Base @ thinktime=0.05s, Level 0 @ depth=20) for normal-style prompts on (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

> I came up with the idea to test on RedPajama 3B Base (base model used to finetune ChessGPT variants) after performing my initial set of tests, so the results files are separate.

`redpajama-base-results.txt` - Results from RedPajama for normal and cheating-style prompts on (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`redpajama-modulo-pass@k-results.txt` - Results from RedPajama for pass@K=10 and modulo-style prompts on (same) n=300 sample of n=100 mate-in-1, mate-in-2, and mate-in-3 theme puzzles.

`chimera-vs-c1-themes.txt` - Results from theme-wide puzzle comparison (n=100 puzzles for set of m=20 themes for 2000 total puzzles) between KinGPT-Chimera and Z. Tang et. al. 2026's model C1-4B.

`modulo-pass@K-detailed-traces.txt` - Full trace from n=1 sample of mate-in-3 puzzles from OpenLLaMa, ChessGPT, and RedPajama with full output for LLM-Modulo loop reprompting and pass@K=10 prompting.

### Puzzle Samples (`.\sample_puzzles`)

`mateIn1_sample.txt` - n=100 random sample of mate-in-1 puzzles from validation set of puzzles (please check out Puzzles HF link at top of repo).

`mateIn2_sample.txt` - n=100 random sample of mate-in-2 puzzles from validation set of puzzles.

`mateIn3_sample.txt` - n=100 random sample of mate-in-3 puzzles from validation set of puzzles.

`\chimera-vs-c1-samples` - n=100 puzzles from n=20 themes, testing KinGPT-Chimera on the same themes (but not same set of puzzles, see below for why) as Z. Tang's model C1-4B.

### Misc (`.\misc`)

`.\chessLLM_perf_calc.py` - small script to demonstrate how Zhang et. al. 2025's ChessLLM does not achieve their advertised rating of 1788 Elo using true performance rating.

## Training/Inference

Training for KinGPT variants was conducted on a 1x A100 GPU node on the ASU Sol Supercomputer.

Inference for Stockfish 18 and KinGPT variants was conducted on my personal 2019 computer with a Ryzen 7 5800X, 32 GB DDR4 2133 MHz RAM, and GTX 1060 6GB (I would love to upgrade it, but...).

Inference for OpenLLaMa 3B and ChessGPT model variants was conducted on a Lambda Labs 1xH100 GPU node.

Inference for RedPajama 3B was conducted on a Lambda Labs 1xA10 GPU node.

## Evaluations

### Models Used

| Name | Model |
|:---|:---|
| Stockfish 18 | [Stockfish 18](https://stockfishchess.org/) |
| KinGPT | [KinGPT](https://huggingface.co/ethanjtang/KinGPT) |
| OpenLLaMa | [Open LLaMa 3B V1](https://huggingface.co/openlm-research/open_llama_3b) |
| RedPajama | [Red Pajama 3B Base](https://huggingface.co/togethercomputer/RedPajama-INCITE-Base-3B-v1) |
| ChessGPT-Base | [ChessGPT Base V1](https://huggingface.co/Waterhorse/chessgpt-base-v1) |
| ChessGPT-Chat | [ChessGPT Chat V1](https://huggingface.co/Waterhorse/chessgpt-chat-v1) |

### Inference Types

For all responses, a seperate judge engine (SF18 instance at depth=20) checks if the provided move is equivalent to the solution provided by Lichess. For mate-in-X puzzles, a move is an alternative solution if it improves the evaluation of the position (mate-in-N -> mate-in-[N-1]).

**normal -** LLM gives a single response.

**cheating -** Prompt has the evaluation of the position appended before it, LLM gives a single response.

> Please refer to `.\eval_models_on_puzzles\eval_all_models_base` for implementation details on normal and cheating style LLM inference.

**pass@K=10 -** LLM gives 10 responses at temperature=0.7, correct answer if any of the K answers matches solution/passes judgement.

**modulo -** LLM is reprompted with feedback up to 10 times from Critic #1 (move validity) or Critic #2 (move accuracy), correct answer if LLM response passes both critics.

> Please refer to `.\eval_models_on_puzzles\eval_all_models_modulo` for implementation details on pass@K=10 and modulo style LLM inference.

### Model Accuracy (Best Move %)

Overall accuracy measures how frequently a model chooses the best move in any given puzzle position.

$\text{Overall accuracy} = \frac{\text{number of correct responses}}{\text{total number of positions}}$

A puzzle is considered solved correctly if a model generates a correct response to **all** positions in the puzzle.

Puzzle accuracy measures how frequently a model solves all puzzle positions for a given puzzle for all puzzles tested.

$\text{Puzzle accuracy} = \frac{\text{number of puzzles solved}}{\text{total number of puzzles}}$

| Model | Inference Type | Puzzle Accuracy | Overall Accuracy |
|:---|:---|---:|---:|
| Stockfish 18, Base | depth=20 | 300/300 (100.0%) | **600/600 (100.0%)** |
| Stockfish 18, Base | time=0.05s | 300/300 (100.0%) | 600/600 (100.0%) |
| Stockfish 18, Level 0 | depth=20 | 192/300 (64.0%) | **476/600 (79.3%)** |
| KinGPT-Woodpecker | normal | 217/300 (72.3%) | 492/600 (82.0%) |
| KinGPT-Beaver* | normal | 3/300 (1.0%) | 10/600 (1.7%) |
| KinGPT-Chimera | normal | 225/300 (75.0%) | **510/600 (85.0%)** |
| OpenLLaMa 3B | normal | 0/300 (0.0%) | 1/600 (0.2%) |
| OpenLLaMa 3B | cheating | 5/300 (1.7%) | 13/600 (2.2%) |
| OpenLLaMa 3B | pass@K=10 | 3/300 (1.0%) | **20/600 (3.3%)** |
| OpenLLaMa 3B | modulo | 8/300 (2.7%) | **70/600 (11.7%)** |
| RedPajama 3B | normal | 0/300 (0.0%) | 4/600 (0.7%) |
| RedPajama 3B | cheating | 0/300 (0.0%) | 0/600 (0.0%) |
| RedPajama 3B | pass@K=10 | 1/300 (0.3%) | **9/600 (1.5%)** |
| RedPajama 3B | modulo | 30/300 (10.0%) | **125/600 (20.8%)** |
| ChessGPT-Base | normal | 46/300 (15.3%) | 166/600 (27.7%) |
| ChessGPT-Base | cheating | 48/300 (16.0%) | 182/600 (30.3%) |
| ChessGPT-Base | pass@K=10 | 115/300 (38.3%) | **353/600 (58.8%)** |
| ChessGPT-Base | Modulo | 54/300 (18.0%) | **202/600 (33.7%)** |
| ChessGPT-Chat | normal | 30/300 (10.0%) | 126/600 (21.0%) |
| ChessGPT-Chat | cheating | 37/300 (12.3%) | 153/600 (25.5%) |
| ChessGPT-Chat | pass@K=10 | 61/300 (20.3%) | **227/600 (37.8%)** |
| ChessGPT-Chat | modulo | 41/300 (13.7%) | **176/600 (29.3%)** |

*KinGPT-Beaver acts as a (very approximate) proxy for Zhang et. al. 2025's ChessLLM from ["Complete Chess Games Enable LLM Become Chess Master"](https://arxiv.org/abs/2501.17186v2), testing whether training on position + best move pairs from game data generalizes to puzzle positions. I note that solving puzzle positions and playing full games is the same core task of finding the best move in any given position.

### Model Sanity (Legal Move %)

Sanity measures how frequently a model chooses a legal/valid move in a given position.

$\text{Sanity} = 1 - \frac{\text{number of invalid parses}}{\text{total number of positions}}$

| Model | Inference Type | Sanity |
|:---|:---|---:|
| Stockfish 18 | all | **n/a (100%)** |
| KinGPT-Woodpecker | normal | 591/600 (98.5%) |
| KinGPT-Beaver | normal | 170/600 (28.3%) |
| KinGPT-Chimera | normal | **597/600 (99.5%)** |
| OpenLLaMa 3B | normal | 33/600 (5.5%) |
| OpenLLaMa 3B | cheating | 120/600 (20.0%) |
| OpenLLaMa 3B | pass@K=10 | 309/600 (51.5%) |
| OpenLLaMa 3B | modulo | **488/600 (81.3%)** |
| RedPajama 3B | normal | 116/600 (19.3%) |
| RedPajama 3B | cheating | 19/600 (3.1%) |
| RedPajama 3B | pass@K=10 | 305/600 (50.8%) |
| RedPajama 3B | modulo | **572/600 (95.3%)** |
| ChessGPT-Base | normal | 502/600 (83.7%) |
| ChessGPT-Base | cheating | 486/600 (81.0%) |
| ChessGPT-Base | pass@K=10 | **597/600 (99.5%)** |
| ChessGPT-Base | modulo | 590/600 (98.3%) |
| ChessGPT-Chat | normal | 458/600 (76.3%) |
| ChessGPT-Chat | cheating | 398/600 (66.3%) |
| ChessGPT-Chat | pass@K=10 | 569/600 (94.8%) |
| ChessGPT-Chat | modulo | **584/600 (97.3%)** |

### KinGPT Theme-wide Comparison vs. C1-4B

**As of 5/16/2026,** the full sample of puzzles and checkpoints for C1-4B have not been published on [Z. Tang's GitHub repo for C1-4B](https://github.com/CSSLab/C1). I record first-move accuracy for both models KinGPT-Chimera and C1-4B, but note that the sample size for number of puzzles tested per theme differs between KinGPT (n=100) and C1-4B (n=25).

<ins>Key</ins>

**KinGPT -** [KINGPT-Chimera](https://github.com/ethanjtang/KinGPT)

**C1 -** [C1-4B](https://github.com/CSSLab/C1)

| Theme | KinGPT Accuracy (%) | C1 Accuracy (%) |
|:---|---:|---:|
| advancedPawn | 61.0 | 64.0 |
| attraction | 64.0 | 64.0 |
| backRankMate | 94.0 | 84.0 |
| capturingDefender | 65.0 | 56.0 |
| defensiveMove | 61.0 | 60.0 |
| deflection | 73.0 | 36.0 |
| discoveredAttack | 61.0 | 44.0 |
| doubleCheck | 74.0 | 52.0 |
| fork | 66.0 | 36.0 |
| hangingPiece | 81.0 | 64.0 |
| mateIn1 | 87.0 | 64.0 |
| mateIn2 | 85.0 | 56.0 |
| pin | 62.0 | 28.0 |
| promotion | 71.0 | 52.0 |
| queensideAttack | 70.0 | 68.0 |
| sacrifice | 56.0 | 60.0 |
| skewer | 75.0 | 52.0 |
| trappedPiece | 48.0 | 4.0 |
| xRayAttack | 75.0 | 52.0 |
| zugzwang* | 79.0 | 76.0 |
| **overall** | **70.4** | **53.6** |

*zugzwang is more commonly referred to colloquially as "zuggie"

## Citation

**Citation COMING SOON**
