# GAMBIT

**arXiv link COMING SOON**

[![GitHub](https://img.shields.io/badge/GitHub-KINGPT-black.svg?style=for-the-badge)](https://github.com/ethanjtang/KINGPT) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-KINGPT-yellow?style=for-the-badge)](https://huggingface.co/ethanjtang/KINGPT) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-Puzzles-yellow?style=for-the-badge)](https://huggingface.co/datasets/ethanjtang/GAMBIT-lichess-puzzle-positions) <br>
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-SF18%20Selfplay-yellow?style=for-the-badge)](https://huggingface.co/datasets/ethanjtang/GAMBIT-stockfish18-selfplay) <br>


> <ins>G</ins>ener<ins>a</ins>lization or <ins>M</ins>emorization? <ins>B</ins>r<ins>i</ins>ttleness <ins>T</ins>esting for Chess-Trained Language Models

### Evaluations

Training for KINGPT variants was conducted on a 1x A100 GPU node on the ASU Sol Supercomputer.

Inference for Stockfish 18 and KINGPT variants was conducted on my personal 2019 computer with a Ryzen 7 5800X, 32 GB DDR4 2133 MHz (yuck!) RAM, and GTX 1060 6GB.

Inference for Open LLaMa 3B and ChessGPT model variants were conducted on a Lambda Labs 1xH100 GPU node.

## Results

### Models

| Name | Model |
|:---|:---|
| Stockfish 18 | [Stockfish 18](https://stockfishchess.org/) |
| KINGPT | [KINGPT](https://huggingface.co/ethanjtang/KINGPT) |
| Open LLaMa | [Open LLaMa 3B V1](https://huggingface.co/openlm-research/open_llama_3b) |
| ChessGPT-Base | [ChessGPT Base V1](https://huggingface.co/Waterhorse/chessgpt-base-v1) |
| ChessGPT-Chat | [ChessGPT Chat V1](https://huggingface.co/Waterhorse/chessgpt-chat-v1) |

### Overall Model Accuracy

Overall accuracy = number of correct responses / total number of positions.

A puzzle is considered solved correctly if a model generates a correct response to ALL puzzle positions.

Puzzle accuracy = number of correct responses to puzzles / total number of puzzles

| Model | Inference Type | Puzzle Accuracy | Overall Accuracy |
|:---|:---|---:|---:|
| Stockfish 18, Base | depth=20 | 300/300 (100.0%) | 600/600 (100.0%) |
| Stockfish 18, Base | time=0.05s | 300/300 (100.0%) | 600/600 (100.0%) |
| Stockfish 18, Level 0 | depth=20 | 192/300 (64.0%) | 476/600 (79.3%) |
| KINGPT-Woodpecker | normal | 217/300 (72.3%) | 492/600 (82.0%) |
| KINGPT-Beaver* | normal | 3/300 (1.0%) | 10/600 (1.7%) |
| KINGPT-Chimera | normal | 225/300 (75.0%) | 510/600 (85.0%) |
| Open LLaMa 3B | normal | 0/300 (0.0%) | 1/600 (0.2%) |
| Open LLaMa 3B | cheating | 5/300 (1.7%) | 13/600 (2.2%) |
| Open LLaMa 3B | pass@K=10 | 3/300 (1.0%) | 20/600 (3.3%) |
| Open LLaMa 3B | modulo | 8/300 (2.7%) | 70/600 (11.7%) |
| ChessGPT-Base | normal | 46/300 (15.3%) | 166/600 (27.7%) |
| ChessGPT-Base | cheating | 48/300 (16.0%) | 182/600 (30.3%) |
| ChessGPT-Base | pass@K=10 | 115/300 (38.3%) | 353/600 (58.8%) |
| ChessGPT-Base | Modulo | 54/300 (18.0%) | 202/600 (33.7%) |
| ChessGPT-Chat | normal | 30/300 (10.0%) | 126/600 (21.0%) |
| ChessGPT-Chat | cheating | 37/300 (12.3%) | 153/600 (25.5%) |
| ChessGPT-Chat | pass@K=10 | 61/300 (20.3%) | 227/600 (37.8%) |
| ChessGPT-Chat | modulo | 41/300 (13.7%) | 176/600 (29.3%) |

*KINGPT-Beaver acts as a (approximate) proxy for Zhang et. al. 2025's ChessLLM from ["Complete Chess Games Enable LLM Become Chess Master"](https://arxiv.org/abs/2501.17186v2)

### Overall Model Accuracy

Sanity measures how frequently a model chooses a legal/valid move in a given position.

Sanity = 1 / (number of invalid parses / total number of positions)

| Model | Inference Type | Sanity |
|:---|:---|---:|
| Stockfish 18 | all | n/a (100%) |
| KINGPT-Woodpecker | normal | 591/600 (98.5%) |
| KINGPT-Beaver* | normal | 170/600 (28.3%) |
| KINGPT-Chimera | normal | 597/600 (99.5%) |
| Open LLaMa 3B | normal | 33/600 (5.5%) |
| Open LLaMa 3B | cheating | 120/600 (20.0%) |
| Open LLaMa 3B | pass@K=10 | 309/600 (51.5%) |
| Open LLaMa 3B | modulo | 488/600 (81.3%) |
| ChessGPT-Base | normal | 502/600 (83.7%) |
| ChessGPT-Base | cheating | 486/600 (81.0%) |
| ChessGPT-Base | pass@K=10 | 597/600 (99.5%) |
| ChessGPT-Base | modulo | 590/600 (98.3%) |
| ChessGPT-Chat | normal | 458/600 (76.3%) |
| ChessGPT-Chat | cheating | 398/600 (66.3%) |
| ChessGPT-Chat | pass@K=10 | 569/600 (94.8%) |
| ChessGPT-Chat | modulo | 584/600 (97.3%) |

*KINGPT-Beaver acts as a (approximate) proxy for Zhang et. al. 2025's ChessLLM from ["Complete Chess Games Enable LLM Become Chess Master"](https://arxiv.org/abs/2501.17186v2)

### Comparison vs. C1

KINGPT vs. C1

Note that, **as of 4/27/2026,** the full sample of puzzles has not been published on [Z. Tang's GitHub repo for C1](https://github.com/CSSLab/C1). This is a rough comparison since my sampling method takes the average score across N=100 puzzles without regard for difficulty level.

KINGPT tests for overall accuracy while Zhang's model C1 tests for first-move accuracy for puzzles. I think overall accuracy is a more accurate representation of chess puzzle proficiency (finding the first move of a puzzle is usually easier than the followup*).

*This is anecdotal from my own experience solving 40k+ rated puzzles on Chess.com

| Theme | KINGPT Accuracy (%) | C1 Accuracy (%) |
|:---|:---|:---|
| advancedPawn | 68.3 |   |
| attraction | 76.1 |   |
| backRankMate | 96.5 |   |
| capturingDefender | 74.4 |   |
| defensiveMove | 60.1 |   |
| deflection | 75.9 |   |
| discoveredAttack | 69.7 |   |
| doubleCheck | 75.9 |   |
| fork | 71.4 |   |
| hangingPiece | 72.6 |   |
| mateIn1 | 87.0 |   |
| mateIn2 | 89.0 |   |
| pin | 69.3 |   |
| promotion | 76.1 |   |
| queensideAttack | 75.9 |   |
| sacrifice | 72.3 |   |
| skewer | 78.3 |   |
| trappedPiece | 67.5 |   |
| xRayAttack | 84.6 |   |
| zugzwang* | 81.5 |   |
| overall | 75.3 |  |

*zugzwang is more commonly referred to colloquially as "zuggie"
