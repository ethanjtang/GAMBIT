#!/bin/bash 
#SBATCH -p general ## Partition
#SBATCH -q public  ## QOS
#SBATCH -N 1      ## Number of Sol Nodes
#SBATCH -c 16     ## Number of Cores
#SBATCH --mem=64G  ## Memory (GB)
#SBATCH --time=10000  ## Minutes of compute
#SBATCH -G 1        ## Number of GPUs
#SBATCH --job-name=patzerLM-finetuning
#SBATCH --output=slurm.%j.out  ## job /dev/stdout record (%j expands -> jobid)
#SBATCH --error=slurm.%j.err   ## job /dev/stderr record 
#SBATCH --export=NONE          ## keep environment clean
#SBATCH --mail-type=ALL        ## notify <asurite>@asu.edu for any job state change

echo "=========================================="
echo "PatzerLM Finetuning (open_llama_3b) Script"
echo "=========================================="

# Load environment
module load mamba/latest

# Install dependencies
echo "Installing mamba stuffs"
if ! mamba env list | grep -q "patzer-env"; then
    echo "Creating new mamba environment patzer-env"
    mamba create -y -n patzer-env python=3.10
fi

# Activate env and install dependencies
source activate patzer-env
echo "Installing Python stuffs"
pip install torch transformers datasets accelerate sentencepiece

# Save HF models and weights and stuff to scratch
# (to not use up all of my home directory storage)
export HF_HOME=/scratch/ejtang/.cache/huggingface

# Run PatzerLM finetuning script
python -u finetune.py
