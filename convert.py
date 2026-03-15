#!/usr/bin/env python3
import subprocess, openpyxl, re, os
from pathlib import Path

pdfs = sorted(Path('/home/admin/.openclaw/media/inbound').glob('BOC*.pdf'))
print(f'找到 {len(pdfs)} 个 PDF')

wb = openpyxl.Workbook()
wb.remove(wb.active)
all_data = []

for i, p in enumerate(pdfs):
    parts = p.stem.split('-')
    sh = f'{parts[1]}年{parts[2].lstrip("0")}月' if len(parts)>=3 else 'X'
    ws = wb.create_sheet(sh[:31])
    
    hd = ['序号','记账日','起息日','类型','凭证','摘要','借方','贷方','余额','机构','备注']
    for c,h in enumerate(hd,1): ws.cell(1,c,h)
    
    # 提取文本到临时文件
    tmp = f'/tmp/pdf_{i}.txt'
    subprocess.run(['pdftotext','-layout',str(p),tmp], timeout=30)
    
    with open(tmp) as f:
        row = 2
        for ln in f:
            if '|' not in ln or '序号' in ln or '合计' in ln: continue
            m = re.search(r'\|(\d+)\s*\|', ln)
            if m:
                pts = [x.strip() for x in ln.split('|')]
                for c,v in enumerate(pts[1:12],1):
                    if v and c<=11: ws.cell(row,c,v)
                all_data.append({'文件':p.name,'期间':sh,'data':pts})
                row += 1
        print(f'[{i+1}/{len(pdfs)}] {sh}: {row-2}条')
    os.remove(tmp)

# 汇总表
sws = wb.create_sheet('全部汇总',index=0)
h2 = ['文件','期间','序号','记账日','起息日','类型','凭证','摘要','借方','贷方','余额','机构','备注']
for c,h in enumerate(h2,1): sws.cell(1,c,h)
for r,d in enumerate(all_data,2):
    p = d['data']
    vals = [d['文件'],d['期间']]+p[1:12]
    for c,v in enumerate(vals[:13],1):
        if c<=13: sws.cell(r,c,v)

out = '银行对账单汇总.xlsx'
wb.save(out)
print(f'\n✅ {len(all_data)}条记录 | {out} ({os.path.getsize(out)/1024:.0f}KB)')
