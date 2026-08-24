#!/usr/bin/env python3
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parent.parent
p=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))

def theme():
    return '''<style>
.bg{fill:#fff}.border{fill:none;stroke:#d0d7de}.fg{fill:#24292f}.muted{fill:#57606a}.accent{fill:#24292f}.rule{stroke:#d8dee4}
@media(prefers-color-scheme:dark){.bg{fill:#0d1117}.border{stroke:#30363d}.fg{fill:#c9d1d9}.muted{fill:#8b949e}.accent{fill:#f0f6fc}.rule{stroke:#30363d}}
text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}
</style>'''
cmd=f'{p["username"]}@github:~$ whoami'; name=f'{p["name"]}  //  {p["role"]}'
header=f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="138" viewBox="0 0 920 138" role="img" aria-label="Terminal header for {escape(p['name'])}">
{theme()}
<rect class="bg" x="1" y="1" width="918" height="136" rx="12"/><rect class="border" x="1" y="1" width="918" height="136" rx="12"/>
<circle cx="19" cy="18" r="4" class="muted" opacity=".65"/><circle cx="33" cy="18" r="4" class="muted" opacity=".45"/><circle cx="47" cy="18" r="4" class="muted" opacity=".3"/>
<text x="68" y="22" class="muted" font-size="10">profile.session</text>
<clipPath id="cmd"><rect x="20" y="36" width="0" height="23"><animate attributeName="width" from="0" to="410" dur="1.4s" fill="freeze"/></rect></clipPath>
<text x="20" y="54" class="fg" font-size="15" clip-path="url(#cmd)">{escape(cmd)}</text>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.45s" dur=".25s" fill="freeze"/><text x="20" y="84" class="fg" font-size="22" font-weight="700">{escape(name)}</text><text x="20" y="111" class="muted" font-size="12">{escape(p['tagline'])}</text></g>
<text x="880" y="54" class="accent" font-size="14">█<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></text>
</svg>'''
(ROOT/'assets'/'terminal-header.svg').write_text(header,encoding='utf-8')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="510" height="500" viewBox="0 0 510 500" role="img" aria-label="Neofetch-style profile information">',theme(),'<rect class="bg" x="1" y="1" rx="12" width="508" height="498"/><rect class="border" x="1" y="1" rx="12" width="508" height="498"/><circle cx="18" cy="18" r="4" class="muted" opacity=".65"/><circle cx="32" cy="18" r="4" class="muted" opacity=".45"/><circle cx="46" cy="18" r="4" class="muted" opacity=".3"/>',f'<text x="64" y="22" class="muted" font-size="10">{escape(p["username"])}@github</text>',f'<text x="22" y="58" class="accent" font-size="15" font-weight="700">{escape(p["username"])}@github</text>','<line x1="22" y1="69" x2="488" y2="69" class="rule"/>']
y=98
for idx,(k,v) in enumerate(p['rows']):
    delay=.18*idx+.25
    s.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".3s" fill="freeze"/><text x="22" y="{y}" class="accent" font-size="12">{escape(k)}</text><text x="105" y="{y}" class="fg" font-size="12">{escape(v)}</text></g>'); y+=34
s += [f'<line x1="22" y1="{y-12}" x2="488" y2="{y-12}" class="rule"/>',f'<text x="22" y="{y+18}" class="muted" font-size="11">featured:// public work</text>']; y+=48
for proj in p['featured'][:4]: s.append(f'<text x="22" y="{y}" class="fg" font-size="11">• {escape(proj["name"])}</text>'); y+=25
s += ['<text x="22" y="475" class="fg" font-size="11">$ status: building <tspan>█<animate attributeName="opacity" values="1;0;1" dur="1.05s" repeatCount="indefinite"/></tspan></text>','</svg>']
(ROOT/'assets'/'info-card.svg').write_text('\n'.join(s),encoding='utf-8')
print('Rendered terminal-header.svg and info-card.svg')
