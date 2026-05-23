"""generate_report.py: 生成 report.html"""
import os, base64
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def img_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def img_tag(path, alt='', width='100%'):
    b64 = img_b64(path)
    return f'<img src="data:image/png;base64,{b64}" alt="{alt}" style="width:{width};max-width:900px;display:block;margin:16px auto;border-radius:6px;">'

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>P01 金融数据获取、管理与初步分析 - 分析报告</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:14px;color:#222;background:#f8f8f6;line-height:1.7}
.container{max-width:960px;margin:0 auto;padding:32px 24px}
h1{font-size:22px;font-weight:500;color:#1a1a1a;border-bottom:2px solid #185FA5;padding-bottom:10px;margin-bottom:24px}
h2{font-size:17px;font-weight:500;color:#185FA5;margin:32px 0 12px;border-left:3px solid #185FA5;padding-left:10px}
h3{font-size:15px;font-weight:500;color:#333;margin:20px 0 8px}
p{margin:8px 0;color:#444}
.meta{color:#888;font-size:12px;margin-bottom:28px}
.section{background:#fff;border-radius:8px;padding:24px 28px;margin-bottom:24px;border:0.5px solid #e8e8e4}
table{width:100%;border-collapse:collapse;font-size:13px;margin:12px 0}
th{background:#185FA5;color:#fff;padding:8px 12px;text-align:left;font-weight:500}
td{padding:7px 12px;border-bottom:0.5px solid #eee}
tr:nth-child(even) td{background:#f9f9f7}
.note{background:#f0f5ff;border-left:3px solid #185FA5;padding:10px 14px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px;color:#333}
.warn{background:#fff8f0;border-left:3px solid #854F0B;padding:10px 14px;border-radius:0 6px 6px 0;margin:12px 0;font-size:13px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0}
.metric{background:#f4f6fb;border-radius:6px;padding:12px 16px}
.metric .label{font-size:11px;color:#888;margin-bottom:4px}
.metric .value{font-size:18px;font-weight:500;color:#185FA5}
code{background:#f0f0ec;padding:1px 5px;border-radius:3px;font-family:monospace;font-size:12px}
</style>
</head>
<body>
<div class="container">
<h1>P01：金融数据获取、管理与初步分析</h1>
<p class="meta">作者：王佳（Eleanor）&nbsp;|&nbsp;中山大学 Data Science for Finance 课程作业&nbsp;|&nbsp;2026-05-23</p>

<!-- 数据说明 -->
<div class="section">
<h2>一、数据说明</h2>
<h3>1.1 自选股票列表</h3>
<table>
<tr><th>代码</th><th>名称</th><th>行业</th><th>选股理由</th></tr>
<tr><td>603685</td><td>晨丰科技</td><td>电气设备</td><td>新能源配套行业代表，近年高增长</td></tr>
<tr><td>603319</td><td>美湖股份</td><td>化工</td><td>精细化工细分龙头，行业典型标的</td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>食品饮料</td><td>白酒行业绝对龙头，长期价值个人偏好</td></tr>
<tr><td>601288</td><td>农业银行</td><td>银行</td><td>国有大行代表，低估值高股息</td></tr>
<tr><td>601166</td><td>兴业银行</td><td>银行</td><td>股份制银行代表，与农业银行对比</td></tr>
<tr><td>600048</td><td>保利发展</td><td>房地产</td><td>央企地产龙头，行业周期代表</td></tr>
<tr><td>000568</td><td>泸州老窖</td><td>食品饮料</td><td>高端白酒第二梯队，与茅台行业内对比</td></tr>
<tr><td>002179</td><td>中航光电</td><td>国防军工</td><td>军工电子核心标的，个人偏好</td></tr>
<tr><td>300510</td><td>金冠股份</td><td>电气设备</td><td>电网设备细分赛道，与晨丰同行业对比</td></tr>
<tr><td>000988</td><td>华工科技</td><td>电子</td><td>激光与光通信龙头，科技制造代表</td></tr>
</table>
<h3>1.2 数据来源</h3>
<div class="note">
<b>股票行情</b>：AKShare <code>ak.stock_zh_a_hist(adjust='hfq')</code>，后复权日度数据，2020-01-01 至 2026-05-23<br>
<b>市场指数</b>：沪深300（000300）+ 中证500（000905），来源：<code>ak.stock_zh_index_hist_csindex()</code><br>
<b>CPI 同比增速</b>：AKShare <code>ak.macro_china_cpi_yearly()</code><br>
<b>人民币/美元汇率</b>：AKShare <code>ak.currency_boc_safe()</code>，中国银行中间价月均值<br>
<b>财务指标</b>：AKShare <code>ak.stock_financial_analysis_indicator()</code>，ROE/净利润率/资产负债率/营收增速
</div>
<h3>1.3 存储方式</h3>
<p>基础方式：<b>CSV（方式 A）</b>——所有原始数据和清洗后数据以 CSV 格式存储；合并数据保存至 <code>data/combined/combined_data.csv</code>。</p>
<p>进阶方式：<b>Parquet（方式 B）</b>——清洗后股票数据额外保存 <code>data/clean/stock_clean.parquet</code>，用于展示列式存储的特性。</p>
<div class="warn">CSV 的局限：无法存储数据类型信息（每次读入需手动转换）；数据量超百万行时读写效率低下；不支持列式随机访问。</div>
</div>

<!-- 清洗说明 -->
<div class="section">
<h2>二、数据清洗说明</h2>
<h3>清洗流程概述</h3>
<p>对每只股票的原始数据依次完成：缺失值检测 → 向前填充（ffill）→ 日期转 <code>datetime64</code> 并设为索引 → 数值列类型校验 → 重复日期去重 → 极端收益率标注（<code>is_extreme = |return| > 20%</code>）。</p>
<h3>清洗结果汇总</h3>
<table>
<tr><th>代码</th><th>名称</th><th>原始行数</th><th>清洗后</th><th>重复删除</th><th>填充缺失</th><th>极端收益日</th></tr>
<tr><td>603685</td><td>晨丰科技</td><td>1543</td><td>1543</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>603319</td><td>美湖股份</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>601288</td><td>农业银行</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>601166</td><td>兴业银行</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>600048</td><td>保利发展</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>000568</td><td>泸州老窖</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>002179</td><td>中航光电</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
<tr><td>300510</td><td>金冠股份</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>1</td></tr>
<tr><td>000988</td><td>华工科技</td><td>1545</td><td>1545</td><td>0</td><td>1</td><td>0</td></tr>
</table>
<p>数据质量整体较好：无重复记录，缺失值极少（每只股票仅 1 处，来自数据源返回首行时的前向填充无法覆盖，属正常现象）。金冠股份存在 1 个极端收益日，标注保留，不删除。</p>
<h3>宽表 vs 长表</h3>
<p><b>宽表</b>（列=股票代码，行=日期）：适合相关系数计算、矩阵运算、多股票走势对比绘图。</p>
<p><b>长表</b>（每行=一只股票一天）：适合分组统计（<code>groupby</code>）、分面可视化、多表 merge 及数据库存储。两者互为转换，本项目通过 <code>pd.melt()</code> 完成宽→长转换。</p>
<h3>多表合并行数变化</h3>
<p>10 只股票纵向堆叠 → 15,448 行；与沪深 300 指数 left join → 行数不变（交易日高度重叠）；与月度汇率 left join（通过年月键映射）→ 行数不变，同月每日共享同一月均汇率值。综合数据最终保存为 <code>data/combined/combined_data.csv</code>（15,448 行 × 13 列）。</p>
</div>

<!-- 统计结果 -->
<div class="section">
<h2>三、描述性统计</h2>
<h3>4.1 日收益率基本统计量</h3>
<table>
<tr><th>代码</th><th>名称</th><th>行业</th><th>年化均值</th><th>年化波动率</th><th>偏度</th><th>超额峰度</th><th>最大回撤</th></tr>
<tr><td>603685</td><td>晨丰科技</td><td>电气设备</td><td>14.47%</td><td>37.63%</td><td>0.131</td><td>3.586</td><td>-76.59%</td></tr>
<tr><td>603319</td><td>美湖股份</td><td>化工</td><td>24.62%</td><td>49.51%</td><td>0.220</td><td>1.330</td><td>-77.95%</td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>食品饮料</td><td>4.64%</td><td>25.56%</td><td>0.202</td><td>3.550</td><td>-60.11%</td></tr>
<tr><td>601288</td><td>农业银行</td><td>银行</td><td>9.86%</td><td>11.52%</td><td>0.222</td><td>5.005</td><td>-20.33%</td></tr>
<tr><td>601166</td><td>兴业银行</td><td>银行</td><td>2.35%</td><td>19.45%</td><td>0.180</td><td>4.674</td><td>-41.09%</td></tr>
<tr><td>600048</td><td>保利发展</td><td>房地产</td><td>-8.07%</td><td>26.67%</td><td>0.534</td><td>3.505</td><td>-74.84%</td></tr>
<tr><td>000568</td><td>泸州老窖</td><td>食品饮料</td><td>4.16%</td><td>36.49%</td><td>0.120</td><td>2.508</td><td>-95.50%</td></tr>
<tr><td>002179</td><td>中航光电</td><td>国防军工</td><td>11.33%</td><td>34.93%</td><td>0.147</td><td>2.334</td><td>-59.77%</td></tr>
<tr><td>300510</td><td>金冠股份</td><td>电气设备</td><td>-9.43%</td><td>53.39%</td><td>0.180</td><td>5.276</td><td>-112.05%</td></tr>
<tr><td>000988</td><td>华工科技</td><td>电子</td><td>33.23%</td><td>47.12%</td><td>0.238</td><td>1.574</td><td>-75.04%</td></tr>
</table>
<div class="note">
所有股票偏度均为正（右偏），超额峰度均大于 0（尖峰肥尾），符合金融资产收益率的典型统计特征（Stylized Facts）。华工科技年化均值最高（33.23%），金冠股份波动率最大（53.39%）且最大回撤超过 100%（对数收益率计算），保利发展是唯一年化均值显著为负的股票（-8.07%）。
</div>
</div>

<!-- 图表 -->
<div class="section">
<h2>四、可视化分析</h2>
<h3>图 1：归一化收盘价走势（2020-01-01 = 1）</h3>
"""
html += img_tag('output/fig1_normalized_price.png', '归一化走势图')
html += """
<div class="note">以 2020 年初为基准，各股票表现分化显著。白酒类股票（贵州茅台、泸州老窖）在 2021 年前后录得最高涨幅，体现消费升级和流动性宽松环境下的强劲表现；银行和房地产股票长期低于沪深 300 基准，反映行业景气度的持续承压。军工（中航光电）和电气设备（晨丰科技）呈现明显的阶段性脉冲特征，与政策红利密切相关。</div>

<h3>图 2：日收益率分布图（2×5 分面，叠加正态曲线）</h3>
"""
html += img_tag('output/fig2_return_distribution.png', '收益率分布图')
html += """
<div class="note">所有股票的日收益率分布均呈现「尖峰肥尾」特征，峰部比正态曲线更尖锐，两侧尾部更厚，是金融资产收益率的普遍规律（Stylized Fact）。这意味着若以正态分布假设估计风险（如 VaR），将系统性低估极端损失概率。白酒类股票（贵州茅台、泸州老窖）σ 较小，小市值股票（晨丰科技、金冠股份）σ 较大，反映其更高的日度波动风险。</div>

<h3>图 3：收益率相关系数热力图（按行业排序）</h3>
"""
html += img_tag('output/fig3_correlation_heatmap.png', '相关系数热力图')
html += """
<div class="note">同行业内部相关性普遍高于跨行业，例如银行板块（农业银行与兴业银行）的相关系数明显高于银行与房地产之间的相关性，这验证了行业因子在 A 股市场中的重要性。整体来看，所有股票相关性均为正值，反映 A 股市场较强的同涨同跌特征，大多数相关系数集中在 0.3–0.6 区间。</div>

<h3>图 4：人民币/美元汇率月度变动 vs 沪深 300 月度收益率</h3>
"""
html += img_tag('output/fig4_macro_scatter.png', '宏观散点图')
html += """
<div class="note">散点图显示汇率月度变动与沪深 300 月度收益率之间呈负相关——人民币贬值往往对应 A 股负收益月份。经济逻辑：人民币贬值伴随资本外流压力，外资倾向减持 A 股，同时贬值常出现在经济下行期，与市场悲观情绪相互强化。然而散点分散程度较大，说明汇率并非唯一决定因素，宏观经济基本面和货币政策等同样重要。</div>

<h3>图 5：10 只股票 ROE 近 5 年走势（按行业分组）</h3>
"""
html += img_tag('output/fig5_roe_comparison.png', 'ROE对比图')
html += """
<div class="note">白酒类股票（贵州茅台、泸州老窖）ROE 持续位居前列，体现了高端消费品「轻资产、高壁垒、强定价权」的盈利特征。银行股 ROE 稳定在 10%–13%，受监管约束波动较小。保利发展 ROE 自 2021 年起明显下滑，直观反映房地产行业调控政策收紧和去杠杆的冲击。军工（中航光电）和电子（华工科技）ROE 近年有所改善，与国产替代政策驱动的业绩提升相吻合。</div>
</div>

<!-- CAPM -->
<div class="section">
<h2>五、CAPM 回归分析</h2>
<p>模型：r<sub>i,t</sub> - r<sub>f</sub> = α<sub>i</sub> + β<sub>i</sub>(r<sub>m,t</sub> - r<sub>f</sub>) + ε<sub>i,t</sub>，其中 r<sub>f</sub> = 2%/252（年化 2% 日化）</p>
<table>
<tr><th>代码</th><th>名称</th><th>行业</th><th>α（年化）</th><th>α p值</th><th>β</th><th>β 95%CI</th><th>R²</th></tr>
<tr><td>603685</td><td>晨丰科技</td><td>电气设备</td><td>0.1220</td><td>0.4030</td><td>0.5706</td><td>[0.475,0.666]</td><td>0.0814</td></tr>
<tr><td>603319</td><td>美湖股份</td><td>化工</td><td>0.2213</td><td>0.2368</td><td>0.9353</td><td>[0.812,1.058]</td><td>0.1262</td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>食品饮料</td><td>0.0218</td><td>0.7800</td><td>0.8913</td><td>[0.840,0.943]</td><td>0.4301</td></tr>
<tr><td>601288</td><td>农业银行</td><td>银行</td><td>0.0780</td><td>0.0873</td><td>0.1250</td><td>[0.095,0.155]</td><td>0.0416</td></tr>
<tr><td>601166</td><td>兴业银行</td><td>银行</td><td>0.0008</td><td>0.9911</td><td>0.5224</td><td>[0.478,0.567]</td><td>0.2552</td></tr>
<tr><td>600048</td><td>保利发展</td><td>房地产</td><td>-0.1039</td><td>0.2836</td><td>0.6206</td><td>[0.557,0.684]</td><td>0.1915</td></tr>
<tr><td>000568</td><td>泸州老窖</td><td>食品饮料</td><td>0.0152</td><td>0.8941</td><td>1.2303</td><td>[1.155,1.305]</td><td>0.4020</td></tr>
<tr><td>002179</td><td>中航光电</td><td>国防军工</td><td>0.0893</td><td>0.4869</td><td>0.7733</td><td>[0.689,0.858]</td><td>0.1733</td></tr>
<tr><td>300510</td><td>金冠股份</td><td>电气设备</td><td>-0.1199</td><td>0.5470</td><td>1.0950</td><td>[0.964,1.226]</td><td>0.1487</td></tr>
<tr><td>000988</td><td>华工科技</td><td>电子</td><td>0.3061</td><td>0.0667</td><td>1.2087</td><td>[1.099,1.318]</td><td>0.2326</td></tr>
</table>
"""
html += img_tag('output/fig_capm_beta.png', 'Beta点图')
html += """
<div class="note">
<b>β &gt; 1 的股票</b>：泸州老窖（β=1.23）、华工科技（β=1.21）、金冠股份（β=1.10）属「进攻型」标的，其收益率放大市场波动。这与周期性/成长性行业的理论判断基本吻合。<br>
<b>α 显著性</b>：所有股票的 α p 值均大于 0.05（农业银行 p=0.087 接近显著），符合弱式有效市场假说——个股超额收益难以持续。若 α 显著为正，则意味着 CAPM 遗漏了重要风险因子（如规模、价值、动量因子）。<br>
<b>R² 解释</b>：贵州茅台 R²=0.43 最高（受市场系统性影响最大），农业银行 R²=0.04 最低（个股特质驱动为主，分散化价值高）。
</div>
</div>

<!-- 宏观回归 -->
<div class="section">
<h2>六、宏观指标回归分析</h2>
<p>模型：r<sup>月</sup><sub>i,t</sub> = α<sub>i</sub> + γ<sub>i</sub>·X<sub>t</sub> + ε<sub>i,t</sub>，X = 人民币/美元汇率月度变动率（正=贬值）</p>
<table>
<tr><th>代码</th><th>名称</th><th>行业</th><th>γ（汇率敏感性）</th><th>p 值</th><th>显著性</th></tr>
<tr><td>603685</td><td>晨丰科技</td><td>电气设备</td><td>0.7317</td><td>0.4578</td><td></td></tr>
<tr><td>603319</td><td>美湖股份</td><td>化工</td><td>-0.9156</td><td>0.6496</td><td></td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>食品饮料</td><td>-2.2349</td><td>0.0072</td><td>***</td></tr>
<tr><td>601288</td><td>农业银行</td><td>银行</td><td>-0.0060</td><td>0.9865</td><td></td></tr>
<tr><td>601166</td><td>兴业银行</td><td>银行</td><td>-1.5672</td><td>0.0042</td><td>***</td></tr>
<tr><td>600048</td><td>保利发展</td><td>房地产</td><td>-1.2742</td><td>0.1205</td><td></td></tr>
<tr><td>000568</td><td>泸州老窖</td><td>食品饮料</td><td>-3.4428</td><td>0.0059</td><td>***</td></tr>
<tr><td>002179</td><td>中航光电</td><td>国防军工</td><td>-0.5729</td><td>0.5718</td><td></td></tr>
<tr><td>300510</td><td>金冠股份</td><td>电气设备</td><td>-0.7419</td><td>0.5997</td><td></td></tr>
<tr><td>000988</td><td>华工科技</td><td>电子</td><td>-0.4554</td><td>0.7520</td><td></td></tr>
</table>
"""
html += img_tag('output/fig_macro_gamma.png', '宏观回归gamma点图')
html += """
<div class="note">
显著负相关（p&lt;0.01）的股票为：贵州茅台（γ=-2.23）、兴业银行（γ=-1.57）、泸州老窖（γ=-3.44）。人民币贬值时这三只股票受到显著负面冲击，背后逻辑：贬值往往伴随外资撤出和经济下行预期，高估值消费股（茅台、泸州老窖）和银行股最先受到外资减仓压力。而电气设备、国防军工、电子类股票 γ 不显著，说明其月度收益率与汇率变动关系较弱，受行业特定政策因素（国产替代、电网投资）驱动更多。
</div>
</div>

<!-- 结论 -->
<div class="section">
<h2>七、主要结论</h2>
<p><b>1. 行业表现分化明显</b>：2020–2026 年间，科技成长（华工科技 +33% 年化）和精细化工（美湖股份）表现突出；房地产（保利发展）和金冠股份录得负年化收益，保利发展受调控政策冲击最为显著。</p>
<p><b>2. 收益率分布均呈尖峰肥尾</b>：正态分布假设不适用于本组所有股票，实际极端损失概率被正态假设低估，风险管理需使用更厚尾的分布（如 t 分布或历史模拟法）。</p>
<p><b>3. CAPM 解释力有限</b>：R² 均值约 0.22，说明市场系统性因素仅能解释约 22% 的个股收益率变动；农业银行等个股特质风险更低（R²=0.04），对投资组合的分散化价值更高。所有 α 均不显著，符合弱式有效市场。</p>
<p><b>4. 人民币贬值对高端消费股影响显著</b>：贵州茅台、泸州老窖、兴业银行在汇率贬值期间受到显著负面冲击（p&lt;0.01），经济机制为外资撤离叠加宏观下行预期。</p>
<p><b>5. 行业内相关性 &gt; 行业间相关性</b>：相关系数矩阵验证了行业因子的重要性，A 股整体同涨同跌特征显著，纯依赖个股分散化难以有效降低系统性风险。</p>
</div>

<p style="text-align:center;color:#bbb;font-size:12px;margin-top:24px;padding-bottom:16px">报告生成时间：2026-05-23 | dshw-p01 项目</p>
</div>
</body>
</html>"""

with open('report.html', 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize('report.html') / 1024
print(f"report.html 已生成: {size_kb:.0f} KB")
