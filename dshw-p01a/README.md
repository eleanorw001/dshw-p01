# dshw-p01a：金融数据获取、管理与初步分析

本项目为作业 `ex_P02a_get_clean_fin_data` 的单独实现，工作目录为 `dshw-p01a`，与原仓库 `dshw-p01` 保持独立。

## 目录结构
- `01_download.ipynb`：数据下载
- `02_clean.ipynb`：数据清洗与存储
- `03_analysis.ipynb`：统计与回归分析
- `data/stock/`：个股原始行情 CSV
- `data/index/`：指数原始行情 CSV
- `data/macro/`：宏观指标 CSV
- `data/finance/`：财务指标 CSV
- `data/clean/`：清洗后数据
- `data/combined/`：合并后综合数据
- `output/`：分析结果 CSV 和图表输出
- `download_log.txt`：下载日志

## 运行说明
1. 进入项目目录：`cd dshw-p01a`
2. 创建并激活虚拟环境：
   - PowerShell: `python -m venv .venv`，`./.venv/Scripts/Activate.ps1`
   - Bash: `python -m venv .venv`，`source .venv/bin/activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 运行 `01_download.ipynb` 执行 akshare 数据摄取，或运行 `download_akshare.py`
   - `python download_akshare.py`
5. 运行 `02_clean.ipynb` 生成清洗后的数据集，或运行 `clean_data.py`
   - `python clean_data.py`
6. 运行 `03_analysis.ipynb` 进行 CAPM 回归、宏观回归与统计分析，或运行 `analysis.py`
   - `python analysis.py`
7. 查看 `download_log.txt`、`data/clean/` 和 `output/` 以确认数据与分析结果已保存

## 当前进度
- 已创建新项目目录 `dshw-p01a`
- 已准备并安装项目依赖
- 已实现 `akshare` 下载流程，`download_akshare.py` 和 `01_download.ipynb` 已切换到 `akshare` 数据
- 已下载 10 只个股行情、两只指数、两类宏观数据，以及 10 只股票的财务摘要
- 已实现清洗流程 `clean_data.py`，并生成 `data/clean/` 以及 `data/combined/combined_stocks.csv`
- 已更新 `01_download.ipynb`、`02_clean.ipynb` 和 `03_analysis.ipynb` 的执行逻辑