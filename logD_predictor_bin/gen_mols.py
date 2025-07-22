#!/usr/bin/env python3
"""
Generate 2 D MOL files from SMILES strings.

Pipeline
--------
1.  Canonicalise the SMILES.
2.  Add explicit hydrogens.
3.  Try to embed a 3 D conformer with ETKDG (3 retries).
    • If ETKDG fails → fall back to RDKit CoordGen (2 D).
4.  Force a switch to OpenBabel for molecules that
    contain hyper-valent sulphur (valence > 4) or after an
    ETKDG failure.
    • obabel -d --gen2D strips wedge bonds and flattens the structure.
5.  Write a V3000 MOL file (2 D coordinates, no stereo wedges).
6.  Log errors to *mol_creation_error.log* and all fall-backs/
    warnings to *mol_creation_warning.log*.

Notes
-----
*   OpenBabel (`obabel`) must be on your system `PATH`
    (e.g. `conda install -c conda-forge openbabel`).
*   RDKit warnings are silenced via `RDLogger.DisableLog('rdApp.*')`.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from typing import List, Tuple

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, rdCoordGen

# Silence all RDKit log output (optional but recommended)
RDLogger.DisableLog("rdApp.*")

# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
ANSI_GREEN = "\033[38;5;46m"
ANSI_RED = "\033[38;5;196m"
ANSI_ORANGE = "\033[38;5;214m"
ANSI_RESET = "\033[0m"

PROGRESS_BAR_LEN = 25
MAX_ETKDG_RETRIES = 3
EMBED_RANDOM_SEED = 42


# ──────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────
def safe_embed_molecule(
    mol: Chem.Mol,
    max_retries: int = MAX_ETKDG_RETRIES,
    seed: int = EMBED_RANDOM_SEED,
) -> Tuple[Chem.Mol | None, str | None]:
    """
    Try ETKDG embedding up to *max_retries* times, fall back to CoordGen.

    Returns
    -------
    mol
        RDKit molecule with at least one conformer, or ``None`` on hard fail.
    warning
        ``None`` on ETKDG success, otherwise a human-readable note.
    """
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.maxAttempts = 100

    for _ in range(max_retries):
        mol.RemoveAllConformers()
        if AllChem.EmbedMolecule(mol, params) == 0:
            return mol, None  # ETKDG success

    try:
        rdCoordGen.AddCoords(mol)  # 2 D fallback
        return mol, f"ETKDG failed ({max_retries}x) → used CoordGen"
    except Exception as exc:  # pylint: disable=broad-except
        return None, f"ETKDG + CoordGen failed: {exc}"


def has_hypervalent_sulphur(mol: Chem.Mol) -> bool:
    """Return *True* if the molecule contains S with total valence > 4."""
    return any(
        atom.GetSymbol() == "S" and atom.GetTotalValence() > 4
        for atom in mol.GetAtoms()
    )


def openbabel_fallback(rdkit_mol: Chem.Mol, out_path: str) -> Tuple[bool, str | None]:
    """
    Run *obabel* -d --gen2D on *rdkit_mol*; write to *out_path*.

    Returns *(success, error_message)*.
    """
    with tempfile.NamedTemporaryFile(suffix=".mol", delete=False) as tmp:
        tmp.write(Chem.MolToMolBlock(rdkit_mol, forceV3000=True).encode())
        tmp_path = tmp.name

    cmd = ["obabel", tmp_path, "-O", out_path, "-d", "--gen2D"]
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        os.remove(tmp_path)
        return True, None
    except subprocess.CalledProcessError as exc:
        os.remove(tmp_path)
        return False, exc.stderr.decode().strip()


def canonical_smiles(smiles: str) -> str:
    """Return RDKit-canonical SMILES or raise *ValueError*."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return Chem.MolToSmiles(mol, canonical=True)


def print_progress(current: int, total: int) -> None:
    """Draw a coloured, in-place ASCII progress bar."""
    filled = int(PROGRESS_BAR_LEN * current / total)
    bar = ANSI_GREEN + "█" * filled + "-" * (PROGRESS_BAR_LEN - filled) + ANSI_RESET
    percent = int(100 * current / total)
    sys.stdout.write(f"\rProgress: |{bar}| {current}/{total} ({percent}%)")
    sys.stdout.flush()
    if current == total:
        print()  # newline


# ──────────────────────────────────────────────────────────────
# Extra “weird‑chemistry” detectors
# ──────────────────────────────────────────────────────────────
EXOTIC_VALENCE_LIMITS = {"S": 4, "P": 4, "As": 4, "Se": 4}
TRANSITION_METALS = {21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                     39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                     57, 72, 73, 74, 75, 76, 77, 78, 79}

def needs_openbabel(mol: Chem.Mol) -> bool:
    """
    Return True for molecules that should bypass RDKit-only handling.
    Triggers:
        • hyper-valent S/P/As/Se
        • any transition metal
        • radicals
        • too many heavy atoms (> 150)
        • dot-disconnected SMILES fragments
    """
    # hyper‑valent chalcogens / pnictogens
    if any(
        a.GetSymbol() in EXOTIC_VALENCE_LIMITS
        and a.GetTotalValence() > EXOTIC_VALENCE_LIMITS[a.GetSymbol()]
        for a in mol.GetAtoms()
    ):
        return True

    # transition metals
    if any(a.GetAtomicNum() in TRANSITION_METALS for a in mol.GetAtoms()):
        return True

    # radicals
    if any(a.GetNumRadicalElectrons() for a in mol.GetAtoms()):
        return True

    # very large molecules
    if mol.GetNumHeavyAtoms() > 150:
        return True

    return False


