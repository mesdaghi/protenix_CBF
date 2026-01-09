import os
import gemmi
import numpy as np
from multiprocessing import Pool, cpu_count
import pandas as pd
import pickle


OVERLAP_SIZE = 100
OVERLAP_PLDTT_DIFF_WARN = 20.0

def find_structure_file(predictions_dir):
    for f in os.listdir(predictions_dir):
        if f.endswith(".cif") or f.endswith(".pdb"):
            return os.path.join(predictions_dir, f)
    return None


def read_residue_plddt_ordered(file_path):
    """
    Returns list of per-residue mean pLDDT in sequence order
    """
    residues = []

    if file_path.endswith(".cif"):
        cif_doc = gemmi.cif.read_file(file_path)
        block = cif_doc.sole_block()
        atom_site = block.get_mmcif_category("_atom_site")

        current_res = None
        bvals = []

        for asym, seq, b in zip(
            atom_site["label_asym_id"],
            atom_site["label_seq_id"],
            atom_site["B_iso_or_equiv"]
        ):
            res_id = (asym, int(seq))

            if current_res is None:
                current_res = res_id

            if res_id != current_res:
                residues.append(float(np.mean(bvals)))
                bvals = []
                current_res = res_id

            bvals.append(float(b))

        if bvals:
            residues.append(float(np.mean(bvals)))

    else:  # PDB
        structure = gemmi.read_structure(file_path)
        for model in structure:
            for chain in model:
                for res in chain:
                    b_list = [atom.b_iso for atom in res]
                    if b_list:
                        residues.append(float(np.mean(b_list)))

    return residues



def collect_mean_plddt(dataset_path):
    dataset_name = os.path.basename(dataset_path)
    print(f"[START] Processing dataset: {dataset_name}", flush=True)

    is_split = dataset_name.endswith("_split")
    plddt_dict = {}

    if is_split:
        # locate *_all_one
        all_one_dir = None
        for item in os.listdir(dataset_path):
            p = os.path.join(dataset_path, item)
            if os.path.isdir(p) and item.endswith("_all_one"):
                all_one_dir = p
                break

        if all_one_dir is None:
            print(f"[SKIP] {dataset_name}: no *_all_one directory", flush=True)
            return dataset_name, {}

        subdirs = [
            d for d in os.listdir(all_one_dir)
            if os.path.isdir(os.path.join(all_one_dir, d))
            and (d.endswith("_A") or d.endswith("_B"))
        ]

        proteins = sorted(set(d[:-2] for d in subdirs))
        print(f"[INFO] {dataset_name}: found {len(proteins)} split proteins", flush=True)

        for idx, protein_id in enumerate(proteins, 1):
            try:
                a_dir = os.path.join(
                    all_one_dir, f"{protein_id}_A", "seed_101", "predictions"
                )
                b_dir = os.path.join(
                    all_one_dir, f"{protein_id}_B", "seed_101", "predictions"
                )

                if not (os.path.isdir(a_dir) and os.path.isdir(b_dir)):
                    continue

                a_file = find_structure_file(a_dir)
                b_file = find_structure_file(b_dir)
                if not a_file or not b_file:
                    continue

                a_res = read_residue_plddt_ordered(a_file)
                b_res = read_residue_plddt_ordered(b_file)

                if not a_res or not b_res:
                    continue

                overlap = min(OVERLAP_SIZE, len(a_res), len(b_res))

                a_overlap = a_res[-overlap:]
                b_overlap = b_res[:overlap]

                diffs = [abs(a - b) for a, b in zip(a_overlap, b_overlap)]
                mean_diff = float(np.mean(diffs))

                if mean_diff > OVERLAP_PLDTT_DIFF_WARN:
                    print(
                        f"[WARN] {dataset_name} | {protein_id}: "
                        f"large pLDDT mismatch in overlap "
                        f"(mean Δ={mean_diff:.1f} over {overlap} residues)",
                        flush=True
                    )

                merged_overlap = [max(a, b) for a, b in zip(a_overlap, b_overlap)]

                merged = (
                    a_res[:-overlap]
                    + merged_overlap
                    + b_res[overlap:]
                )

                plddt_dict[protein_id] = float(np.mean(merged))

            except Exception as e:
                print(f"[WARN] {protein_id}: split processing failed ({e})", flush=True)

            if idx % 50 == 0:
                print(f"[INFO] {dataset_name}: {idx}/{len(proteins)} processed", flush=True)

        print(f"[DONE] Finished dataset: {dataset_name} ({len(plddt_dict)} proteins)\n", flush=True)
        return dataset_name, plddt_dict

    all_one_dir = None
    for item in os.listdir(dataset_path):
        p = os.path.join(dataset_path, item)
        if os.path.isdir(p) and item.endswith("_all_one"):
            all_one_dir = p
            break

    if all_one_dir is None:
        print(f"[SKIP] {dataset_name}: no *_all_one directory", flush=True)
        return dataset_name, {}

    protein_dirs = [
        d for d in os.listdir(all_one_dir)
        if os.path.isdir(os.path.join(all_one_dir, d))
    ]

    print(f"[INFO] {dataset_name}: found {len(protein_dirs)} proteins", flush=True)

    for idx, protein_id in enumerate(protein_dirs, 1):
        try:
            predictions_dir = os.path.join(
                all_one_dir, protein_id, "seed_101", "predictions"
            )
            if not os.path.isdir(predictions_dir):
                continue

            file_path = find_structure_file(predictions_dir)
            if not file_path:
                continue

            residues = read_residue_plddt_ordered(file_path)
            if residues:
                plddt_dict[protein_id] = float(np.mean(residues))

        except Exception as e:
            print(f"[WARN] Could not read {protein_id}: {e}", flush=True)

        if idx % 50 == 0:
            print(f"[INFO] {dataset_name}: {idx}/{len(protein_dirs)} processed", flush=True)

    print(f"[DONE] Finished dataset: {dataset_name} ({len(plddt_dict)} proteins)\n", flush=True)
    return dataset_name, plddt_dict



