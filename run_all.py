"""
run_all.py: 直接执行清洗 + 分析 + 生成 report.html
规避 notebook JSON 编码问题，所有逻辑集中在此脚本
"""
import os, sys, warnings, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import pyarrow.parquet as pq

warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

os.makedirs('output', exist_ok=True)
os.makedirs('data/clean', exist_ok=True)
os.makedirs('data/combined', exist_ok=True)

print("="*60)
print("dshw-p01 数据处理与分析脚本")
print("="*60)

# ===== 元信息 =====
STOCKS_INFO = {
    '603685': {'name': '晨丰科技', 'industry': '电气设备'},
    '603319': {'name': '美湖股份', 'industry': '化工'},
    '600519': {'name': '贵州茅台', 'industry': '食品饮料'},
    '601288': {'name': '农业银行', 'industry': '银行'},
    '601166': {'name': '兴业银行', 'industry': '银行'},
    '600048': {'name': '保利发展', 'industry': '房地产'},
    '000568': {'name': '泸州老窖', 'industry': '食品饮料'},
    '002179': {'name': '中航光电', 'industry': '国防军工'},
    '300510': {'name': '金冠股份', 'industry': '电气设备'},
    '000988': {'name': '华工科技', 'industry': '电子'},
}
INDUSTRY_ORDER = ['银行', '房地产', '食品饮料', '电气设备', '化工', '国防军工', '电子']
codes_by_industry = sorted(
    STOCKS_INFO.keys(),
    key=lambda c: (INDUSTRY_ORDER.index(STOCKS_INFO[c]['industry'])
                   if STOCKS_INFO[c]['industry'] in INDUSTRY_ORDER else 99,
                   STOCKS_INFO[c]['name'])
)
INDUSTRY_COLORS = {
    '银行': '#185FA5', '房地产': '#A32D2D', '食品饮料': '#854F0B',
    '电气设备': '#0F6E56', '化工': '#534AB7', '国防军工': '#993556', '电子': '#444441'
}

# ===== 加载数据 =====
print("\n[1/6] 加载原始数据...")
dfs = {}
for code in STOCKS_INFO:
    df = pd.read_csv(f'data/stock/stock_{code}.csv', encoding='utf-8-sig')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    for c in ['open','close','high','low','volume','amount']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df['return'] = np.log(df['close'] / df['close'].shift(1))
    dfs[code] = df

df_hs300 = pd.read_csv('data/index/index_000300.csv', encoding='utf-8-sig')
df_hs300['date'] = pd.to_datetime(df_hs300['date'])
df_hs300 = df_hs300.set_index('date').sort_index()
df_hs300['close'] = pd.to_numeric(df_hs300['close'], errors='coerce')
df_hs300['return'] = np.log(df_hs300['close'] / df_hs300['close'].shift(1))

df_fx = pd.read_csv('data/macro/macro_exchange_rate.csv', encoding='utf-8-sig')
df_fx['date'] = pd.to_datetime(df_fx['date'])
df_fx = df_fx.set_index('date').sort_index()
# 统一列名为 usd_cny_mid
if 'value' in df_fx.columns:
    df_fx = df_fx.rename(columns={'value': 'usd_cny_mid'})

df_fin = pd.read_csv('data/finance/finance_ratios.csv', encoding='utf-8-sig', dtype={'code': str})
df_fin['code'] = df_fin['code'].str.zfill(6)
print("  数据加载完毕")

# ===== 第三部分：清洗 =====
print("\n[2/6] 数据清洗...")
dfs_clean = {}
clean_records = []

for code, info in STOCKS_INFO.items():
    df = dfs[code].copy()
    n0 = len(df)
    n_miss_before = df.isna().sum().sum()
    df = df.ffill()
    n_dup = df.index.duplicated().sum()
    df = df[~df.index.duplicated(keep='first')]
    df['is_extreme'] = df['return'].abs() > 0.20
    dfs_clean[code] = df
    clean_records.append({
        'code': code, 'name': info['name'],
        'rows_before': n0, 'rows_after': len(df),
        'dup_removed': n_dup, 'missing_filled': n_miss_before,
        'extreme_days': int(df['is_extreme'].sum())
    })

