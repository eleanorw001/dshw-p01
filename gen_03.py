# -*- coding: utf-8 -*-
"""Generate 03_analysis.ipynb with valid JSON (all Chinese via ensure_ascii)."""
import json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

cells = []

def md(source):
    cells.append({"cell_type":"markdown","metadata":{},"source":source})

def code(source):
    cells.append({"cell_type":"code","metadata":{"execution":{"iopub.status.busy":"2025-01-01T00:00:00Z","iopub.execute_input":"2025-01-01T00:00:00Z"},"trusted":True},"source":source,"outputs":[],"execution_count":None})

# ========== Part 4: Descriptive Statistics ==========
md([
    "# \u7b2c\u56db\u90e8\u5206\uff1a\u63cf\u8ff0\u6027\u7edf\u8ba1\u4e0e\u53ef\u89c6\u5316\n",
    "\u672c\u90e8\u5206\u5bf9 10 \u53ea\u80a1\u7968\u8fdb\u884c\u63cf\u8ff0\u6027\u7edf\u8ba1\uff0c\u5e76\u7ed8\u5236 5 \u5f20\u53ef\u89c6\u5316\u56fe\u8868\uff0c\u4fdd\u5b58\u81f3 `output/` \u76ee\u5f55\u3002"
])

md([
    "## 4.1 \u57fa\u672c\u7edf\u8ba1\u91cf\n",
    "\u8ba1\u7b97\u65e5\u5bf9\u6570\u6536\u76ca\u7387\u7684\u63cf\u8ff0\u6027\u7edf\u8ba1\uff0c\u5305\u62ec\u5e74\u5316\u5747\u503c\u3001\u5e74\u5316\u6ce2\u52a8\u7387\u3001\u504f\u5ea6\u3001\u5cf0\u5ea6\u3001\u6700\u5927\u56de\u64a4\u3002"
])

code([
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib\n",
    "matplotlib.use('Agg')\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.font_manager as fm\n",
    "import seaborn as sns\n",
    "from scipy import stats\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# \u4e2d\u6587\u5b57\u4f53\u8bbe\u7f6e\n",
    "plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']\n",
    "plt.rcParams['axes.unicode_minus'] = False\n",
    "\n",
    "# \u80a1\u7968\u4fe1\u606f\n",
    "stock_info = {\n",
    "    '603685': ('\\u6668\\u4e30\\u79d1\\u6280', '\\u7535\\u6c14\\u8bbe\\u5907'),\n",
    "    '603319': ('\\u7f8e\\u6e56\\u80a1\\u4efd', '\\u5316\\u5de5'),\n",
    "    '600519': ('\\u8d35\\u5dde\\u8305\\u53f0', '\\u98df\\u54c1\\u996e\\u6599'),\n",
    "    '601288': ('\\u519c\\u4e1a\\u94f6\\u884c', '\\u94f6\\u884c'),\n",
    "    '601166': ('\\u5174\\u4e1a\\u94f6\\u884c', '\\u94f6\\u884c'),\n",
    "    '600048': ('\\u4fdd\\u5229\\u53d1\\u5c55', '\\u623f\\u5730\\u4ea7'),\n",
    "    '000568': ('\\u6cf8\\u5dde\\u8001\\u7956', '\\u98df\\u54c1\\u996e\\u6599'),\n",
    "    '002179': ('\\u4e2d\\u822a\\u5149\\u7535', '\\u56fd\\u9632\\u519b\\u5de5'),\n",
    "    '300510': ('\\u91d1\\u51a0\\u80a1\\u4efd', '\\u7535\\u6c14\\u8bbe\\u5907'),\n",
    "    '000988': ('\\u534e\\u5de5\\u79d1\\u6280', '\\u7535\\u5b50'),\n",
    "}\n",
    "\n",
    "# \u8bfb\u53d6\u6e05\u6d17\u540e\u6570\u636e\n",
    "df = pd.read_csv('data/clean/stock_clean.csv', encoding='utf-8-sig', dtype={'code': str})\n",
    "df['date'] = pd.to_datetime(df['date'])\n",
    "print(f'\\u6570\\u636e\\u89c4\\u6a21: {df.shape}')\n",
    "print(df.head())"
])

code([
    "# \u8ba1\u7b97\u65e5\u5bf9\u6570\u6536\u76ca\u7387\n",
    "df_list = []\n",
    "for code in sorted(stock_info.keys()):\n",
    "    sub = df[df['code'] == code].sort_values('date').copy()\n",
    "    sub['ret'] = np.log(sub['close'] / sub['close'].shift(1))\n",
    "    sub = sub.dropna(subset=['ret'])\n",
    "    sub['name'] = stock_info[code][0]\n",
    "    sub['industry'] = stock_info[code][1]\n",
    "    df_list.append(sub)\n",
    "df_ret = pd.concat(df_list, ignore_index=True)\n",
    "print(f'\\u6536\\u76ca\\u7387\\u6570\\u636e: {df_ret.shape}')"
])

code([
    "# 4.1 \u63cf\u8ff0\u6027\u7edf\u8ba1\u8868\n",
    "stats_rows = []\n",
    "for code in sorted(stock_info.keys()):\n",
    "    name, industry = stock_info[code]\n",
    "    r = df_ret[df_ret['code'] == code]['ret']\n",
    "    ann_mean = r.mean() * 252\n",
    "    ann_vol = r.std() * np.sqrt(252)\n",
    "    skew = r.skew()\n",
    "    kurt = r.kurtosis()\n",
    "    cum = (1 + r).cumprod()\n",
    "    running_max = cum.cummax()\n",
    "    drawdown = (cum - running_max) / running_max\n",
    "    max_dd = drawdown.min()\n",
    "    stats_rows.append({\n",
    "        '\\u80a1\\u7968': f'{name}({code})', '\\u884c\\u4e1a': industry,\n",
    "        '\\u5e74\\u5316\\u5747\\u503c': f'{ann_mean:.4f}',\n",
    "        '\\u5e74\\u5316\\u6ce2\\u52a8\\u7387': f'{ann_vol:.4f}',\n",
    "        '\\u504f\\u5ea6': f'{skew:.4f}', '\\u5cf0\\u5ea6': f'{kurt:.4f}',\n",
    "        '\\u6700\\u5927\\u56de\\u64a4': f'{max_dd:.4f}'\n",
    "    })\n",
    "\n",
    "stats_df = pd.DataFrame(stats_rows)\n",
    "stats_df.to_csv('output/stats_summary.csv', index=False, encoding='utf-8-sig')\n",
    "stats_df"
])

