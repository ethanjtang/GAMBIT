# GAMBIT

> <ins>G</ins>ener<ins>a</ins>lization or <ins>M</ins>emorization? <ins>B</ins>r<ins>i</ins>ttleness <ins>T</ins>esting for Chess-Trained Language Models

## Results

### Key

Open LLaMa - Open LLaMa 3B V1 - LINK
ChessGPT-Base - ChessGPT Base V1 - LINK
ChessGPT-Chat - ChessGPT Chat V1 - LINK

### Overall Model Accuracy

Overall accuracy - number of correct responses / total number of positions

A puzzle is considered solved correctly if a model generates a correct response to ALL puzzle positions.

Puzzle accuracy - number of correct responses to puzzles / total number of puzzles

| Model | Prompt Type | Puzzle Accuracy | Overall Accuracy |
|:---|:---|---:|---:|
| Open LLaMa 3B | normal | 0/300 (0.0%) | 1/600 (0.2%) |
| Open LLaMa 3B | cheating | 5/300 (1.7%) | 13/600 (2.2%) |
| ChessGPT-Base | normal | 46/300 (15.3%) | 166/600 (27.7%) |
| ChessGPT-Base | cheating | 48/300 (16.0%) | 182/600 (30.3%) |
| ChessGPT-Chat | normal | 30/300 (10.0%) | 126/600 (21.0%) |
| ChessGPT-Chat | cheating | 37/300 (12.3%) | 153/600 (25.5%) |

Sanity measures how frequently a model chooses a legal/valid move in the given position.
Sanity = 1 / (number of invalid parses / total number of positions)

| Model | Prompt Type |  Sanity |
|:---|:---|---:|
| Open LLaMa 3B | normal | 33/600 (5.5%) |
| Open LLaMa 3B | cheating | 120/600 (20.0%) |
| ChessGPT-Base | normal | 502/600 (83.7%) |
| ChessGPT-Base | cheating | 486/600 (81.0%) |
| ChessGPT-Chat | normal | 458/600 (76.3%) |
| ChessGPT-Chat | cheating | 398/600 (66.3%) |