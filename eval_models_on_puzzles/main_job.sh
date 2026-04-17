#!/bin/bash
#SBATCH -p public ## Partition
#SBATCH -q class  ## QOS
#SBATCH -N 1      ## Number of Sol Nodes
#SBATCH -c 32    ## Number of Cores
#SBATCH --mem=64G  ## Memory (GB)
#SBATCH --time=960   ## Minutes of compute
#SBATCH -G 1 ## Number of GPUs
#SBATCH --job-name=gambit-test-all-models
#SBATCH --output=slurm.%j.out  ## job /dev/stdout record (%j expands -> jobid)
#SBATCH --error=slurm.%j.err   ## job /dev/stderr record
#SBATCH --export=NONE          ## keep environment clean
#SBATCH --mail-type=END,FAIL   ## notify <asurite>@asu.edu for any job state change

# ------------------------------
# SCRIPT SETUP
# ------------------------------

# load modules
module load mamba/latest
module load gcc/15.2.0  # for some reason, stockfish needs this module to load on linux hee hee ha ha AAAAAAAAAAAAAaaaa

# create and activate env
mamba create -n gambit-env python=3.9 -y
source activate gambit-env

# dependencies
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install transformers accelerate python-chess numpy sentencepiece

# UNLEASH THE BIG FISH
chmod +x ./stockfish_18_compiled

# clean conda env
conda clean -a -y

# set HF Home so your script does not use up all of your storage
export HF_HOME="/scratch/ejtang/.cache/huggingface"

# ------------------------------
# MAIN SCRIPT
# ------------------------------

# run the script 
python3 -u eval_all_models.py

