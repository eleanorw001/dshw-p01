import os
import glob
import pandas as pd
from datetime import datetime, timezone

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_DIR, "data", "stock")
DST_DIR = os.path.join(PROJECT_DIR, "data", "clean")
LOG_FILE = os.path.join(PROJECT_DIR, "download_log.txt")

os.makedirs(DST_DIR, exist_ok=True)

entries = []
for path in sorted(glob.glob(os.path.join(SRC_DIR, "*.csv"))):
    fname = os.path.basename(path)
    try:
        df = pd.read_csv(path)
        dst_path = os.path.join(DST_DIR, fname)
        df.to_csv(dst_path, index=False)
        rows, cols = df.shape
        t = datetime.now(timezone.utc).isoformat()
        entry = f"{t}\t{fname}\trows={rows}\tcols={cols}\tsrc={path}\tdst={dst_path}\n"
        entries.append(entry)
    except Exception as e:
        t = datetime.now(timezone.utc).isoformat()
        entries.append(f"{t}\t{fname}\tERROR\t{e}\n")

with open(LOG_FILE, "a", encoding="utf-8") as f:
    for e in entries:
        f.write(e)

print(f"Processed {len(entries)} files. Log appended to {LOG_FILE}.")
