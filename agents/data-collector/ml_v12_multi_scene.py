#!/usr/bin/env python3
"""V12 多场景回测"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
from itertools import product
from futu import *
import akshare as ak

INITIAL_CAPITAL = 1000000
TXN_COST = 0.001

print("="*80)
print("🤖 V12 多场景回测 - 沪深 300 全量 + 参数优化")
print("="*80)

# 市场状态
ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
ret, data, _ = ctx.request_history_kline('SH.000300', ktype=KLType.K_DAY, max_count=250)
if ret == RET_OK and data is not None:
    c = data['close'].values
    ma20, ma60, ma250 = data['close'].rolling(20).mean().values[-1], data['close'].rolling(60).mean().values[-1], data['close'].rolling(250).mean().values[-1]
    chg = (c[-1]-c[0])/c[0]*100
    bull = (c[-1]>ma20)+(c[-1]>ma60)+(c[-1]>ma250)+(2 if ma20>ma60>ma250 else 0)
    bear = (c[-1]<ma20)+(c[-1]<ma60)+(c[-1]<ma250)+(2 if ma20<ma60<ma250 else 0)
    if bull>=4 and chg>20: mstate='bull'
    elif bear>=4 and chg<-20: mstate='bear'
    else: mstate='oscillate'
    print(f"\n📈 市场:{'🐂牛市' if mstate=='bull' else '🐻熊市' if mstate=='bear' else '📊震荡市'} (沪深 300:{c[-1]:.0f}, 250 日:{chg:+.1f}%)")

# 股票池
hs300 = ['000001','000002','000063','000100','000157','000333','000538','000568','000596','000651','000661','000725','000776','000858','000895','002001','002027','002049','002129','002142','002230','002252','002304','002352','002415','002475','002594','002714','300014','300059','600000','600009','600016','600028','600030','600036','600048','600050','600104','600276','600309','600346','600436','600519','600585','600588','600690','600745','600809','600887','600893','600900','600905','600919','600938','601012','601066','601088','601166','601211','601225','601288','601318','601328','601390','601398','601601','601628','601633','601668','601688','601728','601766','601800','601816','601857','601888','601898','601899','601919']
print(f"\n📊 股票池:{len(hs300)}只")

# 基本面
print("\n📊 获取基本面...")
fund = {}
for code in tqdm(hs300, desc="基本面"):
    try:
        r = ak.stock_financial_analysis_indicator(symbol=code)
        if r is not None and len(r)>0:
            l = r.iloc[0]
            fund[code] = {'roe':float(l.get('净资产收益率 - 加权%',np.nan)) if '净资产收益率 - 加权%' in l.index else np.nan,'gross':float(l.get('销售毛利率%',np.nan)) if '销售毛利率%' in l.index else np.nan,'pe':float(l.get('市盈率 - 动态%',np.nan)) if '市盈率 - 动态%' in l.index else np.nan}
    except: pass
    time.sleep(0.1)
print(f"  ✅ {len(fund)}只")

# K 线
print("\n📊 获取 K 线...")
kdata = {}
for code in tqdm(hs300, desc="K 线"):
    try:
        ret,k,_ = ctx.request_history_kline(f'SH.{code}' if code.startswith('6') else f'SZ.{code}', ktype=KLType.K_DAY, max_count=500)
        if ret==RET_OK and k is not None and len(k)>100: kdata[code]=k.sort_values('time_key')
    except: pass
    time.sleep(0.15)
ctx.close()
print(f"  ✅ {len(kdata)}只")

# 回测
def backtest(hp, tk, w):
    al = []
    for code in kdata.keys():
        k = kdata[code].copy()
        if len(k)<200: continue
        c,v = k['close'],k['volume']
        mom = c.pct_change(10)*(v/v.rolling(20).mean())
        obv = (np.sign(c.diff())*v).rolling(20).sum().pct_change(10)
        cap = (mom*0.6+obv*0.4).fillna(0)
        if code in fund and not np.isnan(fund[code].get('pe',np.nan)) and fund[code]['pe']>0: val=pd.Series(1/(fund[code]['pe']+0.01),index=k.index)
        else: h52,l52=c.rolling(250).max(),c.rolling(250).min(); val=(1-(c-l52)/(h52-l52+0.01)).fillna(0)
        if code in fund and not np.isnan(fund[code].get('roe',np.nan)): roe=pd.Series(fund[code]['roe']/100,index=k.index)
        else: roe=(1/(c.pct_change().rolling(60).std()+0.01)).pct_change().fillna(0)
        gr = pd.Series(fund.get(code,{}).get('gross',10)/100,index=k.index) if code in fund else pd.Series(0.5,index=k.index)
        qual = (roe*0.6+gr*0.4).fillna(0)
        d = c.diff(); g,l = d.where(d>0,0).rolling(14).mean(),(-d.where(d<0,0)).rolling(14).mean()
        rsi = 100-(100/(1+g/l)); sent = ((50-rsi)/50).fillna(0)
        k['score'] = (cap*w['capital']+val*w['value']+qual*w['quality']+sent*w['sentiment'])
        k['score'] = (k['score']-k['score'].rolling(60).mean())/(k['score'].rolling(60).std()+0.01)
        k['label'] = c.shift(-hp).pct_change(hp)
        k = k.dropna()
        if len(k)>50: k['code']=code; al.append(k)
    if not al: return None
    ds = pd.concat(al, ignore_index=True)
    dates = sorted(ds['time_key'].unique())
    cap,pos,trades = INITIAL_CAPITAL,{},[]
    for date in dates[:-hp]:
        dd = ds[ds['time_key']==date]
        for code in list(pos.keys()):
            p = pos[code]
            if (pd.to_datetime(date)-pd.to_datetime(p['entry_date'])).days>=hp:
                sd = dd[dd['code']==code]
                if len(sd)>0:
                    ep = sd['close'].values[0]; pnl=(ep-p['entry_price'])*p['shares']-p['entry_price']*p['shares']*TXN_COST*2
                    cap += p['shares']*ep-p['entry_price']*p['shares']*TXN_COST*2; trades.append({'pnl':pnl}); del pos[code]
        if len(pos)<tk:
            top = dd.sort_values('score',ascending=False).head(tk-len(pos))
            for _,r in top.iterrows():
                sh = int(cap*0.15/r['close']/100)*100
                if sh>0 and cap>=r['close']*sh*(1+TXN_COST): cap-=r['close']*sh*(1+TXN_COST); pos[r['code']]={'entry_price':r['close'],'entry_date':date,'shares':sh}
    fv = cap
    for code,p in pos.items():
        sd = ds[ds['time_key']==dates[-1]]; sd=sd[sd['code']==code]
        if len(sd)>0: fv+=p['shares']*sd['close'].values[0]
    tr = (fv-INITIAL_CAPITAL)/INITIAL_CAPITAL*100
    wr = len([t for t in trades if t['pnl']>0])/len(trades)*100 if trades else 0
    return {'total_return':tr,'win_rate':wr,'trades':len(trades),'final_value':fv}

# 多场景
print("\n📈 多场景测试...")
hps = [10,20,30,60]; tks = [3,5,10]
if mstate=='bull': ws = [{'capital':0.40,'sentiment':0.20,'value':0.20,'quality':0.20,'name':'牛市进攻'},{'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10,'name':'均衡'}]
elif mstate=='bear': ws = [{'value':0.40,'quality':0.40,'capital':0.10,'sentiment':0.10,'name':'熊市防御'},{'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10,'name':'均衡'}]
else: ws = [{'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10,'name':'震荡均衡'},{'capital':0.40,'value':0.30,'quality':0.30,'sentiment':0.00,'name':'重资金'}]

rs = []; tot = len(hps)*len(tks)*len(ws)
for i,(hp,tk,w) in enumerate(product(hps,tks,ws),1):
    print(f"\n[{i}/{tot}] 持有{hp}天 | 持仓{tk}只 | {w['name']}")
    r = backtest(hp,tk,w)
    if r:
        rs.append({'holding_period':hp,'top_k':tk,'weights':w['name'],'total_return':r['total_return'],'win_rate':r['win_rate'],'trades':r['trades'],'final_value':r['final_value']})
        st = '✅' if r['total_return']>0 else '🟡' if r['win_rate']>50 else '❌'
        print(f"  {st} 收益:{r['total_return']:+.2f}% | 胜率:{r['win_rate']:.1f}% | 交易:{r['trades']}笔 | 终值:{r['final_value']:,.0f}元")
    else: print(f"  ❌ 数据不足")
    time.sleep(0.3)

# 汇总
print("\n"+"="*80)
print("📊 结果汇总")
print("="*80)
if rs:
    df = pd.DataFrame(rs).sort_values('total_return',ascending=False)
    print("\n🏆 TOP5:")
    for i,(_,r) in enumerate(df.head(5).iterrows(),1): print(f"  {i}. 持有{r['holding_period']}天|持仓{r['top_k']}只|{r['weights']} 收益:{r['total_return']:+.2f}% 胜率:{r['win_rate']:.1f}%")
    print("\n按持有期:")
    for hp in hps: s=df[df['holding_period']==hp]; print(f"  {hp}天：平均{s['total_return'].mean():+.2f}% 最高{s['total_return'].max():+.2f}%")
    print("\n按持仓数:")
    for tk in tks: s=df[df['top_k']==tk]; print(f"  {tk}只：平均{s['total_return'].mean():+.2f}% 最高{s['total_return'].max():+.2f}%")
    ts=datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v12_{ts}.json",'w') as f: json.dump({'ts':ts,'market':mstate,'results':rs,'top5':df.head(5).to_dict('records')},f,indent=2)
    print(f"\n💾 已保存:v12_{ts}.json")