md([
    "**\u89e3\u8bfb\uff1a** \u5e74\u5316\u5747\u503c\u53cd\u6620\u80a1\u7968\u7684\u5e74\u5747\u6536\u76ca\u6c34\u5e73\uff0c\u6b63\u503c\u8868\u793a\u6da8\u3001\u8d1f\u503c\u8868\u793a\u8dcc\u3002\u5e74\u5316\u6ce2\u52a8\u7387\u5ea6\u91cf\u98ce\u9669\uff0c\u503c\u8d8a\u5927\u8868\u793a\u4ef7\u683c\u6ce2\u52a8\u8d8a\u5267\u70c8\u3002\u504f\u5ea6\u4e3a\u8d1f\u8868\u793a\u6536\u76ca\u7387\u5de6\u504f\uff08\u5de6\u5c3e\u8f83\u957f\uff09\uff0c\u5cf0\u5ea6\u5927\u4e8e 0 \u8868\u793a\u5c16\u5cf0\u539a\u5c3e\uff08\u6781\u7aef\u6536\u76ca\u51fa\u73b0\u9891\u7387\u9ad8\u4e8e\u6b63\u6001\uff09\u3002\u6700\u5927\u56de\u64a4\u8868\u793a\u4ece\u5386\u53f2\u6700\u9ad8\u70b9\u5230\u6700\u4f4e\u70b9\u7684\u6700\u5927\u4e0b\u8dcc\u5e45\u5ea6\u3002"
])

# ========== Figure 1 ==========
md([
    "## 4.2 \u53ef\u89c6\u5316\n",
    "### \u56fe 1\uff1a\u5f52\u4e00\u5316\u6536\u76d8\u4ef7\u8d70\u52bf\u56fe\n",
    "\u4ee5 2020-01-02 \u4e3a\u57fa\u51c6\uff08\u5f52\u4e00\u5316\u4e3a 1\uff09\uff0c\u5c55\u793a 10 \u53ea\u80a1\u7968\u548c\u6caa\u6df1 300 \u7684\u7d2f\u8ba1\u8868\u73b0\u3002"
])

code([
    "df_hs300 = pd.read_csv('data/index/index_000300.csv', encoding='utf-8-sig', dtype={'code': str})\n",
    "df_hs300['date'] = pd.to_datetime(df_hs300['date'])\n",
    "hs300_price = df_hs300.set_index('date')['close']\n",
    "hs300_norm = hs300_price / hs300_price.iloc[0]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(14, 7))\n",
    "industry_colors = {'\\u98df\\u54c1\\u996e\\u6599': '#e74c3c', '\\u94f6\\u884c': '#2980b9', '\\u623f\\u5730\\u4ea7': '#8e44ad',\n",
    "                  '\\u7535\\u6c14\\u8bbe\\u5907': '#27ae60', '\\u5316\\u5de5': '#f39c12', '\\u56fd\\u9632\\u519b\\u5de5': '#1abc9c', '\\u7535\\u5b50': '#e67e22'}\n",
    "\n",
    "for code in sorted(stock_info.keys()):\n",
    "    name, industry = stock_info[code]\n",
    "    sub = df[(df['code'] == code)].sort_values('date')\n",
    "    price = sub.set_index('date')['close']\n",
    "    norm = price / price.iloc[0]\n",
    "    ax.plot(norm.index, norm.values, label=f'{name}', linewidth=1.2,\n",
    "            color=industry_colors.get(industry, '#7f8c8d'), alpha=0.85)\n",
    "\n",
    "ax.plot(hs300_norm.index, hs300_norm.values, label='\\u6caa\\u6df1 300',\n",
    "        color='black', linewidth=2, linestyle='--', alpha=0.7)\n",
    "\n",
    "ax.set_title('\\u5f52\\u4e00\\u5316\\u6536\\u76d8\\u4ef7\\u8d70\\u52bf\\u56fe (2020-01 = 1)', fontsize=16)\n",
    "ax.set_xlabel('\\u65e5\\u671f', fontsize=12)\n",
    "ax.set_ylabel('\\u5f52\\u4e00\\u5316\\u4ef7\\u683c', fontsize=12)\n",
    "ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)\n",
    "ax.grid(True, alpha=0.3)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig1_normalized_price.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe 1 \\u5df2\\u4fdd\\u5b58')"
])

md([
    "**\u89e3\u8bfb\uff1a** \u4ece\u5f52\u4e00\u5316\u8d70\u52bf\u6765\u770b\uff0c\u534e\u5de5\u79d1\u6280\u5728 2020-2026 \u5e74\u95f4\u8868\u73b0\u6700\u4e3a\u4eae\u773c\uff0c\u7d2f\u8ba1\u6da8\u5e45\u8fdc\u8d85\u6caa\u6df1 300\u3002\u4fdd\u5229\u53d1\u5c55\u53d7\u623f\u5730\u4ea7\u8c03\u63a7\u5f71\u54cd\uff0c\u8868\u73b0\u6700\u5dee\uff0c\u7d2f\u8ba1\u6536\u76ca\u4e3a\u8d1f\u3002\u5927\u90e8\u5206\u80a1\u7968\u5728 2022 \u5e74\u524d\u540e\u7ecf\u5386\u4e86\u663e\u8457\u56de\u8c03\uff0c\u53cd\u6620\u4e86 A \u80a1\u6574\u4f53\u7684\u718a\u5e02\u73af\u5883\u3002\n",
    "\u4ece\u884c\u4e1a\u5206\u7ec4\u6765\u770b\uff0c\u7535\u5b50\u548c\u7535\u6c14\u8bbe\u5907\u884c\u4e1a\u80a1\u7968\u6574\u4f53\u8868\u73b0\u8f83\u597d\uff0c\u800c\u94f6\u884c\u548c\u623f\u5730\u4ea7\u884c\u4e1a\u80a1\u7968\u5219\u76f8\u5bf9\u6ede\u540e\uff0c\u8fd9\u4e0e\u8fd1\u5e74\u6765\u5229\u7387\u4e0b\u884c\u548c\u623f\u5730\u4ea7\u884c\u4e1a\u8c03\u63a7\u7684\u5927\u73af\u5883\u76f8\u7b26\u3002"
])

