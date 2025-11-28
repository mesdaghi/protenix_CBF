# -*- coding: utf-8 -*-
"""
Harvest ESMfold/AlphaFold CIF data
----------------------------------
Recursively searches subdirectories for CIF files inside paths like:
    ./x/seed_*/predictions/
Extracts per-residue pLDDT statistics and saves them into a TSV file.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from Bio.PDB import MMCIFParser
import sys
import argparse


def progress_bar(progress, total):
    """Simple ASCII progress bar."""
    percent = (100 * progress / float(total))
    bar = "█" * int(percent) + "-" * (100 - int(percent))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


def get_cif_files(parent_directory):
    parent = Path(parent_directory)
    files = list(parent.glob("**/*.cif"))
    print(f"🔍 Found {len(files)} CIF files under {parent.resolve()}")
    return files


def parse_structure(file_path):
    """Parse CIF structure file with BioPython."""
    parser = MMCIFParser(QUIET=True)
    return parser.get_structure(Path(file_path).stem, str(file_path))


def get_esmfold_stats(file_path):
    """Extract sequence and pLDDT stats from a CIF structure."""
    structure = parse_structure(file_path)

    d3to1 = {
        'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
        'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
        'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
        'ALA': 'A', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'
    }

    residue_plddt = []
    seq = []

    for model in structure:
        for chain in model:
            for residue in chain:
                # skip heteroatoms (e.g., water, ligands)
                if residue.id[0] != " ":
                    continue
                if residue.resname not in d3to1:
                    continue
                seq.append(d3to1[residue.resname])
                res_plddts = [atom.get_bfactor() for atom in residue]
                residue_plddt.append(np.mean(res_plddts))

    stats_dict = {
        'gene_name': Path(file_path).stem,
        'peptide_length': len(residue_plddt),
        'residue_plddt': list(residue_plddt),
        'residue_plddt_mean': np.mean(residue_plddt) if residue_plddt else np.nan,
        'residue_plddt_median': np.median(residue_plddt) if residue_plddt else np.nan,
        'residue_plddt_min': np.min(residue_plddt) if residue_plddt else np.nan,
        'residue_plddt_max': np.max(residue_plddt) if residue_plddt else np.nan,
        'residue_plddt_50': len([v for v in residue_plddt if 50 <= v < 60]),
        'residue_plddt_60': len([v for v in residue_plddt if 60 <= v < 70]),
        'residue_plddt_70': len([v for v in residue_plddt if 70 <= v < 80]),
        'residue_plddt_80': len([v for v in residue_plddt if 80 <= v < 90]),
        'residue_plddt_90': len([v for v in residue_plddt if v >= 90]),
        'total_residue_plddt_over_80': len([v for v in residue_plddt if v >= 80]),
        'residue_plddt_count_tp': len([i for i in residue_plddt if i > 60]),
        'residue_plddt_count_fp': len([i for i in residue_plddt if i < 25]),
    }

    return stats_dict


def main():
    parser = argparse.ArgumentParser(
        description="Harvest ESMfold/AlphaFold CIF files recursively"
    )
    parser.add_argument('-d', '--directory', required=True,
                        help='Parent directory containing seed_* subdirectories')
    parser.add_argument('-o', '--outputprefix', required=True,
                        help='Prefix for the output .tsv file')

    args = parser.parse_args()
    parent_directory = args.directory
    output = args.outputprefix

    print(f'Searching for CIF files in {parent_directory} ...')
    sys.tracebacklimit = 0

    files_list = get_cif_files(parent_directory)
    if not files_list:
        print("⚠️ No CIF files found. Check your directory structure and path.")
        return

    rows = []
    for index, file_path in enumerate(files_list):
        rows.append(get_esmfold_stats(file_path))
        progress_bar(index + 1, len(files_list))

    df = pd.DataFrame(rows)
    df.to_csv(output + '.tsv', sep='\t', index=None)
    print(f"\nDone! Found {len(files_list)} CIF files. Results saved to {output}.tsv")


if __name__ == "__main__":
    main()

