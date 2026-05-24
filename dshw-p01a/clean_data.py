import glob
import os
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "stock")
CLEAN_DIR = os.path.join(PROJECT_DIR, "data", "clean")
COMBINED_DIR = os.path.join(PROJECT_DIR, "data", "combined")


def ensure_dirs():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(COMBINED_DIR, exist_ok=True)


def clean_stock_files():
    ensure_dirs()
    clean_files = []
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "stock_*.csv"))):
        code = os.path.splitext(os.path.basename(path))[0].replace("stock_", "")
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.drop_duplicates(subset=["date"]).sort_values("date")
        df["ticker"] = code
        dst = os.path.join(CLEAN_DIR, f"stock_{code}.csv")
        df.to_csv(dst, index=False)
        clean_files.append(dst)
        print("Cleaned", dst, df.shape)
    return clean_files


def combine_cleaned_files(clean_files=None):
    ensure_dirs()
    if clean_files is None:
        clean_files = sorted(glob.glob(os.path.join(CLEAN_DIR, "stock_*.csv")))
    frames = []
    for path in clean_files:
        df = pd.read_csv(path, parse_dates=["date"], dtype={"ticker": str})
        frames.append(df)
    if not frames:
        raise RuntimeError("No cleaned stock files were found.")
    combined = pd.concat(frames, ignore_index=True)
    combined_path = os.path.join(COMBINED_DIR, "combined_stocks.csv")
    combined.to_csv(combined_path, index=False)
    print("Combined data shape:", combined.shape)
    print("Saved combined file:", combined_path)
    return combined_path


def clean_all():
    clean_files = clean_stock_files()
    return combine_cleaned_files(clean_files)


if __name__ == "__main__":
    clean_all()
