import os
import re


ui_dir = os.path.join(os.path.dirname(__file__), "src", "platform_base", "desktop", "ui_files")

files = ["compareSeriesDialog.ui", "shortcutsDialog.ui", "mathAnalysisDialog.ui",
         "annotationDialog.ui", "selectionToolbar.ui", "selectionInfo.ui", "uploadDialog.ui"]

for f in files:
    path = os.path.join(ui_dir, f)
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    spacers = list(re.finditer(r'<spacer name="([^"]+)">(.*?)</spacer>', content, re.DOTALL))
    bad = [s.group(1) for s in spacers if "sizeHint" not in s.group(2)]
    print(f"{f}: {len(spacers)} spacers, {len(bad)} bad: {bad}")
