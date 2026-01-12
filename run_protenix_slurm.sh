#!/bin/bash -l
#SBATCH -J protenix_Cauris6684       # Job name
#SBATCH -o protenix_predict_%A_%a.out      # Stdout (%A=jobID, %a=array index)
#SBATCH -e protenix_predict_%A_%a.err      # Stderr
#SBATCH -p gpu
#SBATCH --ntasks=1
#SBATCH -c 8
#SBATCH --gres=gpu:1
#SBATCH -t 2-00:00:00
#SBATCH --mail-user=username@liverpool.ac.uk
#SBATCH --mail-type=ALL

# setup
module load python/3.10
source ~/miniconda3/etc/profile.d/conda.sh
conda activate protenix_env

export DS_BUILD_OPS=0
export PROTENIX_CACHE=/home/shahmes/protenix_cache

# Debug info
echo "===== DEBUG INFORMATION ====="
echo "PROTENIX_CACHE = $PROTENIX_CACHE"

python - << 'EOF'
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
EOF

echo "Checkpoint files:"
ls -lh $PROTENIX_CACHE/checkpoint/

echo "CCD cache files:"
ls -lh $PROTENIX_CACHE/ccd_cache/
echo "=============================="


# find JSON chunks

CHUNKS=(./FungiDB-68_Cauris6684_AnnotatedProteins_chunk_*.json)
NUM_CHUNKS=${#CHUNKS[@]}

if [ $NUM_CHUNKS -eq 0 ]; then
    echo "No JSON chunks found. Exiting."
    exit 1
fi

# Map array index to chunk
INPUT_JSON=${CHUNKS[$SLURM_ARRAY_TASK_ID-1]}
echo "Running chunk: $INPUT_JSON"


# Run Protenix

start_time=$(date +%s)

protenix predict \
    --input $INPUT_JSON \
    --out_dir ./Cauris6684_all_one \
    --seeds 101 \
    --model_name "protenix_mini_esm_v0.5.0" \
    --use_msa false \
    --sample 1 \

end_time=$(date +%s)
runtime=$((end_time - start_time))
hours=$((runtime / 3600))
minutes=$(((runtime % 3600) / 60))
seconds=$((runtime % 60))
echo "Chunk runtime: ${hours}h ${minutes}m ${seconds}s"

