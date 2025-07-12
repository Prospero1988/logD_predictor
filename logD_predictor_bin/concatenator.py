import os
import pandas as pd
from pathlib import Path

def concatenate(datasets, quiet=False):
    """
    Combine 1H and 13C DataFrames by concatenation and save the result to a CSV.

    Parameters:
        datasets (list): List of two DataFrames [1H, 13C].
        quiet (bool): If True, suppresses output.

    Returns:
        str: Path to the folder containing the concatenated file.
    """
    
    META_COLS = ["MOLECULE_NAME"]

    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    def split_meta_feat(df: pd.DataFrame):
        meta = df[META_COLS].copy()
        features = df.drop(columns=META_COLS).copy()
        return meta, features

    def renumber_features(df: pd.DataFrame) -> pd.DataFrame:
        meta, feats = split_meta_feat(df)
        renamed = {
            f"FEATURE_{i}": feats[col]
            for i, col in enumerate(feats.columns, start=1)
        }
        return pd.concat([meta, pd.DataFrame(renamed)], axis=1)

    def concat_features(df_h: pd.DataFrame, df_c: pd.DataFrame) -> pd.DataFrame:
        meta, feats_h = split_meta_feat(df_h)
        _, feats_c = split_meta_feat(df_c)
        feats_h.columns = [f"H_{col}" for col in feats_h.columns]
        feats_c.columns = [f"C_{col}" for col in feats_c.columns]
        feats_concat = pd.concat([feats_h, feats_c], axis=1)
        return renumber_features(pd.concat([meta, feats_concat], axis=1))

    if len(datasets) != 2:
        raise ValueError("Expected exactly two datasets: [1H, 13C].")

    df_1h, df_13c = datasets
    concat_dir = Path(os.getcwd()) / "hybrid_generated_ML_querries"
    concat_dir.mkdir(parents=True, exist_ok=True)

    combined = concat_features(df_1h, df_13c)
    output_path = concat_dir / "hybrid_1H13C.csv"
    combined.to_csv(output_path, index=False)

    verbose_print(f"Hybrid dataset saved to: {output_path}")
    verbose_print("\n✅ Combined shape after hybrid concat:", combined.shape, "\n")
    return combined, str(concat_dir)
