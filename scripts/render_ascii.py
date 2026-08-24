#!/usr/bin/env python3
from pathlib import Path
from html import escape
import json

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
p = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
avatar = ROOT / "assets" / "source-avatar.webp"

img = cv2.imread(str(avatar))
if img is None:
    raise RuntimeError(f"Could not read avatar: {avatar}")

h, w = img.shape[:2]
mask = np.zeros((h, w), np.uint8)
bgd = np.zeros((1, 65), np.float64)
fgd = np.zeros((1, 65), np.float64)
cv2.grabCut(img, mask, (4, 2, w - 8, h - 4), bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)

fg = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
fg = cv2.GaussianBlur(fg.astype(np.float32), (5, 5), 0)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8)).apply(gray)

cols, rows = 58, 38
small = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)
ms = cv2.resize(fg, (cols, rows), interpolation=cv2.INTER_AREA)
ramp = "@%#*+=-:. "

art = []
for y in range(rows):
    line = []
    for x in range(cols):
        if ms[y, x] < 0.34:
            line.append(" ")
            continue
        value = (float(small[y, x]) / 255.0) ** 0.88
        char = ramp[min(len(ramp) - 1, int(value * (len(ramp) - 1)))]
        if value > 0.94 and ms[y, x] < 0.72:
            char = " "
        line.append(char)
    art.append("".join(line).rstrip())

style = '''<style>
.bg{fill:#fff}.border{fill:none;stroke:#d0d7de}.fg{fill:#24292f}.muted{fill:#57606a}
@media(prefers-color-scheme:dark){.bg{fill:#0d1117}.border{stroke:#30363d}.fg{fill:#c9d1d9}.muted{fill:#8b949e}}
text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}
</style>'''

s = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="390" height="500" viewBox="0 0 390 500" role="img" aria-label="Animated ASCII portrait of {escape(p["name"])}">',
    style,
    '<rect class="bg" x="1" y="1" rx="12" width="388" height="498"/>',
    '<rect class="border" x="1" y="1" rx="12" width="388" height="498"/>',
    '<circle cx="18" cy="18" r="4" class="muted" opacity=".65"/>',
    '<circle cx="32" cy="18" r="4" class="muted" opacity=".45"/>',
    '<circle cx="46" cy="18" r="4" class="muted" opacity=".3"/>',
    f'<text x="63" y="22" class="muted" font-size="10">portrait://{escape(p["username"])}</text>',
]

x0, y0, line_h = 18, 42, 10.6
for i, line in enumerate(art):
    y = y0 + i * line_h
    cid = f"row{i}"
    begin = 0.06 * i
    dur = max(0.18, min(0.42, len(line) * 0.008))
    s.append(
        f'<clipPath id="{cid}"><rect x="{x0}" y="{y-9:.1f}" height="12" width="0">'
        f'<animate attributeName="width" from="0" to="360" dur="{dur:.2f}s" begin="{begin:.2f}s" fill="freeze"/>'
        "</rect></clipPath>"
    )
    s.append(
        f'<text xml:space="preserve" x="{x0}" y="{y:.1f}" class="fg" font-size="10.2" clip-path="url(#{cid})">{escape(line)}</text>'
    )

end_y = y0 + len(art) * line_h + 22
s += [
    f'<text x="18" y="{end_y:.1f}" class="muted" font-size="10">render: monochrome / local / self-hosted</text>',
    f'<text x="18" y="{end_y+20:.1f}" class="fg" font-size="11">$ identity --resolved ✓</text>',
    "</svg>",
]

(ROOT / "assets" / "ascii-portrait.svg").write_text("\n".join(s), encoding="utf-8")
print("Rendered ascii-portrait.svg")
