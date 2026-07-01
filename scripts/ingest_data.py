from pathlib import Path
import pandas as pd


# ==========================
# Paths
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "data" / "raw" / "cloud_budget_2023_dataset.csv"

PROCESSED_DATA = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cloud_budget_2023_dataset_cleaned.csv"
)


# ==========================
# Load Dataset
# ==========================

def load_dataset(path: Path):

    print("Loading dataset...")

    df = pd.read_csv(path)

    print("Dataset Loaded Successfully.\n")

    return df


# ==========================
# Data Profiling
# ==========================

def profile_data(df):

    print("=" * 60)
    print("DATA PROFILE")
    print("=" * 60)

    print(f"\nRows : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    print("\nColumn Names:\n")

    for col in df.columns:
        print(col)

    print("\n")

    print(df.info())

    print("\nMissing Values\n")

    print(df.isnull().sum())

    print("\nDuplicate Rows")

    print(df.duplicated().sum())


# ==========================
# Cleaning
# ==========================

def clean_data(df):

    print("\nCleaning Dataset...\n")

    df = df.drop_duplicates()

    return df


# ==========================
# Save
# ==========================

def save_dataset(df):

    df.to_csv(PROCESSED_DATA, index=False)

    print("\nClean dataset saved successfully.")


# ==========================
# Main
# ==========================

def main():

    df = load_dataset(RAW_DATA)

    profile_data(df)

    df = clean_data(df)

    save_dataset(df)


if __name__ == "__main__":
    main()