if __name__ == "__main__":

    base_dir = os.getcwd()
    datasets = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    print("Datasets found:", [os.path.basename(d) for d in datasets], flush=True)

    pickle_file = "plddt_all_values.pkl"
    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as f:
            all_values_per_dataset = pickle.load(f)
        print(f" Loaded existing pLDDT values from {pickle_file}", flush=True)
    else:
        all_values_per_dataset = {}

    datasets_to_process = [
        d for d in datasets
        if os.path.basename(d) not in all_values_per_dataset
    ]

    if not datasets_to_process:
        print("No new datasets to process. Exiting.", flush=True)
        exit(0)

    print(
        f"Datasets to process: {[os.path.basename(d) for d in datasets_to_process]}",
        flush=True
    )

    n_workers = cpu_count()
    print(f"Using {n_workers} workers\n", flush=True)

    with Pool(n_workers) as pool:
        results = pool.map(collect_mean_plddt, datasets_to_process)

    for dataset_name, values_dict in results:
        if values_dict:
            all_values_per_dataset[dataset_name] = values_dict


    rows = []
    for species, protein_dict in all_values_per_dataset.items():
        for protein_id, mean_plddt in protein_dict.items():
            rows.append({
                "Species": species,
                "Protein_ID": protein_id,   # UniProt code preserved
                "Mean_pLDDT": mean_plddt
            })

    df = pd.DataFrame(rows)
    csv_file = "plddt_all_values.csv"
    df.to_csv(csv_file, index=False)
    print(f" Saved all mean pLDDT values to CSV: {csv_file}", flush=True)

    with open(pickle_file, "wb") as f:
        pickle.dump(all_values_per_dataset, f)
    print(f" Saved all mean pLDDT values to pickle: {pickle_file}", flush=True)

