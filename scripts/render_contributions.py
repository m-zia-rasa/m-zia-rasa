#!/usr/bin/env python3
from pathlib import Path
from html import escape
import datetime as dt, json
ROOT=Path(__file__).resolve().parent.parent
D=json.loads((ROOT/'data'/'contributions.json').read_text(encoding='utf-8')); OUT=ROOT/'assets'/'contrib-heatmap.svg'
W,H,left,top,cell,gap=920,230,63,70,11,4
def sunday(d): return d-dt.timedelta(days=(d.weekday()+1)%7)
days={dt.date.fromisoformat(x['date']):x for x in D['days']}; end=max(days) if days else dt.date.today(); start=sunday(end)-dt.timedelta(weeks=52)
months=[]; last=None
for week in range(53):
    d=start+dt.timedelta(weeks=week); key=(d.year,d.month)
    if key!=last: months.append((week,d.strftime('%b'))); last=key
stats=D.get('stats',{}); user=D.get('username','')
style='''<style>.bg{fill:#fff}.border{fill:none;stroke:#d0d7de}.fg{fill:#24292f}.muted{fill:#57606a}.l0{fill:#afb8c1;opacity:.14}.l1{fill:#57606a;opacity:.34}.l2{fill:#57606a;opacity:.52}.l3{fill:#24292f;opacity:.68}.l4{fill:#24292f;opacity:.9}@media(prefers-color-scheme:dark){.bg{fill:#0d1117}.border{stroke:#30363d}.fg{fill:#c9d1d9}.muted{fill:#8b949e}.l0{fill:#8b949e;opacity:.13}.l1{fill:#8b949e;opacity:.35}.l2{fill:#c9d1d9;opacity:.48}.l3{fill:#c9d1d9;opacity:.68}.l4{fill:#f0f6fc;opacity:.92}}text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}</style>'''
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub contribution heatmap for {escape(user)}">',style,'<rect class="bg" x="1" y="1" width="918" height="228" rx="12"/><rect class="border" x="1" y="1" width="918" height="228" rx="12"/>',f'<text x="20" y="28" class="fg" font-size="13" font-weight="700">contributions://{escape(user)}</text>',f'<text x="20" y="47" class="muted" font-size="10">total {stats.get("total",0)} • active {stats.get("active_days",0)}d • current streak {stats.get("current_streak",0)}d • longest {stats.get("longest_streak",0)}d</text>']
for week,label in months: s.append(f'<text x="{left+week*(cell+gap)}" y="62" class="muted" font-size="9">{label}</text>')
for label,dow in [('Mon',1),('Wed',3),('Fri',5)]: s.append(f'<text x="18" y="{top+dow*(cell+gap)+9}" class="muted" font-size="9">{label}</text>')
for week in range(53):
    for dow in range(7):
        d=start+dt.timedelta(weeks=week,days=dow); info=days.get(d,{'level':0}); level=max(0,min(4,int(info.get('level',0)))); x=left+week*(cell+gap); y=top+dow*(cell+gap); delay=(week*7+dow)*.0018
        s.append(f'<rect class="l{level}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".22s" fill="freeze"/></rect>')
s += [f'<text x="20" y="211" class="muted" font-size="10">updated {escape(D.get("generated_at","")[:10])} • public GitHub contribution HTML • self-hosted SVG</text>','</svg>']
OUT.write_text('\n'.join(s),encoding='utf-8'); print('Rendered contrib-heatmap.svg')