df_clean_stat = pd.DataFrame(clean_records)
print(df_clean_stat.to_string(index=False))

# 保存清洗后 CSV
all_stocks_list = []
for code, info in STOCKS_INFO.items():
    df_tmp = dfs_clean[code].copy().reset_index()
    df_tmp['code'] = code
    df_tmp['name'] = info['name']
    all_stocks_list.append(df_tmp)
df_all = pd.concat(all_stocks_list, ignore_index=True)
df_all.to_csv('data/clean/stock_clean.csv', index=False, encoding='utf-8-sig')

# 保存 Parquet
df_all.to_parquet('data/clean/stock_clean.parquet', index=False, engine='pyarrow')
print(f"  stock_clean.csv  shape={df_all.shape}")
print(f"  stock_clean.parquet 已保存")

# 宽表/长表
wide_close = pd.DataFrame({code: dfs_clean[code]['close'] for code in STOCKS_INFO})
wide_close.index.name = 'date'
long_close = wide_close.reset_index().melt(id_vars='date', var_name='code', value_name='close')

# 合并指数 + 宏观
df_idx = pd.read_csv('data/index/index_000300.csv', encoding='utf-8-sig')
df_idx['date'] = pd.to_datetime(df_idx['date'])
df_idx = df_idx.rename(columns={'close': 'hs300_close'})
df_idx_sub = df_idx[['date', 'hs300_close']]

df_all_merged = df_all.merge(df_idx_sub, on='date', how='left')
df_all_merged['year_month'] = df_all_merged['date'].dt.to_period('M')
df_fx_m = df_fx['usd_cny_mid'].resample('MS').mean().reset_index()
df_fx_m['year_month'] = df_fx_m['date'].dt.to_period('M')
df_combined = df_all_merged.merge(df_fx_m[['year_month','usd_cny_mid']], on='year_month', how='left')
df_combined = df_combined.drop(columns=['year_month'])
df_combined.to_csv('data/combined/combined_data.csv', index=False, encoding='utf-8-sig')
print(f"  combined_data.csv shape={df_combined.shape}")

# Parquet 性能对比
csv_path = 'data/clean/stock_clean.csv'
parquet_path = 'data/clean/stock_clean.parquet'
t0 = time.time(); pd.read_csv(csv_path); csv_time = time.time()-t0
t0 = time.time(); pd.read_parquet(parquet_path); pq_time = time.time()-t0
csv_kb = os.path.getsize(csv_path)/1024
pq_kb = os.path.getsize(parquet_path)/1024
print(f"  CSV {csv_time:.3f}s {csv_kb:.0f}KB | Parquet {pq_time:.3f}s {pq_kb:.0f}KB | 压缩比 {csv_kb/pq_kb:.1f}x")

# ===== 第四部分：描述统计 =====
print("\n[3/6] 计算描述统计...")
TRADING_DAYS = 252

def max_drawdown(series):
    cum = series.cumsum()
    roll_max = cum.cummax()
    return (cum - roll_max).min()

stat_rows = []
for code in STOCKS_INFO:
    r = dfs_clean[code]['return'].dropna()
    stat_rows.append({
        '代码': code, '名称': STOCKS_INFO[code]['name'], '行业': STOCKS_INFO[code]['industry'],
        '年化均值': f"{r.mean()*TRADING_DAYS:.2%}",
        '年化波动率': f"{r.std()*np.sqrt(TRADING_DAYS):.2%}",
        '偏度': round(r.skew(),3),
        '超额峰度': round(r.kurtosis(),3),
        '最大回撤': f"{max_drawdown(r):.2%}"
    })
df_stat = pd.DataFrame(stat_rows)
print(df_stat.to_string(index=False))

# ===== 图 1：归一化走势 =====
print("\n[4/6] 生成图表...")
fig, ax = plt.subplots(figsize=(14,7))
hs300_norm = df_hs300['close'] / df_hs300['close'].iloc[0]
ax.plot(hs300_norm.index, hs300_norm.values, color='black', linewidth=2,
        linestyle='--', label='沪深300', alpha=0.9, zorder=5)