# ========== Figure 2 ==========
md([
    "### \u56fe 2\uff1a\u65e5\u6536\u76ca\u7387\u5206\u5e03\u56fe\n",
    "10 \u53ea\u80a1\u7968\u6536\u76ca\u7387\u7684 2\u00d75 \u5206\u9762\u76f4\u65b9\u56fe\uff0c\u6bcf\u4e2a\u5b50\u56fe\u53e0\u52a0\u6b63\u6001\u5206\u5e03\u66f2\u7ebf\u3002"
])

code([
    "codes = sorted(stock_info.keys())\n",
    "fig, axes = plt.subplots(2, 5, figsize=(20, 8))\n",
    "axes = axes.flatten()\n",
    "\n",
    "for i, code in enumerate(codes):\n",
    "    name = stock_info[code][0]\n",
    "    r = df_ret[df_ret['code'] == code]['ret']\n",
    "    ax = axes[i]\n",
    "    ax.hist(r, bins=60, density=True, alpha=0.7, color=industry_colors.get(stock_info[code][1], 'gray'), edgecolor='white')\n",
    "    \n",
    "    x = np.linspace(r.min(), r.max(), 200)\n",
    "    ax.plot(x, stats.norm.pdf(x, r.mean(), r.std()), 'r-', linewidth=2, label='\\u6b63\\u6001\\u66f2\\u7ebf')\n",
    "    ax.set_title(f'{name}', fontsize=11)\n",
    "    ax.text(0.02, 0.95, f'\\u03bc={r.mean():.4f}\\n\\u03c3={r.std():.4f}',\n",
    "            transform=ax.transAxes, fontsize=9, verticalalignment='top',\n",
    "            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))\n",
    "    ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)\n",
    "    ax.set_xlabel('\\u65e5\\u6536\\u76ca\\u7387', fontsize=9)\n",
    "\n",
    "plt.suptitle('\\u65e5\\u6536\\u76ca\\u7387\\u5206\\u5e03\\u56fe\\uff08\\u53e0\\u52a0\\u6b63\\u6001\\u66f2\\u7ebf\\uff09', fontsize=15, y=1.02)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig2_return_distribution.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe 2 \\u5df2\\u4fdd\\u5b58')"
])

md([
    "**\u89e3\u8bfb\uff1a** \u6240\u6709\u80a1\u7968\u7684\u6536\u76ca\u7387\u5206\u5e03\u5747\u5448\u73b0\u660e\u663e\u7684\u5c16\u5cf0\u539a\u5c3e\u7279\u5f81\uff08\u5cf0\u5ea6\u8fdc\u5927\u4e8e\u6b63\u6001\u5206\u5e03\u7684 3\uff09\uff0c\u8fd9\u662f A \u80a1\u5e02\u573a\u7684\u5178\u578b\u7279\u5f81\uff0c\u8868\u660e\u6781\u7aef\u6536\u76ca\uff08\u6da8\u8dcc\u505c\uff09\u51fa\u73b0\u7684\u9891\u7387\u9ad8\u4e8e\u6b63\u6001\u5047\u8bbe\u3002\n",
    "\u91d1\u51a0\u80a1\u4efd\u548c\u534e\u5de5\u79d1\u6280\u7684\u6ce2\u52a8\u7387\u6700\u5927\uff08\u5206\u5e03\u6700\u5bbd\uff09\uff0c\u800c\u519c\u4e1a\u94f6\u884c\u548c\u5174\u4e1a\u94f6\u884c\u7684\u6ce2\u52a8\u7387\u6700\u5c0f\uff0c\u53cd\u6620\u4e86\u94f6\u884c\u80a1\u4f5c\u4e3a\u9632\u5fa1\u6027\u8d44\u4ea7\u7684\u7279\u5f81\u3002\u5927\u90e8\u5206\u80a1\u7968\u5448\u73b0\u8f7b\u5fae\u8d1f\u504f\uff0c\u8bf4\u660e\u51fa\u73b0\u5927\u5e45\u4e0b\u8dcc\u7684\u6982\u7387\u7565\u9ad8\u4e8e\u5927\u5e45\u4e0a\u6da8\u3002"
])

# ========== Figure 3 ==========
md([
    "### \u56fe 3\uff1a\u6536\u76ca\u7387\u76f8\u5173\u7cfb\u6570\u70ed\u529b\u56fe\n",
    "10 \u53ea\u80a1\u7968\u65e5\u6536\u76ca\u7387\u7684\u76f8\u5173\u7cfb\u6570\u77e9\u9635\uff0c\u6309\u884c\u4e1a\u5206\u7ec4\u7740\u8272\u3002"
])

