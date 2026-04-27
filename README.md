# GAMBIT

> <ins>G</ins>ener<ins>a</ins>lization or <ins>M</ins>emorization? <ins>B</ins>r<ins>i</ins>ttleness <ins>T</ins>esting for Chess-Trained Language Models

## Results

### Key

Open LLaMa - Open LLaMa 3B V1 - LINK

ChessGPT-Base - ChessGPT Base V1 - LINK

ChessGPT-Chat - ChessGPT Chat V1 - LINK

### Overall Model Accuracy

Overall accuracy - number of correct responses / total number of positions.

A puzzle is considered solved correctly if a model generates a correct response to ALL puzzle positions.

Puzzle accuracy - number of correct responses to puzzles / total number of puzzles

| Model | Inference Type | Puzzle Accuracy | Overall Accuracy |
|:---|:---|---:|---:|
| Open LLaMa 3B | normal | 0/300 (0.0%) | 1/600 (0.2%) |
| Open LLaMa 3B | cheating | 5/300 (1.7%) | 13/600 (2.2%) |
| Open LLaMa 3B | pass@K=10 | 3/300 (1.0%) | 20/600 (3.3%) |
| Open LLaMa 3B | modulo | 8/300 (2.7%) | 70/600 (11.7%) |
| ChessGPT-Base | normal | 46/300 (15.3%) | 166/600 (27.7%) |
| ChessGPT-Base | cheating | 48/300 (16.0%) | 182/600 (30.3%) |
| ChessGPT-Base | pass@K=10 | 115/300 (38.3%) | 353/600 (58.8%) |
| ChessGPT-Base | Modulo | /300 (%) | 182/600 (%) |
| ChessGPT-Chat | normal | 30/300 (10.0%) | 126/600 (21.0%) |
| ChessGPT-Chat | cheating | 37/300 (12.3%) | 153/600 (25.5%) |
| ChessGPT-Chat | pass@K=10 | 61/300 (20.3%) | 227/600 (37.8%) |
| ChessGPT-Chat | modulo | 41/300 (13.7%) | 176/600 (29.3%) |

### Overall Model Accuracy

Sanity measures how frequently a model chooses a legal/valid move in the given position.

Sanity = 1 / (number of invalid parses / total number of positions)

| Model | Inference Type | Sanity |
|:---|:---|---:|
| Open LLaMa 3B | normal | 33/600 (5.5%) |
| Open LLaMa 3B | cheating | 120/600 (20.0%) |
| Open LLaMa 3B | pass@K=10 | 309/600 (51.5%) |
| Open LLaMa 3B | modulo | 488/600 (81.3%) |
| ChessGPT-Base | normal | 502/600 (83.7%) |
| ChessGPT-Base | cheating | 486/600 (81.0%) |
| ChessGPT-Base | pass@K=10 | 597/600 (99.5%) |
| ChessGPT-Base | modulo | /600 (%) |
| ChessGPT-Chat | normal | 458/600 (76.3%) |
| ChessGPT-Chat | cheating | 398/600 (66.3%) |
| ChessGPT-Chat | pass@K=10 | 569/600 (94.8%) |
| ChessGPT-Chat | modulo | 584/600 (97.3%) |