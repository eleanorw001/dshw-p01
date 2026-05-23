"""
run_notebooks.py: 执行所有 Notebook 并生成 report.html
"""
import subprocess
import sys
import os

PYTHON = sys.executable
os.chdir(os.path.dirname(os.path.abspath(__file__)))

notebooks = ['02_clean.ipynb', '03_analysis.ipynb']

for nb in notebooks:
    print(f"\n{'='*60}")
    print(f"执行: {nb}")
    print('='*60)
    result = subprocess.run(
        [PYTHON, '-m', 'nbconvert',
         '--to', 'notebook',
         '--execute',
         '--ExecutePreprocessor.timeout=600',
         '--inplace',
         nb],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  ✅ {nb} 执行完成")
    else:
        print(f"  ❌ {nb} 执行失败:")
        print(result.stderr[-2000:])

# 生成 report.html（从 03_analysis.ipynb 导出）
print(f"\n{'='*60}")
print("生成 report.html ...")
result = subprocess.run(
    [PYTHON, '-m', 'nbconvert',
     '--to', 'html',
     '03_analysis.ipynb',
     '--output', 'report.html',
     '--no-input',   # 隐藏代码，只保留输出和 Markdown
    ],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("  ✅ report.html 生成完成")
else:
    # 不加 --no-input 再试一次
    result2 = subprocess.run(
        [PYTHON, '-m', 'nbconvert',
         '--to', 'html',
         '03_analysis.ipynb',
         '--output', 'report.html'],
        capture_output=True, text=True
    )
    if result2.returncode == 0:
        print("  ✅ report.html（含代码版）生成完成")
    else:
        print(f"  ❌ report.html 生成失败: {result2.stderr[-1000:]}")

print("\n完成!")
