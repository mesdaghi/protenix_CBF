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

---

## 📦 Requirements

- Python 3.7+
- No external dependencies (standard library only)

---

## 🚀 Usage

```bash
python fasta_to_protenix_json_all.py input.fasta output.json