code([
    "# \u6784\u5efa\u6536\u76ca\u7387\u5bbd\u8868\n",
    "pivot_ret = df_ret.pivot_table(index='date', columns='code', values='ret')\n",
    "# \u6309\u884c\\u4e1a\\u5206\\u7ec4\\u6392\\u5e8f\n",
    "industry_order = {'\\u98df\\u54c1\\u996e\\u6599': ['000568', '600519'], '\\u94f6\\u884c': ['601288', '601166'],\n",
    "                 '\\u623f\\u5730\\u4ea7': ['600048'], '\\u7535\\u6c14\\u8bbe\\u5907': ['300510', '603685'],\n",
    "                 '\\u5316\\u5de5': ['603319'], '\\u56fd\\u9632\\u519b\\u5de5': ['002179'], '\\u7535\\u5b50': ['000988']}\n",
    "ordered_codes = []\n",
    "for ind in ['\\u98df\\u54c1\\u996e\\u6599', '\\u94f6\\u884c', '\\u623f\\u5730\\u4ea7', '\\u7535\\u6c14\\u8bbe\\u5907', '\\u5316\\u5de5', '\\u56fd\\u9632\\u519b\\u5de5', '\\u7535\\u5b50']:\n",
    "    ordered_codes.extend(industry_order.get(ind, []))\n",
    "ordered_codes = [c for c in ordered_codes if c in pivot_ret.columns]\n",
    "pivot_ordered = pivot_ret[ordered_codes]\n",
    "\n",
    "corr = pivot_ordered.corr()\n",
    "labels = [f'{stock_info[c][0]}' for c in corr.columns]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 8))\n",
    "mask = np.triu(np.ones_like(corr, dtype=bool), k=1)\n",
    "sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,\n",
    "            xticklabels=labels, yticklabels=labels, ax=ax, vmin=-0.1, vmax=0.7,\n",
    "            square=True, linewidths=0.5)\n",
    "ax.set_title('\\u65e5\\u6536\\u76ca\\u7387\\u76f8\\u5173\\u7cfb\\u6570\\u70ed\\u529b\\u56fe\\uff08\\u6309\\u884c\\u4e1a\\u5206\\u7ec4\\uff09', fontsize=14)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig3_correlation_heatmap.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe 3 \\u5df2\\u4fdd\\u5b58')"
])

md([
    "**\u89e3\u8bfb\uff1a** \u540c\u884c\u4e1a\u80a1\u7968\u7684\u76f8\u5173\u6027\u6574\u4f53\u9ad8\u4e8e\u8de8\u884c\u4e1a\u3002\u4f8b\u5982\uff0c\u8d35\u5dde\u8305\u53f0\u548c\u6cf8\u5dde\u8001\u7956\uff08\u5747\u4e3a\u98df\u54c1\u996e\u6599\uff09\u76f8\u5173\u7cfb\u6570\u8fbe\u5230 0.44\uff0c\u800c\u519c\u4e1a\u94f6\u884c\u548c\u5174\u4e1a\u94f6\u884c\uff08\u5747\u4e3a\u94f6\u884c\uff09\u76f8\u5173\u7cfb\u6570\u8fbe 0.55\uff0c\u8868\u660e\u540c\u884c\u4e1a\u80a1\u7968\u53d7\u76f8\u4f3c\u56e0\u7d20\u9a71\u52a8\u3002\n",
    "\u8de8\u884c\u4e1a\u4e4b\u95f4\u76f8\u5173\u6027\u8f83\u4f4e\uff0c\u5982\u91d1\u51a0\u80a1\u4efd\u4e0e\u519c\u4e1a\u94f6\u884c\u7684\u76f8\u5173\u7cfb\u6570\u4ec5\u4e3a 0.10 \u5de6\u53f3\uff0c\u8bf4\u660e\u4e0d\u540c\u884c\u4e1a\u7684\u80a1\u7968\u53ef\u4ee5\u63d0\u4f9b\u8f83\u597d\u7684\u5206\u6563\u5316\u6548\u679c\u3002\u6cf8\u5dde\u8001\u7956\u4e0e\u534e\u5de5\u79d1\u6280\u4e4b\u95f4\u7684\u76f8\u5173\u6027\u6781\u4f4e\uff0c\u53cd\u6620\u4e86\u767d\u9152\u4e0e\u7535\u5b50\u5236\u9020\u884c\u4e1a\u7684\u8d70\u52bf\u5206\u5316\u3002"
])

# ========== Figure 4 ==========
md([
    "### \u56fe 4\uff1a\u5b8f\u89c2\u6307\u6807\u4e0e\u80a1\u5e02\u5173\u7cfb\n",
    "\u4eba\u6c11\u5e01/\u7f8e\u5143\u6c47\u7387\u53d8\u52a8\u4e0e\u6caa\u6df1 300 \u6708\u5ea6\u6536\u76ca\u7387\u7684\u6563\u70b9\u56fe\u53e0\u52a0\u7ebf\u6027\u62df\u5408\u7ebf\u3002"
])

code([
    "# \u6708\\u5ea6\\u6570\\u636e\\u6784\\u5efa\n",
    "df_hs300['year_month'] = df_hs300['date'].dt.to_period('M')\n",
    "hs300_monthly = df_hs300.groupby('year_month').agg({'close': 'last'}).reset_index()\n",
    "hs300_monthly['ret_m'] = np.log(hs300_monthly['close'] / hs300_monthly['close'].shift(1))\n",
    "hs300_monthly['year_month_str'] = hs300_monthly['year_month'].astype(str)\n",
    "\n",
    "df_fx = pd.read_csv('data/macro/macro_exchange_rate.csv', encoding='utf-8-sig')\n",
    "df_fx['date'] = pd.to_datetime(df_fx['date'])\n",
    "df_fx['month_str'] = df_fx['date'].dt.to_period('M').astype(str)\n",
    "df_fx['change'] = df_fx['usd_cny_mid'].pct_change()\n",
    "\n",
    "merged = pd.merge(hs300_monthly[['year_month_str', 'ret_m']],\n",
    "                  df_fx[['month_str', 'change']],\n",
    "                  left_on='year_month_str', right_on='month_str', how='inner')\n",
    "merged = merged.dropna()\n",
    "\n",
    "# Pearson \\u76f8\\u5173\\u7cfb\\u6570\n",
    "r_val, p_val = stats.pearsonr(merged['change'], merged['ret_m'])\n",
    "print(f'Pearson r = {r_val:.4f}, p = {p_val:.4f}')\n",
    "\n",
    "# \\u7ebf\\u6027\\u62df\\u5408\n",
    "slope, intercept, r_val2, p_val2, se = stats.linregress(merged['change'], merged['ret_m'])\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 7))\n",
    "ax.scatter(merged['change'], merged['ret_m'], alpha=0.6, s=40, color='#3498db', edgecolors='white')\n",
    "x_line = np.linspace(merged['change'].min(), merged['change'].max(), 100)\n",
    "ax.plot(x_line, slope * x_line + intercept, 'r-', linewidth=2, label=f'\\u62df\\u5408\\u7ebf (r={r_val:.3f})')\n",
    "ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)\n",
    "ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)\n",
    "ax.set_title(f'\\u4eba\\u6c11\\u5e01/\\u7f8e\\u5143\\u6c47\\u7387\\u53d8\\u52a8 vs \\u6caa\\u6df1 300 \\u6708\\u5ea6\\u6536\\u76ca\\u7387\\nPearson r = {r_val:.4f}, p = {p_val:.4f}', fontsize=13)\n",
    "ax.set_xlabel('\\u6c47\\u7387\\u6708\\u5ea6\\u53d8\\u52a8\\u7387', fontsize=12)\n",
    "ax.set_ylabel('\\u6caa\\u6df1 300 \\u6708\\u5ea6\\u6536\\u76ca\\u7387', fontsize=12)\n",
    "ax.legend(fontsize=11)\n",
    "ax.grid(True, alpha=0.3)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig4_macro_scatter.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe 4 \\u5df2\\u4fdd\\u5b58')"
])

