#!/bin/bash
#SBATCH -p public ## Partition
#SBATCH -q public  ## QOS
#SBATCH -N 1      ## Number of Sol Nodes
#SBATCH -c 32    ## Number of Cores
#SBATCH --mem=64G  ## Memory (GB)
#SBATCH --time=1000   ## Minutes of compute
#SBATCH -G 1 ## Number of GPUs
#SBATCH --job-name=gambit-test-all-models
#SBATCH --output=slurm.%j.out  ## job /dev/stdout record (%j expands -> jobid)
#SBATCH --error=slurm.%j.err   ## job /dev/stderr record
#SBATCH --export=NONE          ## keep environment clean
#SBATCH --mail-type=END,FAIL   ## notify <asurite>@asu.edu for any job state change

# ------------------------------
# SCRIPT SETUP
# ------------------------------

# create and load env
module load mamba/latest
mamba create -n gambit-env python=3.9 -y
source activate gambit-env

# dependencies
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate python-chess

# UNLEASH THE BIG FISH
chmod +x ./stockfish_compiled

# ------------------------------
# MAIN SCRIPT
# ------------------------------

# run the script 
python3 -u eval_all_models.py

