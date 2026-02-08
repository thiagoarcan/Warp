"""Fix all spacer elements missing sizeHint in UI files."""
import os
import re


ui_dir = os.path.join(os.path.dirname(__file__), "src", "platform_base", "desktop", "ui_files")

files = ["compareSeriesDialog.ui", "shortcutsDialog.ui", "mathAnalysisDialog.ui",
         "annotationDialog.ui", "selectionToolbar.ui", "selectionInfo.ui"]

def add_sizehint_to_spacer(match):
    """Add sizeHint property to spacer element if missing."""
    full = match.group(0)
    if "sizeHint" in full:
        return full  # already has sizeHint

    # Determine orientation
    if "Qt::Horizontal" in full:
        w, h = 40, 20
    else:
        w, h = 20, 40

    sizehint = f"""       <property name="sizeHint" stdset="0">
        <size>
         <width>{w}</width>
         <height>{h}</height>
        </size>
       </property>"""

    # Insert sizeHint before </spacer>
    return full.replace("</spacer>", sizehint + "\n      </spacer>")

for f in files:
    path = os.path.join(ui_dir, f)
    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    original = content
    content = re.sub(
        r'<spacer name="[^"]+">.*?</spacer>',
        add_sizehint_to_spacer,
        content,
        flags=re.DOTALL,
    )

    if content != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"FIXED: {f}")
    else:
        print(f"OK: {f}")