def is_dot_smiles(smiles: str) -> bool:
    """True if SMILES contains disconnected fragments (“dot-SMILES”)."""
    return "." in smiles

# ──────────────────────────────────────────────────────────────
# Main routine
# ──────────────────────────────────────────────────────────────
def generate_mol_files(csv_path: str, strict_mode: bool = True) -> str:
    """
    Convert SMILES in *csv_path* to flat MOL files.

    Parameters
    ----------
    csv_path
        CSV with columns ``MOLECULE_NAME`` and ``SMILES``.
    strict_mode
        If *True*, reject molecules whose 3D coords all sit at (0, 0, 0).

    Returns
    -------
    str
        Output directory path.
    """
    output_dir = os.path.join(os.getcwd(), "mols")
    os.makedirs(output_dir, exist_ok=True)

    errors: List[str] = []
    warnings: List[str] = []

    data = pd.read_csv(csv_path)
    data = data.drop_duplicates(subset="MOLECULE_NAME", keep="first")

    total = len(data)
    last_update = 0
    saved_files = 0

    print("\nGenerating *.mol files …\n")

    for idx, row in enumerate(data.itertuples(index=False), start=1):
        name, raw_smiles = row.MOLECULE_NAME, row.SMILES
        try:
            smiles = canonical_smiles(raw_smiles)
            mol = Chem.AddHs(Chem.MolFromSmiles(smiles))

            # ── RDKit embedding ───────────────────────────────────────────
            mol, warn_msg = safe_embed_molecule(mol)
            if mol is None:
                raise ValueError(warn_msg)
            if warn_msg:
                warnings.append(f"{name}: {warn_msg}")

            # ---------- Decide if this molecule must go through OpenBabel -------------
            force_babel = False
            reason_list: List[str] = []

            if needs_openbabel(mol):
                force_babel = True
                reason_list.append("exotic atom / metal / radical / size")

            if is_dot_smiles(smiles):
                force_babel = True
                reason_list.append("dot-SMILES (disconnected fragments)")

            if warn_msg:          # ETKDG failed earlier → CoordGen only
                force_babel = True
                reason_list.append("ETKDG failure")

            if force_babel:
                warnings.append(f"{name}: OpenBabel fallback → {', '.join(reason_list)}")

            # ── Basic 3D sanity check ───────────────────────────────────
            conf = mol.GetConformer()
            if all(conf.GetAtomPosition(i).Length() < 0.1 for i in range(mol.GetNumAtoms())):
                raise ValueError("All atoms at origin (invalid 3D)")

            # ── Flatten copy to 2D; strip wedge bonds ───────────────────
            mol2d = Chem.Mol(mol)
            AllChem.Compute2DCoords(mol2d)
            Chem.RemoveStereochemistry(mol2d)

            out_path = os.path.join(output_dir, f"{name}.mol")

            # ── Write via RDKit or OpenBabel ─────────────────────────────
            if not force_babel:
                with open(out_path, "w", encoding="utf-8") as handle:
                    handle.write(Chem.MolToMolBlock(mol2d, forceV3000=True))
            else:
                success, ob_error = openbabel_fallback(mol2d, out_path)
                if not success:
                    raise ValueError(f"OpenBabel fallback failed: {ob_error}")

            saved_files += 1

        except Exception as exc:  # pylint: disable=broad-except
            errors.append(
                f"Molecule: {name}\nSMILES: {raw_smiles}\nError: {exc}\n"
            )

        # ── Progress bar update ─────────────────────────────────────────
        progress = (idx / total) * 100
        if idx != total and progress - last_update >= 1:
            print_progress(idx, total)
            last_update = progress

    print_progress(total, total)

    # ── Write logs ─────────────────────────────────────────────────────
    if errors:
        with open("mol_creation_error.log", "w", encoding="utf-8") as fh_err:
            fh_err.write("==== MOL CREATION ERRORS ====\n\n" + "\n".join(errors))
    if warnings:
        with open("mol_creation_warning.log", "w", encoding="utf-8") as fh_warn:
            fh_warn.write("==== MOL CREATION WARNINGS ====\n\n" + "\n".join(warnings))

    # ── Summary to console ─────────────────────────────────────────────
    print(f"\n{ANSI_GREEN}Generated {saved_files} MOL files in '{output_dir}'.{ANSI_RESET}")
    print(f"{ANSI_GREEN}Failed to generate {len(errors)} MOL files.{ANSI_RESET}")
    if errors:
        print(f"{ANSI_RED}See 'mol_creation_error.log' for details.{ANSI_RESET}")
    if warnings:
        print(f"{ANSI_ORANGE}See 'mol_creation_warning.log' for fallbacks.{ANSI_RESET}")

    return output_dir
