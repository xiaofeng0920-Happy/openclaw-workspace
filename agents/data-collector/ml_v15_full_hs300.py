#!/usr/bin/env python3
"""V15 沪深 300 全量回测 + 权重优化"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, '/home/admin/openclaw/workspace')
import pandas as pd, numpy as np
from datetime import datetime
from tqdm import tqdm
from futu import *
import akshare as ak

print("="*80)
print("🤖 V15 沪深 300 全量回测 + 权重优化")
print("="*80)

ctx = OpenQuoteContext(host='127.0.0.1', port=11112)

# 市场状态
ret, data, _ = ctx.request_history_kline('SH.000300', ktype=KLType.K_DAY, max_count=250)
mstate = 'oscillate'
if ret == RET_OK and data is not None:
    c = data['close'].values
    ma20, ma60, ma250 = data['close'].rolling(20).mean().values[-1], data['close'].rolling(60).mean().values[-1], data['close'].rolling(250).mean().values[-1]
    chg = (c[-1]-c[0])/c[0]*100
    bull = (c[-1]>ma20)+(c[-1]>ma60)+(c[-1]>ma250)+(2 if ma20>ma60>ma250 else 0)
    bear = (c[-1]<ma20)+(c[-1]<ma60)+(c[-1]<ma250)+(2 if ma20<ma60<ma250 else 0)
    if bull>=4 and chg>20: mstate='bull'
    elif bear>=4 and chg<-20: mstate='bear'
    print(f"\n📈 市场:{'🐂牛市' if mstate=='bull' else '🐻熊市' if mstate=='bear' else '📊震荡市'} (沪深 300:{c[-1]:.0f}, 250 日:{chg:+.1f}%)")

# 沪深 300 全量成分股
print("\n📊 获取沪深 300 全量成分股...")
hs300_full = [
    '000001','000002','000063','000100','000157','000333','000538','000568','000596','000651',
    '000661','000725','000776','000858','000895','002001','002027','002049','002129','002142',
    '002230','002252','002304','002352','002415','002475','002594','002714','300014','300059',
    '300122','300124','300142','300274','300312','300347','300413','300433','300498','300601',
    '300628','300750','300759','300760','300782','300896','600000','600009','600016','600028',
    '600030','600031','600036','600048','600050','600104','600276','600309','600346','600436',
    '600519','600585','600588','600690','600745','600809','600887','600893','600900','600905',
    '600919','600938','601012','601066','601088','601166','601211','601225','601288','601318',
    '601328','601390','601398','601601','601628','601633','601668','601688','601728','601766',
    '601800','601816','601857','601888','601898','601899','601919','601988','601995','601998',
    '603259','603288','603799','603986','603993'
]
print(f"  股票池:{len(hs300_full)}只")

# 基本面筛选 (PE<30, ROE>10%)
print("\n📊 PE+ROE 筛选...")
fundamental = {}
for code in tqdm(hs300_full, desc="筛选"):
    try:
        ret = ak.stock_financial_analysis_indicator(symbol=code)
        if ret is None or len(ret)==0: continue
        latest = ret.iloc[0]
        pe = float(latest.get('市盈率 - 动态%',np.nan)) if '市盈率 - 动态%' in latest.index else np.nan
        roe_col = None
        for col in ret.columns:
            if '净资产收益率' in col and '%' in col: roe_col=col; break
        roe_vals = ret[roe_col].head(12).values if roe_col else []
        roe_min = np.nanmin(roe_vals) if len(roe_vals)>0 else np.nan
        if np.isnan(pe) or pe>30: continue
        if np.isnan(roe_min) or roe_min<=10: continue
        fundamental[code] = {'pe':pe,'roe_avg':np.nanmean(roe_vals)}
    except: continue
    time.sleep(0.1)

if len(fundamental)<20:
    print(f"\n⚠️  筛选后仅{len(fundamental)}只，放宽条件...")
    for code in hs300_full:
        try:
            ret = ak.stock_financial_analysis_indicator(symbol=code)
            if ret is None or len(ret)==0: continue
            latest = ret.iloc[0]
            pe = float(latest.get('市盈率 - 动态%',np.nan)) if '市盈率 - 动态%' in latest.index else np.nan
            if np.isnan(pe) or pe>50: continue
            fundamental[code] = {'pe':pe,'roe_avg':12}
        except: continue
        time.sleep(0.1)

qualified = list(fundamental.keys())
print(f"  ✅ 筛选后:{len(qualified)}只")

# K 线
print("\n📊 获取 K 线...")
kdata = {}
for code in tqdm(qualified, desc="K 线"):
    try:
        ret,k,_ = ctx.request_history_kline(f'SH.{code}' if code.startswith('6') else f'SZ.{code}', ktype=KLType.K_DAY, max_count=500)
        if ret==RET_OK and k is not None and len(k)>100:
            kdata[code]=k.sort_values('time_key')
    except: pass
    time.sleep(0.15)
ctx.close()
print(f"  ✅ {len(kdata)}只")

# 回测
print("\n📈 回测测试...")
def backtest(hp, tk, w):
    al = []
    for code in kdata.keys():
        k = kdata[code].copy()
        if len(k)<200: continue
        c,v = k['close'],k['volume']
        mom = c.pct_change(10)*(v/v.rolling(20).mean())
        obv = (np.sign(c.diff())*v).rolling(20).sum().pct_change(10)
        cap = (mom*0.6+obv*0.4).fillna(0)
        if code in fundamental and not np.isnan(fundamental[code].get('pe',np.nan)) and fundamental[code]['pe']>0:
            val=pd.Series(1/(fundamental[code]['pe']+0.01),index=k.index)
        else:
            h52,l52=c.rolling(250).max(),c.rolling(250).min()
            val=(1-(c-l52)/(h52-l52+0.01)).fillna(0)
        if code in fundamental and not np.isnan(fundamental[code].get('roe_avg',np.nan)):
            roe=pd.Series(fundamental[code]['roe_avg']/100,index=k.index)
        else:
            roe=(1/(c.pct_change().rolling(60).std()+0.01)).pct_change().fillna(0)
        qual = roe.fillna(0)
        d = c.diff(); g,l = d.where(d>0,0).rolling(14).mean(),(-d.where(d<0,0)).rolling(14).mean()
        rsi = 100-(100/(1+g/l)); sent = ((50-rsi)/50).fillna(0)
        k['score'] = (cap*w['capital']+val*w['value']+qual*w['quality']+sent*w['sentiment'])
        k['score'] = (k['score']-k['score'].rolling(60).mean())/(k['score'].rolling(60).std()+0.01)
        k = k.dropna()
        if len(k)>50: k['code']=code; al.append(k)
    if not al: return None
    ds = pd.concat(al, ignore_index=True)
    dates = sorted(ds['time_key'].unique())
    cap,pos,trades = 1000000,{},[]
    for date in dates[:-hp]:
        dd = ds[ds['time_key']==date]
        for code in list(pos.keys()):
            p = pos[code]
            if (pd.to_datetime(date)-pd.to_datetime(p['entry_date'])).days>=hp:
                sd = dd[dd['code']==code]
                if len(sd)>0:
                    ep = sd['close'].values[0]
                    pnl=(ep-p['entry_price'])*p['shares']-p['entry_price']*p['shares']*0.002
                    cap += p['shares']*ep-p['entry_price']*p['shares']*0.002
                    trades.append({'pnl':pnl})
                    del pos[code]
        if len(pos)<tk:
            top = dd.sort_values('score',ascending=False).head(tk-len(pos))
            for _,r in top.iterrows():
                sh = int(cap*0.15/r['close']/100)*100
                if sh>0 and cap>=r['close']*sh*1.001:
                    cap-=r['close']*sh*1.001
                    pos[r['code']]={'entry_price':r['close'],'entry_date':date,'shares':sh}
    fv = cap
    for code,p in pos.items():
        sd = ds[ds['time_key']==dates[-1]]; sd=sd[sd['code']==code]
        if len(sd)>0: fv+=p['shares']*sd['close'].values[0]
    return (fv-1000000)/1000000*100, len([t for t in trades if t['pnl']>0])/len(trades)*100 if trades else 0, len(trades), fv

# 测试不同权重组合（固定 10 天/5 只）
print("\n  测试权重组合 (持有 10 天/持仓 5 只):")
weight_sets = [
    {'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10,'name':'均衡'},
    {'capital':0.40,'value':0.30,'quality':0.30,'sentiment':0.00,'name':'重资金'},
    {'capital':0.20,'value':0.40,'quality':0.40,'sentiment':0.00,'name':'重价值质量'},
    {'capital':0.50,'value':0.20,'quality':0.20,'sentiment':0.10,'name':'激进资金'},
    {'capital':0.25,'value':0.25,'quality':0.25,'sentiment':0.25,'name':'高情绪'},
]

results = []
for w in weight_sets:
    r = backtest(10, 5, w)
    if r:
        results.append({'weights':w['name'],'return':r[0],'win_rate':r[1],'trades':r[2],'final':r[3]})
        st = '✅' if r[0]>0 else '🟡' if r[1]>50 else '❌'
        print(f"    {st} {w['name']}:收益{r[0]:+.2f}% 胜率{r[1]:.1f}% 交易{r[2]}笔")

# 测试不同持有期（固定 5 只，均衡权重）
print("\n  测试持有期 (持仓 5 只/均衡权重):")
w_eq = {'capital':0.30,'value':0.30,'quality':0.30,'sentiment':0.10}
for hp in [5,7,10,12,15,20]:
    r = backtest(hp, 5, w_eq)
    if r:
        results.append({'hp':hp,'tk':5,'weights':'均衡','return':r[0],'win_rate':r[1],'trades':r[2],'final':r[3]})
        st = '✅' if r[0]>0 else '🟡' if r[1]>50 else '❌'
        print(f"    {st} {hp}天：收益{r[0]:+.2f}% 胜率{r[1]:.1f}% 交易{r[2]}笔")

# 测试不同持仓数（固定 10 天，均衡权重）
print("\n  测试持仓数 (持有 10 天/均衡权重):")
for tk in [3,5,7,10,15]:
    r = backtest(10, tk, w_eq)
    if r:
        results.append({'hp':10,'tk':tk,'weights':'均衡','return':r[0],'win_rate':r[1],'trades':r[2],'final':r[3]})
        st = '✅' if r[0]>0 else '🟡' if r[1]>50 else '❌'
        print(f"    {st} {tk}只：收益{r[0]:+.2f}% 胜率{r[1]:.1f}% 交易{r[2]}笔")

# 汇总
print("\n"+"="*80)
print("📊 结果汇总")
print("="*80)
if results:
    df = pd.DataFrame(results).sort_values('return',ascending=False)
    print("\n🏆 TOP5:")
    for i,(_,r) in enumerate(df.head(5).iterrows(),1):
        if 'weights' in r:
            print(f"  {i}. {r.get('hp','10')}天/{r.get('tk',5)}只/{r['weights']}:收益{r['return']:+.2f}% 胜率{r['win_rate']:.1f}%")
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(Path("/home/admin/openclaw/workspace/agents/data-collector/backtest_results")/f"v15_{ts}.json",'w') as f:
        json.dump({'ts':ts,'market':mstate,'pool_size':len(qualified),'results':results,'top5':df.head(5).to_dict('records')},f,indent=2,ensure_ascii=False)