for code in codes_by_industry:
    df = dfs_clean[code]
    color = INDUSTRY_COLORS[STOCKS_INFO[code]['industry']]
    norm = df['close'] / df['close'].iloc[0]
    ax.plot(norm.index, norm.values, color=color, linewidth=1.2,
            alpha=0.75, label=STOCKS_INFO[code]['name'])
ax.axhline(y=1, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
ax.set_title('归一化收盘价走势（2020-01-01=1）', fontsize=13, fontweight='bold')
ax.set_xlabel('日期'); ax.set_ylabel('归一化价格')
ax.legend(loc='upper left', fontsize=8, ncol=2, framealpha=0.85)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('output/fig1_normalized_price.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig1 done")

# ===== 图 2：收益率分布 =====
fig, axes = plt.subplots(2, 5, figsize=(18,7))
axes = axes.flatten()
codes_list = list(STOCKS_INFO.keys())
for i, code in enumerate(codes_list):
    r = dfs_clean[code]['return'].dropna()
    mu, sigma = r.mean(), r.std()
    ax = axes[i]
    color = INDUSTRY_COLORS[STOCKS_INFO[code]['industry']]
    ax.hist(r, bins=60, density=True, color=color, alpha=0.55, edgecolor='none')
    x = np.linspace(r.min(), r.max(), 200)
    ax.plot(x, stats.norm.pdf(x, mu, sigma), color=color, linewidth=1.8)
    ax.set_title(f"{STOCKS_INFO[code]['name']}\n({code})", fontsize=9, fontweight='bold')
    ax.text(0.97,0.92, f'mu={mu:.4f}\nsigma={sigma:.4f}',
            transform=ax.transAxes, ha='right', va='top', fontsize=7.5,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    ax.set_xlabel('日对数收益率', fontsize=7)
    ax.tick_params(labelsize=7); ax.grid(True, alpha=0.25)
fig.suptitle('10只股票日收益率分布（叠加正态曲线）', fontsize=13, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig('output/fig2_return_distribution.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig2 done")

# ===== 图 3：相关系数热力图 =====
ret_wide = pd.DataFrame({code: dfs_clean[code]['return'] for code in codes_by_industry})
ret_wide.columns = [STOCKS_INFO[c]['name'] for c in codes_by_industry]
corr_matrix = ret_wide.dropna().corr()
fig, ax = plt.subplots(figsize=(10,8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r',
            vmin=-0.2, vmax=1.0, center=0.4, linewidths=0.5, linecolor='white',
            annot_kws={'size': 9}, ax=ax, cbar_kws={'shrink': 0.8})
names_ord = [STOCKS_INFO[c]['name'] for c in codes_by_industry]
inds_ord = [STOCKS_INFO[c]['industry'] for c in codes_by_industry]
y_labs = [f'{n}\n[{ind}]' for n, ind in zip(names_ord, inds_ord)]
ax.set_yticklabels(y_labs, rotation=0, fontsize=8)
ax.set_xticklabels(names_ord, rotation=30, ha='right', fontsize=8)
ax.set_title('10只股票日收益率相关系数矩阵（按行业排序）', fontsize=12, fontweight='bold')
fig.tight_layout()
fig.savefig('output/fig3_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig3 done")

# ===== 图 4：宏观散点图 =====
hs300_monthly = df_hs300['close'].resample('MS').last().pct_change().dropna()
fx_chg = df_fx['usd_cny_mid'].resample('MS').mean().pct_change().dropna()
common_idx = hs300_monthly.index.intersection(fx_chg.index)
y_sc = hs300_monthly.loc[common_idx].values
x_sc = fx_chg.loc[common_idx].values
slope, intercept, r_val, p_val, se = stats.linregress(x_sc, y_sc)
fig, ax = plt.subplots(figsize=(8,5.5))
ax.scatter(x_sc*100, y_sc*100, color='#185FA5', alpha=0.6, s=50, edgecolors='none')
x_line = np.linspace(x_sc.min(), x_sc.max(), 100)
ax.plot(x_line*100, (slope*x_line+intercept)*100, color='#A32D2D', linewidth=2)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_title(f'人民币/美元汇率月度变动 vs 沪深300月度收益率\nPearson r={r_val:.3f}, p={p_val:.3f}',
             fontsize=11, fontweight='bold')
ax.set_xlabel('汇率月度变动率（人民币贬值为正）(%)'); ax.set_ylabel('沪深300月度收益率 (%)')
ax.text(0.97, 0.05, f'slope={slope:.2f}\np={p_val:.3f}',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('output/fig4_macro_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig4 done")

# ===== 图 5：ROE 折线图 =====
df_roe = df_fin[df_fin['indicator']=='ROE'].copy()
df_roe['year'] = df_roe['year'].astype(str)
df_roe = df_roe[df_roe['year'].isin(['2020','2021','2022','2023','2024'])]
df_roe['value'] = pd.to_numeric(df_roe['value'], errors='coerce')
fig, ax = plt.subplots(figsize=(12,6))
for code in STOCKS_INFO:
    sub = df_roe[df_roe['code']==code].sort_values('year')
    if len(sub)==0: continue
    color = INDUSTRY_COLORS[STOCKS_INFO[code]['industry']]
    ax.plot(sub['year'], sub['value'], marker='o', color=color, linewidth=1.8,
            markersize=5, label=f"{STOCKS_INFO[code]['name']}（{STOCKS_INFO[code]['industry']}）", alpha=0.85)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.set_title('10只股票ROE（净资产收益率）近5年走势', fontsize=13, fontweight='bold')
ax.set_xlabel('年份'); ax.set_ylabel('ROE (%)')
ax.legend(loc='upper right', fontsize=8, ncol=2, framealpha=0.85)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig('output/fig5_roe_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig5 done")

# ===== 第五部分：CAPM =====
print("\n[5/6] CAPM 回归分析...")
RF_DAILY = 0.02 / 252
capm_rows = []
betas_plot, beta_lo_plot, beta_hi_plot, names_plot, inds_plot = [], [], [], [], []

for code in STOCKS_INFO:
    ri = dfs_clean[code]['return'].dropna()
    rm = df_hs300['return'].dropna()
    common = ri.index.intersection(rm.index)
    ri_exc = ri.loc[common] - RF_DAILY
    rm_exc = rm.loc[common] - RF_DAILY
    X = sm.add_constant(rm_exc)
    model = sm.OLS(ri_exc, X).fit()
    alpha = model.params.iloc[0]
    beta = model.params.iloc[1]
    alpha_p = model.pvalues.iloc[0]
    ci_lo = model.conf_int().iloc[1,0]
    ci_hi = model.conf_int().iloc[1,1]
    r2 = model.rsquared
    capm_rows.append({
        '代码': code, '名称': STOCKS_INFO[code]['name'], '行业': STOCKS_INFO[code]['industry'],
        'alpha(年化)': round(alpha*252, 4), 'alpha_p': round(alpha_p, 4),
        'beta': round(beta, 4), 'beta_95CI': f'[{ci_lo:.3f},{ci_hi:.3f}]', 'R2': round(r2, 4)
    })
    betas_plot.append(beta); beta_lo_plot.append(ci_lo); beta_hi_plot.append(ci_hi)
    names_plot.append(STOCKS_INFO[code]['name']); inds_plot.append(STOCKS_INFO[code]['industry'])

df_capm = pd.DataFrame(capm_rows)
print(df_capm.to_string(index=False))

# Beta 点图
sort_idx = np.argsort(betas_plot)
betas_s = np.array(betas_plot)[sort_idx]
blo_s = np.array(beta_lo_plot)[sort_idx]
bhi_s = np.array(beta_hi_plot)[sort_idx]
names_s = [names_plot[i] for i in sort_idx]
inds_s = [inds_plot[i] for i in sort_idx]
colors_s = [INDUSTRY_COLORS[ind] for ind in inds_s]
fig, ax = plt.subplots(figsize=(9,6))
y_pos = np.arange(len(betas_s))
ax.hlines(y_pos, blo_s, bhi_s, color=colors_s, linewidth=2.5, alpha=0.6)
for i in range(len(betas_s)):
    ax.scatter(betas_s[i], y_pos[i], color=colors_s[i], s=80, zorder=5)
ax.axvline(x=1, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='beta=1')
ax.axvline(x=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels([f'{n}\n[{ind}]' for n,ind in zip(names_s,inds_s)], fontsize=9)
ax.set_xlabel('Beta系数（95%置信区间）', fontsize=11)
ax.set_title('CAPM Beta系数估计（按行业分组着色）', fontsize=12, fontweight='bold')
ax.legend(fontsize=9); ax.grid(True, axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig('output/fig_capm_beta.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig_capm_beta done")

# ===== 第5.2节：宏观回归 =====
print("\n[5.5/6] 宏观指标回归...")
fx_chg_m = df_fx['usd_cny_mid'].resample('MS').mean().pct_change().dropna()
macro_rows = []
gammas, gamma_names, gamma_inds = [], [], []

for code in STOCKS_INFO:
    monthly_ret = dfs_clean[code]['close'].resample('MS').last().pct_change().dropna()
    common = monthly_ret.index.intersection(fx_chg_m.index)
    if len(common) < 12: continue
    y_m = monthly_ret.loc[common].values
    x_m = fx_chg_m.loc[common].values
    X = sm.add_constant(x_m)
    model = sm.OLS(y_m, X).fit()
    gamma = model.params[1]
    p = model.pvalues[1]
    sig = '***' if p<0.01 else ('**' if p<0.05 else ('*' if p<0.1 else ''))
    macro_rows.append({
        '代码': code, '名称': STOCKS_INFO[code]['name'], '行业': STOCKS_INFO[code]['industry'],
        'gamma': round(gamma,4), 'p值': round(p,4), '显著性': sig
    })
    gammas.append(gamma); gamma_names.append(STOCKS_INFO[code]['name'])
    gamma_inds.append(STOCKS_INFO[code]['industry'])

df_macro = pd.DataFrame(macro_rows)
print(df_macro.to_string(index=False))

sort_g = np.argsort(gammas)
gam_s = [gammas[i] for i in sort_g]
gnm_s = [gamma_names[i] for i in sort_g]
gin_s = [gamma_inds[i] for i in sort_g]
gc_s = [INDUSTRY_COLORS[ind] for ind in gin_s]
fig, ax = plt.subplots(figsize=(9,5.5))
bars = ax.barh(gnm_s, gam_s, color=gc_s, alpha=0.75, edgecolor='none')
ax.axvline(0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.set_xlabel('gamma系数（汇率月度变动对股票月度收益率的影响）', fontsize=9)
ax.set_title('各股票对人民币/美元汇率的敏感性（gamma系数）', fontsize=11, fontweight='bold')
legend_els = [mpatches.Patch(facecolor=INDUSTRY_COLORS[ind], label=ind) for ind in INDUSTRY_COLORS]
ax.legend(handles=legend_els, fontsize=8, loc='lower right')
ax.grid(True, axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig('output/fig_macro_gamma.png', dpi=150, bbox_inches='tight')
plt.close()
print("  fig_macro_gamma done")

# ===== 输出清单 =====
print("\n[6/6] 输出文件清单:")
for f in sorted(os.listdir('output')):
    p = os.path.join('output', f)
    print(f"  {f}  {os.path.getsize(p)/1024:.0f}KB")

print("\n所有分析完成！")
print("\n统计汇总写入 analysis_results.csv ...")
df_stat.to_csv('output/stats_summary.csv', index=False, encoding='utf-8-sig')
df_capm.to_csv('output/capm_results.csv', index=False, encoding='utf-8-sig')
df_macro.to_csv('output/macro_regression_results.csv', index=False, encoding='utf-8-sig')
print("Done!")
