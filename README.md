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
**Process Models and Plot:**
process_models.py script is designed to process protein structure prediction datasets (AlphaFold-style) and compute the mean per-residue confidence score, pLDDT, for each protein. It starts by searching each dataset directory for structure files in .pdb or .cif format using gemmi, then reads the per-residue B-factors as a proxy for pLDDT, computing a mean score for each residue. For datasets where proteins are split into overlapping segments (denoted with _A and _B), it extracts the overlap region, compares the pLDDT values, warns if the difference exceeds a set threshold, and merges them by taking the maximum per residue in the overlap. For unsplit proteins, it simply reads the structure file and computes the mean pLDDT for the whole protein. The script can process multiple datasets in parallel using all available CPU cores, collects the results into a dictionary, and saves both a CSV file with species, protein IDs, and mean pLDDTs, and a pickle file for future use. Overall, it automates large-scale extraction and aggregation of confidence scores from structure prediction outputs, while handling split proteins and overlap validation.
This script visualizes pLDDT (per-residue confidence scores from protein structure predictions) distributions across multiple species using histograms and kernel density estimates (KDEs). It first loads precomputed pLDDT values from a pickle file, then constructs a global grid spanning the observed range of scores. Figure 1 shows a histogram of mean pLDDT values for all species. Figures 2 and 3 compute KDE curves for all species using two different libraries: StatsModels (KDEUnivariate) and SciPy (gaussian_kde), providing smooth density estimates.
