import os
import re
import pandas as pd
import statsmodels.api as sm

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
COMBINED_PATH = os.path.join(PROJECT_DIR, "data", "combined", "combined_stocks.csv")
INDEX_PATH = os.path.join(PROJECT_DIR, "data", "index", "index_hs300.csv")
MACRO_CPI_PATH = os.path.join(PROJECT_DIR, "data", "macro", "macro_cpi.csv")
MACRO_M2_PATH = os.path.join(PROJECT_DIR, "data", "macro", "macro_money_supply.csv")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

RISK_FREE_RATE = 0.0


def parse_month_text(text):
    m = re.match(r"(\d{4})年\s*(\d{1,2})月份", str(text).strip())
    if m:
        year, month = m.groups()
        return f"{year}-{int(month):02d}"
    return None


def load_data():
    combined = pd.read_csv(COMBINED_PATH, parse_dates=["date"], dtype={"ticker": str})
    index = pd.read_csv(INDEX_PATH, parse_dates=["date"])
    if "close" not in index.columns:
        raise KeyError("Index data must contain a 'close' column")
    index = index[["date", "close"]].rename(columns={"close": "market_close"})

    macro_cpi = pd.read_csv(MACRO_CPI_PATH, dtype=str)
    macro_cpi["month"] = macro_cpi["月份"].apply(parse_month_text)
    macro_cpi["cpi_yoy"] = pd.to_numeric(macro_cpi["全国-同比增长"], errors="coerce")
    macro_cpi = macro_cpi[["month", "cpi_yoy"]].dropna()

    macro_m2 = pd.read_csv(MACRO_M2_PATH, dtype=str)
    macro_m2["month"] = macro_m2["月份"].apply(parse_month_text)
    m2_column = "货币和准货币(M2)-同比增长"
    if m2_column not in macro_m2.columns:
        m2_column = next((c for c in macro_m2.columns if "M2" in c and "同比增长" in c), None)
    macro_m2["m2_yoy"] = pd.to_numeric(macro_m2[m2_column], errors="coerce")
    macro_m2 = macro_m2[["month", "m2_yoy"]].dropna()

    macro = macro_cpi.merge(macro_m2, on="month", how="inner")
    return combined, index, macro


def compute_returns(df, price_col="close"):
    df = df.sort_values(["ticker", "date"]) if "ticker" in df.columns else df.sort_values("date")
    df["ret"] = df.groupby("ticker")[price_col].pct_change()
    return df


def compute_market_returns(index):
    index = index.sort_values("date").copy()
    index["mkt_ret"] = index["market_close"].pct_change()
    return index


def compute_monthly_returns(df):
    df = df.sort_values(["ticker", "date"]).copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby(["ticker", "month"]).last().reset_index()
    monthly["monthly_ret"] = monthly.groupby("ticker")["close"].pct_change()
    return monthly[["ticker", "month", "monthly_ret"]]


def run_capm(stock_returns, market_returns):
    merged = stock_returns.merge(market_returns[["date", "mkt_ret"]], on="date", how="inner")
    merged = merged.dropna(subset=["ret", "mkt_ret"])
    results = []
    for ticker, df in merged.groupby("ticker"):
        if df.shape[0] < 10:
            continue
        X = sm.add_constant(df["mkt_ret"])
        y = df["ret"]
        model = sm.OLS(y, X).fit()
        results.append({
            "ticker": ticker,
            "alpha": model.params["const"],
            "beta": model.params["mkt_ret"],
            "alpha_t": model.tvalues["const"],
            "beta_t": model.tvalues["mkt_ret"],
            "alpha_p": model.pvalues["const"],
            "beta_p": model.pvalues["mkt_ret"],
            "r_squared": model.rsquared,
            "observations": int(model.nobs),
        })
    return pd.DataFrame(results)


def run_macro_regression(monthly_returns, macro):
    merged = monthly_returns.merge(macro, on="month", how="inner")
    merged = merged.dropna(subset=["monthly_ret", "cpi_yoy", "m2_yoy"])
    results = []
    for ticker, df in merged.groupby("ticker"):
        if df.shape[0] < 8:
            continue
        X = sm.add_constant(df[["cpi_yoy", "m2_yoy"]])
        y = df["monthly_ret"]
        model = sm.OLS(y, X).fit()
        results.append({
            "ticker": ticker,
            "alpha": model.params["const"],
            "beta_cpi": model.params["cpi_yoy"],
            "beta_m2": model.params["m2_yoy"],
            "alpha_t": model.tvalues["const"],
            "beta_cpi_t": model.tvalues["cpi_yoy"],
            "beta_m2_t": model.tvalues["m2_yoy"],
            "alpha_p": model.pvalues["const"],
            "beta_cpi_p": model.pvalues["cpi_yoy"],
            "beta_m2_p": model.pvalues["m2_yoy"],
            "r_squared": model.rsquared,
            "observations": int(model.nobs),
        })
    return pd.DataFrame(results), merged


def summarize_statistics(stock_returns):
    stats = stock_returns.groupby("ticker")["ret"].agg(
        mean_ret="mean",
        std_ret="std",
        min_ret="min",
        max_ret="max",
        median_ret="median",
    ).reset_index()
    stats["sharpe_ratio"] = stats["mean_ret"] / stats["std_ret"]
    stats["annualized_volatility"] = stats["std_ret"] * (252 ** 0.5)
    return stats


def run_analysis():
    combined, index, macro = load_data()
    stock_returns = compute_returns(combined)
    market_returns = compute_market_returns(index)
    capm_results = run_capm(stock_returns, market_returns)
    stats_summary = summarize_statistics(stock_returns.dropna(subset=["ret"]))
    monthly_returns = compute_monthly_returns(combined)
    macro_results, merged_macro = run_macro_regression(monthly_returns, macro)

    capm_path = os.path.join(OUTPUT_DIR, "capm_results.csv")
    stats_path = os.path.join(OUTPUT_DIR, "stats_summary.csv")
    market_path = os.path.join(OUTPUT_DIR, "market_returns.csv")
    macro_path = os.path.join(OUTPUT_DIR, "macro_regression_results.csv")
    macro_join_path = os.path.join(OUTPUT_DIR, "macro_monthly_returns.csv")

    capm_results.to_csv(capm_path, index=False)
    stats_summary.to_csv(stats_path, index=False)
    market_returns.dropna(subset=["mkt_ret"]).to_csv(market_path, index=False)
    macro_results.to_csv(macro_path, index=False)
    merged_macro.to_csv(macro_join_path, index=False)

    print(f"Saved CAPM results to {capm_path}")
    print(f"Saved stats summary to {stats_path}")
    print(f"Saved market returns to {market_path}")
    print(f"Saved macro regression results to {macro_path}")
    print(f"Saved macro monthly returns merge to {macro_join_path}")
    print(capm_results)
    return capm_results, stats_summary, market_returns, macro_results


if __name__ == "__main__":
    run_analysis()
