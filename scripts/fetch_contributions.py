#!/usr/bin/env python3
from pathlib import Path
import datetime as dt, json, os, re
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
profile=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
username=os.getenv('GH_PROFILE_USER',profile['username'])
url=f'https://github.com/users/{username}/contributions'
out=ROOT/'data'/'contributions.json'
def parse_count(text):
    if not text or re.search(r'no contributions',text,re.I): return 0
    m=re.search(r'([0-9][0-9,]*)\s+contribution',text,re.I)
    return int(m.group(1).replace(',','')) if m else 0
def fetch_days():
    r=requests.get(url,headers={'User-Agent':'m-zia-rasa-profile/1.0','Accept-Language':'en-US,en;q=0.9'},timeout=30); r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    cells=soup.select('td.ContributionCalendar-day[data-date], rect.ContributionCalendar-day[data-date]') or soup.select('[data-date][data-level]')
    days={}
    for cell in cells:
        date=cell.get('data-date')
        if not date: continue
        level=int(cell.get('data-level') or 0); text=''; cid=cell.get('id')
        if cid:
            tip=soup.find('tool-tip',attrs={'for':cid})
            if tip: text=tip.get_text(' ',strip=True)
        if not text: text=cell.get('aria-label','')
        days[date]={'date':date,'count':parse_count(text),'level':level}
    if not days: raise RuntimeError('GitHub contribution markup changed: no dated cells found')
    return [days[k] for k in sorted(days)]
def calc(days):
    total=sum(d['count'] for d in days); active=sum(d['count']>0 for d in days); best=max(days,key=lambda d:d['count']) if days else {'date':None,'count':0}
    i=len(days)-1; streak=0
    if i>=0 and days[i]['count']==0: i-=1
    while i>=0 and days[i]['count']>0: streak+=1; i-=1
    longest=run=0
    for d in days: run=run+1 if d['count']>0 else 0; longest=max(longest,run)
    return {'total':total,'active_days':active,'current_streak':streak,'longest_streak':longest,'best_day':best}
days=fetch_days(); payload={'username':username,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'days':days,'stats':calc(days)}
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2),encoding='utf-8'); print(f'Fetched {len(days)} days for {username}')
