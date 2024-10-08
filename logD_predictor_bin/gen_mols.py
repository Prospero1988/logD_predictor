import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from tqdm import tqdm

def generate_mol_files(csv_path):
    """
    Generates .mol files from SMILES strings provided in a CSV file.

    Parameters:
    - csv_path (str): Path to the input CSV file containing 'MOLECULE_NAME'
                      and 'SMILES' columns.

    Returns:
    - mols_directory (str): Path to the directory where generated .mol files
                            are stored.
    """
    mols_directory = os.path.join(os.getcwd(), "mols")

    if not os.path.exists(mols_directory):
        os.makedirs(mols_directory)
        print(f"\nCreated directory: {mols_directory}")

    try:
        data = pd.read_csv(csv_path)
        if 'MOLECULE_NAME' not in data.columns or 'SMILES' not in data.columns:
            raise ValueError("CSV must contain 'MOLECULE_NAME' and 'SMILES' columns.")

        file_count = 0  # Counter for successfully generated .mol files
        error_file_count = 0  # Counter for .mol files with errors

        print("\nGenerating *.mol files ...")

        for index, row in tqdm(data.iterrows(), total=len(data), bar_format="Generating structures: {n_fmt}/{total_fmt}"):
            try:
                name = row['MOLECULE_NAME']
                smiles = row['SMILES']
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"Invalid SMILES string: {smiles}")

                mol = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol, randomSeed=0xf00d)
                
                # Optimize the molecule with at least 2000 cycles and convergence threshold
                # AllChem.UFFOptimizeMolecule(mol, maxIters=2000, vdwThresh=15.0, confId=-1, ignoreInterfragInteractions=True)
                
                AllChem.Compute2DCoords(mol)

                mol_file_path = os.path.join(mols_directory, f"{name}.mol")
                with open(mol_file_path, 'w') as f:
                    f.write(Chem.MolToMolBlock(mol, forceV3000=True))

                file_count += 1  # Increment counter for successful files

            except Exception as e:
                # Save the molecule even if there was error during processing
                mol_file_path = os.path.join(mols_directory, f"{row['MOLECULE_NAME']}_error.mol")
                with open(mol_file_path, 'w') as f:
                    if mol:
                        f.write(Chem.MolToMolBlock(mol, forceV3000=True))
                    else:
                        f.write(f"{name} could not be processed due to an error: {e}")
                tqdm.write(f"Error processing row {index + 1} ({name}): {e}")
                error_file_count += 1  # Increment counter for error files

        print(f"\nGenerated {file_count} .mol files in the folder '{mols_directory}'.")
        print(f"Generated {error_file_count} .mol files with errors (saved as *_error.mol).")

    except FileNotFoundError:
        print(f"File not found: {csv_path}")
    except pd.errors.EmptyDataError:
        print(f"File is empty: {csv_path}")
    except pd.errors.ParserError:
        print(f"Error parsing CSV file: {csv_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return mols_directory
