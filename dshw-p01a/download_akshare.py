import os
from datetime import datetime, timezone

import akshare as ak
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
STOCK_DIR = os.path.join(DATA_DIR, "stock")
INDEX_DIR = os.path.join(DATA_DIR, "index")
MACRO_DIR = os.path.join(DATA_DIR, "macro")
FINANCE_DIR = os.path.join(DATA_DIR, "finance")
LOG_PATH = os.path.join(PROJECT_DIR, "download_log.txt")

STOCK_CODES = [
    "000568",
    "000988",
    "002179",
    "300510",
    "600048",
    "600519",
    "601166",
    "601288",
    "603319",
    "603685",
]

INDEX_SOURCES = [
    ("sh000300", "hs300", "tx"),
    ("sz000905", "zz500", "tx"),
]

MACRO_SOURCES = [
    ("macro_china_cpi", "macro_cpi.csv"),
    ("macro_china_money_supply", "macro_money_supply.csv"),
]


def ensure_dirs():
    for path in [STOCK_DIR, INDEX_DIR, MACRO_DIR, FINANCE_DIR]:
        os.makedirs(path, exist_ok=True)


def log_write(message: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(message)


def log_file(path: str, rows: int, cols: int, src: str):
    ts = datetime.now(timezone.utc).isoformat()
    log_write(f"{ts}\t{os.path.basename(path)}\trows={rows}\tcols={cols}\tsrc={src}\tdst={path}\n")


def save_df(df: pd.DataFrame, dst_path: str, src: str):
    df.to_csv(dst_path, index=False)
    rows, cols = df.shape
    log_file(dst_path, rows, cols, src)
    return rows, cols


def stock_prefix(code: str) -> str:
    return "sh" + code if code.startswith("6") else "sz" + code


def download_stock_data():
    print("Downloading stock daily data...")
    for code in STOCK_CODES:
        symbol = stock_prefix(code)
        dst_path = os.path.join(STOCK_DIR, f"stock_{code}.csv")
        try:
            df = ak.stock_zh_a_daily(symbol=symbol, adjust="")
            save_df(df, dst_path, f"akshare.stock_zh_a_daily({symbol})")
            print("Saved", dst_path, df.shape)
        except Exception as exc:
            print("Stock download failed", code, exc)
            log_write(f"{datetime.now(timezone.utc).isoformat()}\tstock_{code}.csv\tERROR\t{exc}\n")


def download_index_data():
    print("Downloading index daily data...")
    for symbol, name, source in INDEX_SOURCES:
        dst_path = os.path.join(INDEX_DIR, f"index_{name}.csv")
        try:
            if source == "em":
                df = ak.stock_zh_index_daily_em(symbol=symbol)
            else:
                df = ak.stock_zh_index_daily_tx(symbol=symbol)
            save_df(df, dst_path, f"akshare.{source} index {symbol}")
            print("Saved", dst_path, df.shape)
        except Exception as exc:
            print("Index download failed", symbol, source, exc)
            log_write(f"{datetime.now(timezone.utc).isoformat()}\tindex_{name}.csv\tERROR\t{exc}\n")


def download_macro_data():
    print("Downloading macro data...")
    for func_name, filename in MACRO_SOURCES:
        dst_path = os.path.join(MACRO_DIR, filename)
        try:
            fn = getattr(ak, func_name)
            df = fn()
            save_df(df, dst_path, f"akshare.{func_name}()")
            print("Saved", dst_path, df.shape)
        except Exception as exc:
            print("Macro download failed", func_name, exc)
            log_write(f"{datetime.now(timezone.utc).isoformat()}\t{filename}\tERROR\t{exc}\n")


def download_finance_data():
    print("Downloading finance data...")
    for code in STOCK_CODES:
        dst_path = os.path.join(FINANCE_DIR, f"finance_{code}.csv")
        try:
            df = ak.stock_financial_abstract(symbol=code)
            save_df(df, dst_path, f"akshare.stock_financial_abstract({code})")
            print("Saved", dst_path, df.shape)
        except Exception as exc:
            print("Finance download failed", code, exc)
            log_write(f"{datetime.now(timezone.utc).isoformat()}\tfinance_{code}.csv\tERROR\t{exc}\n")


def download_all():
    ensure_dirs()
    download_stock_data()
    download_index_data()
    download_macro_data()
    download_finance_data()
    print("All available akshare downloads completed.")


if __name__ == "__main__":
    download_all()