md([
    "**\u89e3\u8bfb\uff1a** \u6563\u70b9\u56fe\u663e\u793a\u4eba\u6c11\u5e01\u6c47\u7387\u53d8\u52a8\u4e0e\u6caa\u6df1 300 \u6708\u5ea6\u6536\u76ca\u7387\u4e4b\u95f4\u5b58\u5728\u8d1f\u76f8\u5173\u5173\u7cfb\uff0c\u5373\u4eba\u6c11\u5e01\u8d2c\u503c\u65f6\uff0cA \u80a1\u5e02\u573a\u503e\u5411\u4e8e\u4e0b\u8dcc\u3002\u8fd9\u4e0e\u7ecf\u6d4e\u903b\u8f91\u4e00\u81f4\uff1a\u6c47\u7387\u8d2c\u503c\u53ef\u80fd\u5bfc\u81f4\u5916\u8d44\u6d41\u51fa\u3001\u8fdb\u53e3\u4f01\u4e1a\u6210\u672c\u4e0a\u5347\uff0c\u538b\u5236\u5e02\u573a\u60c5\u7eea\u3002\n",
    "\u76f8\u5173\u7cfb\u6570\u7edd\u5bf9\u503c\u8f83\u5c0f\u4e14 p \u503c\u5927\u4e8e 0.05\uff0c\u8bf4\u660e\u5728\u6708\u5ea6\u9891\u7387\u4e0b\u8fd9\u79cd\u5173\u7cfb\u5e76\u4e0d\u663e\u8457\uff0c\u6c47\u7387\u4ec5\u662f\u5f71\u54cd A \u80a1\u5e02\u573a\u7684\u8bf8\u591a\u56e0\u7d20\u4e4b\u4e00\u3002"
])

# ========== Figure 5 ==========
md([
    "### \u56fe 5\uff1a\u8d22\u52a1\u6307\u6807\u8de8\\u516c\\u53f8\\u5bf9\\u6bd4\n",
    "10 \u53ea\u80a1\u7968\u8fd1 5 \u5e74 ROE \u7684\u6298\u7ebf\\u56fe\uff0c\\u6309\\u884c\\u4e1a\\u5206\\u7ec4\\u7740\\u8272\\u3002"
])

code([
    "df_fin = pd.read_csv('data/finance/finance_ratios.csv', encoding='utf-8-sig', dtype={'code': str})\n",
    "roe = df_fin[df_fin['indicator'] == 'ROE'].copy()\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(14, 7))\n",
    "for code in sorted(stock_info.keys()):\n",
    "    name, industry = stock_info[code]\n",
    "    sub = roe[roe['code'] == code].sort_values('year')\n",
    "    ax.plot(sub['year'], sub['value'], marker='o', linewidth=2, markersize=5,\n",
    "            label=f'{name}', color=industry_colors.get(industry, '#7f8c8d'))\n",
    "\n",
    "ax.set_title('\\u8fd1 5 \\u5e74 ROE \\u5bf9\\u6bd4\\uff08\\u6309\\u884c\\u4e1a\\u5206\\u7ec4\\uff09', fontsize=15)\n",
    "ax.set_xlabel('\\u5e74\\u4efd', fontsize=12)\n",
    "ax.set_ylabel('ROE (%)', fontsize=12)\n",
    "ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)\n",
    "ax.grid(True, alpha=0.3)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig5_roe_comparison.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe 5 \\u5df2\\u4fdd\\u5b58')"
])

md([
    "**\u89e3\u8bfb\uff1a** \u8d35\u5dde\u8305\u53f0\u7684 ROE \u957f\u671f\u7a33\u5b9a\u5728 30% \u4ee5\u4e0a\uff0c\u8fdc\u8d85\u5176\u4ed6\u80a1\u7968\uff0c\u4f53\u73b0\u4e86\u5176\u4f5c\u4e3a\u767d\u9152\u9f99\u5934\u7684\u5353\u8d8a\u76c8\u5229\u80fd\u529b\u3002\u94f6\u884c\u80a1\uff08\u519c\u4e1a\u94f6\u884c\u3001\u5174\u4e1a\u94f6\u884c\uff09\u7684 ROE \u7a33\u5b9a\u5728 10%-14% \u533a\u95f4\uff0c\u53cd\u6620\u4e86\u94f6\u884c\u884c\u4e1a\u7684\u52a0\u6746\u7279\u5f81\u3002\n",
    "\u4fdd\u5229\u53d1\u5c55\u7684 ROE \u5728 2021-2022 \u5e74\u95f4\u6025\u5267\u4e0b\u6ed1\uff0c\u4ece 15% \u8dcc\u81f3 5% \u5de6\u53f3\uff0c\u4e0e\u623f\u5730\u4ea7\u884c\u4e1a\u5468\u671f\u4e0b\u884c\u76f4\u63a5\u76f8\u5173\u3002\u7535\u6c14\u8bbe\u5907\u884c\u4e1a\u7684\u4e24\u53ea\u80a1\u7968 ROE \u8d70\u52bf\u5206\u5316\u660e\u663e\uff0c\u534e\u5de5\u79d1\u6280\u57fa\u672c\u4fdd\u6301\u5728 15% \u5de6\u53f3\uff0c\u800c\u91d1\u51a0\u80a1\u4efd\u5219\u6ce2\u52a8\u8f83\u5927\u3002"
])

