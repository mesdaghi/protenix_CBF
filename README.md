# protenix_CBF
How to run protenix on CBF Cluster
# FASTA → Protenix JSON Converter

A simple Python script to convert multi-sequence **FASTA** files into **Protenix-compatible JSON** format.  
Each sequence is saved with its UniProt accession (when available) and formatted as a `proteinChain` object.

---

## ✨ Features

- Supports **multi-FASTA** files
- Automatically extracts **UniProt accessions** from headers like:
  - `>sp|P12345|PROT_HUMAN`
  - `>tr|Q9XYZ1|...`
- Falls back to the first token of the header if no pipe (`|`) format is found
- Outputs clean, indented JSON ready for Protenix workflows
- Supports **splitting large JSON files into smaller chunks** for array jobs or batch processing

---

## 📦 Requirements

- Python 3.7+
- No external dependencies (standard library only)

---

## 🚀 Usage

```bash
python fasta_to_protenix_json_all.py input.fasta output.json

---
## 🚀 Also
A SLURM script (run_protenix_array.sh) is provided for batch processing JSON chunks:
How it works:
Activates a conda environment containing Protenix
Detects all JSON chunks in ./json/
Each SLURM array task processes one chunk
Outputs predictions to ./mouse_all/
Measures runtime per chunk

Submitting the SLURM Array Job
# Count the number of JSON chunks
NUM_CHUNKS=$(ls ./json/ALL_mouse_chunk_*.json | wc -l)

# Submit array job (1 task per chunk)
sbatch --array=1-$NUM_CHUNKS run_protenix_array.sh

