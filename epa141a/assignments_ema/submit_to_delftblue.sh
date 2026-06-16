#!/bin/bash -l
#
# submit_to_delftblue.sh — Assignment 5 MOEA job array for DelftBlue
#
# Submits 5 independent optimisation seeds in parallel.
# Each array task runs one seed on a single node using all available CPUs.
#
# Usage (from the epa141a/ root on DelftBlue):
#   sbatch assignments_ema/submit_to_delftblue.sh
#
# Monitor:
#   squeue -u $USER
#
# Cancel all tasks:
#   scancel -u $USER

# ── SLURM directives ──────────────────────────────────────────────────────────
#SBATCH --job-name="A5_JUSTICE_%a"
#SBATCH --time=04:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=4G
#SBATCH --array=1-5
#SBATCH --account=education-tpm-msc-epa
#SBATCH --output=results/logs/seed_%a_%j.out
#SBATCH --error=results/logs/seed_%a_%j.err

# ── Seeds — one per array task ────────────────────────────────────────────────
# These match the defaults in run_optimization_local.py.
# Do not change them unless your TA instructs you to.
seeds=(0 9845531 1644652 3569126 6075612 521475)   # index 0 unused; array starts at 1
SEED=${seeds[$SLURM_ARRAY_TASK_ID]}

# ── Configuration ─────────────────────────────────────────────────────────────
NFE=50000          # Function evaluations per seed (same as local run)
N_ENSEMBLES=50     # FAIR ensemble members (5× more than local run — HPC can handle it)
POPULATION=100     # MOEA population size

# ── Environment setup ─────────────────────────────────────────────────────────
module load 2023r1
module load miniconda3

unset CONDA_SHLVL
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate epa141a

# ── Run ───────────────────────────────────────────────────────────────────────
echo "========================================================"
echo "  Array task : $SLURM_ARRAY_TASK_ID"
echo "  Seed       : $SEED"
echo "  NFE        : $NFE"
echo "  Ensembles  : $N_ENSEMBLES"
echo "  CPUs       : $SLURM_CPUS_PER_TASK"
echo "  Node       : $SLURMD_NODENAME"
echo "========================================================"

mkdir -p results/logs

python model_answers_ema/run_optimization_local.py \
    --seeds $SEED \
    --nfe $NFE \
    --n_ensembles $N_ENSEMBLES \
    --n_processes $SLURM_CPUS_PER_TASK \
    --population $POPULATION \
    --output_dir results

echo "Seed $SEED finished."