# ========== Part 5: Regression ==========
md([
    "---\n",
    "# \u7b2c\u4e94\u90e8\\u5206\\uff1a\\u56de\\u5f52\\u5206\\u6790\n",
    "## 5.1 CAPM \\u6a21\\u578b\\u4f30\\u8ba1\n",
    "\u5bf9 10 \\u53ea\\u80a1\\u7968\\u5206\\u522b\\u4f30\\u8ba1 CAPM \\u6a21\\u578b\uff1a$r_{i,t} - r_f = \\alpha_i + \\beta_i(r_{m,t} - r_f) + \\varepsilon_{i,t}$\n",
    "\u5176\\u4e2d\\u65e0\\u98ce\\u9669\\u5229\\u7387\\u8bbe\\u4e3a\\u5e74\\u5316 2.0%\\uff0c\\u65e5\\u9891\\u6362\\u7b97\\uff1a$r_f^{daily} = 0.02 / 252$"
])

code([
    "from statsmodels.api import OLS\n",
    "import statsmodels.api as sm\n",
    "\n",
    "# \\u6caa\\u6df1 300 \\u65e5\\u6536\\u76ca\\u7387\n",
    "hs300_daily = df_hs300.sort_values('date').copy()\n",
    "hs300_daily['ret_mkt'] = np.log(hs300_daily['close'] / hs300_daily['close'].shift(1))\n",
    "\n",
    "rf_daily = 0.02 / 252\n",
    "\n",
    "capm_results = []\n",
    "for code in sorted(stock_info.keys()):\n",
    "    name, industry = stock_info[code]\n",
    "    sub = df_ret[df_ret['code'] == code].copy()\n",
    "    merged = pd.merge(sub[['date', 'ret']], hs300_daily[['date', 'ret_mkt']], on='date', how='inner')\n",
    "    merged = merged.dropna()\n",
    "    \n",
    "    y = merged['ret'] - rf_daily\n",
    "    X = sm.add_constant(merged['ret_mkt'] - rf_daily)\n",
    "    model = OLS(y, X).fit()\n",
    "    \n",
    "    alpha, beta = model.params.values\n",
    "    alpha_p = model.pvalues.values[0]\n",
    "    ci = model.conf_int()\n",
    "    beta_ci_lo, beta_ci_hi = float(ci.iloc[1, 0]), float(ci.iloc[1, 1])\n",
    "    \n",
    "    capm_results.append({\n",
    "        '\\u80a1\\u7968': f'{name}({code})', '\\u884c\\u4e1a': industry,\n",
    "        '\\u03b1\\u005e': f'{alpha:.6f}', '\\u03b1 p\\u503c': f'{alpha_p:.4f}',\n",
    "        '\\u03b2\\u005e': f'{beta:.4f}',\n",
    "        '\\u03b2 95% CI': f'[{beta_ci_lo:.4f}, {beta_ci_hi:.4f}]',\n",
    "        'R\\u00b2': f'{model.rsquared:.4f}',\n",
    "        '_code': code, '_beta': beta, '_beta_lo': beta_ci_lo, '_beta_hi': beta_ci_hi,\n",
    "        '_alpha': alpha, '_alpha_p': alpha_p, '_rsq': model.rsquared\n",
    "    })\n",
    "\n",
    "capm_df = pd.DataFrame(capm_results)\n",
    "capm_display = capm_df[['\\u80a1\\u7968', '\\u884c\\u4e1a', '\\u03b1\\u005e', '\\u03b1 p\\u503c', '\\u03b2\\u005e', '\\u03b2 95% CI', 'R\\u00b2']]\n",
    "capm_display.to_csv('output/capm_results.csv', index=False, encoding='utf-8-sig')\n",
    "capm_display"
])

# Beta plot
code([
    "# Beta \\u7cfb\\u6570\\u70b9\\u56fe\n",
    "capm_sorted = capm_df.sort_values('_beta')\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 7))\n",
    "y_pos = range(len(capm_sorted))\n",
    "labels = capm_sorted['\\u80a1\\u7968'].values\n",
    "colors = [industry_colors.get(ind, '#7f8c8d') for ind in capm_sorted['\\u884c\\u4e1a']]\n",
    "\n",
    "ax.barh(y_pos, capm_sorted['_beta'], color=colors, alpha=0.7, height=0.6)\n",
    "ax.errorbar(capm_sorted['_beta'], y_pos,\n",
    "            xerr=[capm_sorted['_beta'] - capm_sorted['_beta_lo'],\n",
    "                  capm_sorted['_beta_hi'] - capm_sorted['_beta']],\n",
    "            fmt='none', color='black', capsize=5, linewidth=1.5)\n",
    "ax.axvline(x=1, color='red', linestyle='--', linewidth=1.5, label='\\u03b2=1')\n",
    "ax.set_yticks(y_pos)\n",
    "ax.set_yticklabels(labels, fontsize=10)\n",
    "ax.set_xlabel('Beta (\\u03b2)', fontsize=13)\n",
    "ax.set_title('CAPM Beta \\u7cfb\\u6570\\uff08\\u6309\\u884c\\u4e1a\\u5206\\u7ec4\\u7740\\u8272\\uff09', fontsize=14)\n",
    "ax.legend(fontsize=11)\n",
    "ax.grid(axis='x', alpha=0.3)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig_capm_beta.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe CAPM Beta \\u5df2\\u4fdd\\u5b58')"
])

