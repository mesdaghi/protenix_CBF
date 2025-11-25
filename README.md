# protenix_CBF
How to run protenix on CBF Cluster
# protenix_CBF

**Running Protenix on the CBF Cluster**

---

## FASTA → Protenix JSON Converter

This Python script converts multi-sequence **FASTA** files into **Protenix-compatible JSON** format.  
Each sequence is stored as a `proteinChain` object with its **UniProt accession** (when available).

---

## ✨ Features

- Handles **multi-FASTA** files  
- Extracts **UniProt accessions** from headers, e.g.:  
  - `>sp|P12345|PROT_HUMAN`  
  - `>tr|Q9XYZ1|...`  
- Falls back to the first token if no pipe (`|`) format is present  
- Produces clean, indented JSON ready for Protenix workflows  
- Can **split large JSON files into smaller chunks** for array jobs or batch processing  

---

## 📦 Requirements

- Python 3.7+  
- No external dependencies (standard library only)  

---

## 🚀 Usage

Convert a FASTA file to Protenix JSON:

```bash
python fasta_to_protenix_json_all.py input.fasta output.json
```

---

### Batch Processing with SLURM

A SLURM script (`run_protenix_array.sh`) is included for batch processing JSON chunks.  

**How it works:**  

1. Activates a Conda environment containing Protenix  
2. Detects all JSON chunks in `./json/`  
3. Each SLURM array task processes one chunk  
4. Outputs predictions to `./mouse_all/`  
5. Measures runtime per chunk  

**Submitting the SLURM Array Job:**

```bash
# Count the number of JSON chunks
NUM_CHUNKS=$(ls ./json/ALL_mouse_chunk_*.json | wc -l)

# Submit array job (1 task per chunk)
sbatch --array=1-$NUM_CHUNKS run_protenix_array.sh
```
