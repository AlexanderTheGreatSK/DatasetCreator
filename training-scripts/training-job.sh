#!/bin/bash
#
#$ -S /bin/bash
#$ -N whisper-dialects-cz
#$ -o /mnt/matylda6/xokruc00/training-scripts/out.txt
#$ -e /mnt/matylda6/xokruc00/training-scripts/err.txt
#$ -q long.q@@gpu
#$ -l gpu=1,gpu_ram=24G,matylda6=5
#$ -l ram_free=16G,tmp_free=20G
#

#export OMP_NUM_THREADS=1
#export MKL_NUM_THREADS=1

# Job should finish in about 2 days
ulimit -t 200000

# Enable opening multiple files
ulimit -n 4096

# Enable to save bigger checkpoints
ulimit -f unlimited
ulimit -v unlimited
ulimit -u 4096


source /mnt/matylda6/xokruc00/alex-conda-env/bin/activate

export HF_HOME=/mnt/matylda6/xokruc00/HF/cache/

export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_EVALUATE_OFFLINE=1
export CUDA_VISIBLE_DEVICES=$(/mnt/matylda6/xokruc00/training-scripts/free-gpus.sh 1)

cd /mnt/matylda6/xokruc00/training-scripts/
python /mnt/matylda6/xokruc00/training-scripts/training-script.py