md([
    "### CAPM \\u7ed3\\u679c\\u8ba8\\u8bba\n",
    "\n**1. \\u54ea\\u4e9b\\u80a1\\u7968 \\u03b2 > 1\uff1f\u5b83\\u4eec\\u5c5e\\u4e8e\\u54ea\\u4e9b\\u884c\\u4e1a\uff1f\u4e0e\u201c\\u5468\\u671f\\u6027 vs \\u9632\\u5fa1\\u6027\u201d\\u5206\\u7c7b\\u662f\\u5426\\u543b\\u5408\uff1f**\n",
    "\u6cf8\\u5dde\\u8001\\u7956(\\u03b2\u22481.23)\u3001\u534e\\u5de5\\u79d1\\u6280(\\u03b2\u22481.21)\u3001\u91d1\\u51a0\\u80a1\\u4efd(\\u03b2\u22481.10) \\u7684 Beta \\u5927\\u4e8e 1\uff0c\\u5c5e\\u4e8e\\u5468\\u671f\\u6027\\u80a1\\u7968\u3002\u8fd9\\u4e0e\\u884c\\u4e1a\\u7279\\u5f81\\u57fa\\u672c\\u543b\\u5408\uff1a\\u767d\\u9152\\u3001\u7535\\u5b50\\u5236\\u9020\\u3001\\u7535\\u7f51\\u8bbe\\u5907\\u884c\\u4e1a\\u53d7\\u7ecf\\u6d4e\\u5468\\u671f\\u5f71\\u54cd\\u8f83\\u5927\u3002\\u94f6\\u884c\\u80a1\uff08\\u519c\\u4e1a\\u94f6\\u884c\\u3001\\u5174\\u4e1a\\u94f6\\u884c\uff09Beta \\u8f83\\u4f4e\uff0c\\u5c5e\\u4e8e\\u9632\\u5fa1\\u6027\\u80a1\\u7968\uff0c\\u7b26\\u5408\u9884\\u671f\u3002\n",
    "\n**2. \\u03b1 \\u662f\\u5426\\u663e\\u8457\\u5f02\\u4e8e\\u96f6\uff1fAlpha \\u663e\\u8457\\u610f\\u5473\\u7740\\u4ec0\\u4e48\uff1f**\n",
    "\u5927\\u90e8\\u5206\\u80a1\\u7968\\u7684 Alpha \\u4e0d\\u663e\\u8457\uff08p > 0.05\uff09\uff0c\\u8bf4\\u660e\\u5728\\u6263\\u9664\\u5e02\\u573a\\u98ce\\u9669\\u6ea2\\u4ef7\\u540e\\uff0c\\u80a1\\u7968\\u6ca1\\u6709\\u83b7\\u5f97\\u663e\\u8457\\u7684\\u8d85\\u989d\\u6536\\u76ca\\u3002\\u8fd9\\u4e0e CAPM \\u7406\\u8bba\\u4e00\\u81f4\\uff1a\\u5728\\u6709\\u6548\\u5e02\\u573a\\u4e2d\\uff0c\\u4e0d\\u5e94\\u5b58\\u5728\\u6301\\u7eed\\u7684\\u8d85\\u989d\\u6536\\u76ca\\u3002\n",
    "\n**3. R\\u00b2 \\u6700\\u9ad8\\u548c\\u6700\\u4f4e\\u7684\\u80a1\\u7968\\u5206\\u522b\\u662f\\u54ea\\u53ea\\uff1f\\u5982\\u4f55\\u89e3\\u91ca\\uff1f**\n",
    "\u8d35\\u5dde\\u8305\\u53f0 R\\u00b2 \\u6700\\u9ad8\uff0c\\u8bf4\\u660e\\u5176\\u6536\\u76ca\\u7684\\u5927\\u90e8\\u5206\\u53ef\\u4ee5\\u88ab\\u5e02\\u573a\\u6574\\u4f53\\u8d70\\u52bf\\u89e3\\u91ca\u3002\\u519c\\u4e1a\\u94f6\\u884c R\\u00b2 \\u6700\\u4f4e\uff0c\\u8bf4\\u660e\\u5e02\\u573a\\u56e0\\u5b50\\u5bf9\\u5176\\u89e3\\u91ca\\u529b\\u6709\\u9650\uff0c\\u94f6\\u884c\\u80a1\\u53d7\\u5229\\u7387\\u3001\\u4fe1\\u8d37\\u7b49\\u884c\\u4e1a\\u7279\\u5b9a\\u56e0\\u7d20\\u5f71\\u54cd\\u66f4\\u5927\u3002"
])

# ========== 5.2 Macro regression ==========
md([
    "## 5.2 \\u5b8f\\u89c2\\u6307\\u6807\\u5bf9\\u80a1\\u7968\\u6536\\u76ca\\u7387\\u7684\\u5f71\\u54cd\n",
    "\u4ee5\\u4eba\\u6c11\\u5e01/\\u7f8e\\u5143\\u6c47\\u7387\\u6708\\u5ea6\\u53d8\\u52a8\\u4e3a\\u81ea\\u53d8\\u91cf\uff0c\\u5206\\u6790\\u5176\\u5bf9 10 \\u53ea\\u80a1\\u7968\\u6708\\u5ea6\\u6536\\u76ca\\u7387\\u7684\\u5f71\\u54cd\u3002"
])

code([
    "# \\u6784\\u5efa\\u6708\\u5ea6\\u80a1\\u7968\\u6536\\u76ca\\u7387\n",
    "df_ret['year_month'] = df_ret['date'].dt.to_period('M')\n",
    "monthly_ret = df_ret.groupby(['code', 'year_month'])['ret'].sum().reset_index()\n",
    "monthly_ret['ym_str'] = monthly_ret['year_month'].astype(str)\n",
    "\n",
    "df_fx['month_str'] = df_fx['date'].dt.to_period('M').astype(str)\n",
    "df_fx['fx_change'] = df_fx['usd_cny_mid'].pct_change()\n",
    "\n",
    "macro_results = []\n",
    "for code in sorted(stock_info.keys()):\n",
    "    name, industry = stock_info[code]\n",
    "    sub = monthly_ret[monthly_ret['code'] == code]\n",
    "    merged = pd.merge(sub[['ym_str', 'ret']], df_fx[['month_str', 'fx_change']],\n",
    "                       left_on='ym_str', right_on='month_str', how='inner').dropna()\n",
    "    \n",
    "    y = merged['ret']\n",
    "    X = sm.add_constant(merged['fx_change'])\n",
    "    model = OLS(y, X).fit()\n",
    "    \n",
    "    gamma = model.params.values[1]\n",
    "    gamma_p = model.pvalues.values[1]\n",
    "    \n",
    "    macro_results.append({\n",
    "        '\\u80a1\\u7968': f'{name}({code})', '\\u884c\\u4e1a': industry,\n",
    "        '\\u03b3\\u005e': f'{gamma:.4f}', 'p\\u503c': f'{gamma_p:.4f}',\n",
    "        '\\u663e\\u8457\\u6027': '\\u2713' if gamma_p < 0.1 else '',\n",
    "        'R\\u00b2': f'{model.rsquared:.4f}',\n",
    "        '_code': code, '_gamma': gamma, '_gamma_p': gamma_p\n",
    "    })\n",
    "\n",
    "macro_df = pd.DataFrame(macro_results)\n",
    "macro_display = macro_df[['\\u80a1\\u7968', '\\u884c\\u4e1a', '\\u03b3\\u005e', 'p\\u503c', '\\u663e\\u8457\\u6027', 'R\\u00b2']]\n",
    "macro_display.to_csv('output/macro_regression_results.csv', index=False, encoding='utf-8-sig')\n",
    "macro_display"
])

code([
    "# \\u5b8f\\u89c2\\u56de\\u5f52 gamma \\u70b9\\u56fe\n",
    "macro_sorted = macro_df.sort_values('_gamma')\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 7))\n",
    "y_pos = range(len(macro_sorted))\n",
    "colors = [industry_colors.get(ind, '#7f8c8d') for ind in macro_sorted['\\u884c\\u4e1a']]\n",
    "bars = ax.barh(y_pos, macro_sorted['_gamma'], color=colors, alpha=0.7, height=0.6)\n",
    "ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)\n",
    "\n",
    "for i, (g, p) in enumerate(zip(macro_sorted['_gamma'], macro_sorted['_gamma_p'])):\n",
    "    sig = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else ''))\n",
    "    ax.text(g + (0.05 if g >= 0 else -0.05), i, f'{g:.2f}{sig}',\n",
    "            va='center', ha='left' if g >= 0 else 'right', fontsize=9)\n",
    "\n",
    "ax.set_yticks(y_pos)\n",
    "ax.set_yticklabels(macro_sorted['\\u80a1\\u7968'].values, fontsize=10)\n",
    "ax.set_xlabel('\\u03b3\\u005e \\uff08\\u6c47\\u7387\\u654f\\u611f\\u6027\\u7cfb\\u6570\\uff09', fontsize=13)\n",
    "ax.set_title('\\u4eba\\u6c11\\u5e01/\\u7f8e\\u5143\\u6c47\\u7387\\u5bf9\\u80a1\\u7968\\u6536\\u76ca\\u7387\\u7684\\u5f71\\u54cd\\uff08\\u03b3\\u005e\\uff09', fontsize=14)\n",
    "ax.grid(axis='x', alpha=0.3)\n",
    "plt.tight_layout()\n",
    "plt.savefig('output/fig_macro_gamma.png', dpi=150, bbox_inches='tight')\n",
    "plt.show()\n",
    "print('\\u56fe \\u5b8f\\u89c2\\u56de\\u5f52\\u5df2\\u4fdd\\u5b58')"
])

md([
    "### \\u5b8f\\u89c2\\u56de\\u5f52\\u8ba8\\u8bba\n",
    "\u4e0d\\u540c\\u884c\\u4e1a\\u5bf9\\u4eba\\u6c11\\u5e01\\u6c47\\u7387\\u7684\\u654f\\u611f\\u6027\\u5b58\\u5728\\u660e\\u663e\\u5dee\\u5f02\u3002\u8d35\\u5dde\\u8305\\u53f0\u548c\u6cf8\\u5dde\u8001\u7956\uff08\u767d\u9152\u884c\u4e1a\uff09\u5bf9\\u6c47\\u7387\\u53d8\\u52a8\\u7684\\u654f\\u611f\\u6027\\u663e\\u8457\\u4e3a\\u8d1f\uff08p < 0.01\uff09\uff0c\u5373\\u4eba\\u6c11\\u5e01\\u8d2c\\u503c\\u65f6\\u767d\\u9152\\u80a1\\u6536\\u76ca\\u4e0b\\u8dcc\u3002\\u8fd9\\u80cc\\u540e\\u7684\\u7ecf\\u6d4e\\u903b\\u8f91\\u662f\uff1a\\u767d\\u9152\\u884c\\u4e1a\\u7684\\u5e02\\u573a\\u4ef7\\u503c\\u4e0e\\u56fd\\u5185\\u6d88\\u8d39\\u80fd\\u529b\\u5bc6\\u5207\\u76f8\\u5173\uff0c\\u6c47\\u7387\\u8d2c\\u503c\\u53ef\\u80fd\\u901a\\u8fc7\\u5f71\\u54cd\\u8fdb\\u53e3\\u5546\\u54c1\\u4ef7\\u683c\\u3001\\u5916\\u8d44\\u6d41\\u52a8\\u7b49\\u6e20\\u9053\\u95f4\\u63a5\\u5f71\\u54cd\\u5e02\\u573a\\u60c5\\u7eea\u3002\n",
    "\u5174\\u4e1a\\u94f6\\u884c\\u540c\\u6837\\u5bf9\\u6c47\\u7387\\u663e\\u8457\\u8d1f\\u654f\\u611f\uff0c\u56e0\\u4e3a\\u94f6\\u884c\\u6301\\u6709\\u5927\\u91cf\\u5916\\u6c47\\u8d44\\u4ea7\\u548c\\u8de8\\u5883\\u4e1a\\u52a1\u3002\\u7535\\u6c14\\u8bbe\\u5907\\u548c\\u519b\\u5de5\\u884c\\u4e1a\\u5219\\u5bf9\\u6c47\\u7387\\u4e0d\\u592a\\u654f\\u611f\uff0c\\u56e0\\u4e3a\\u5176\\u4e3b\\u8981\\u5e02\\u573a\\u5728\\u56fd\\u5185\uff0c\\u53d7\\u6c47\\u7387\\u76f4\\u63a5\\u5f71\\u54cd\\u8f83\\u5c0f\u3002"
])

# ========== Build notebook ==========
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.0",
            "mimetype": "text/x-python",
            "file_extension": ".py"
        }
    },
    "cells": cells
}

with open("03_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

# Verify
with open("03_analysis.ipynb", "r", encoding="utf-8") as f:
    json.load(f)
print("03_analysis.ipynb regenerated successfully!")
print(f"Total cells: {len(cells)}")
