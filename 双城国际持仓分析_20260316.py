#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双城国际持仓分析脚本
按产品拆分监控子表，统计、分析各产品持仓情况
"""

import xlrd
import json
from datetime import datetime
from collections import defaultdict

# 文件路径
FILE_PATH = '/home/admin/.openclaw/media/inbound/双城国际持仓记录 20260313.xls---e280215b-4d6a-4565-a933-3b6cede6f09a'

def parse_excel():
    """解析 Excel 文件"""
    workbook = xlrd.open_workbook(FILE_PATH)
    data = {}
    
    for sheet_name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(sheet_name)
        rows = []
        for i in range(sheet.nrows):
            row = sheet.row_values(i)
            if any(str(cell).strip() for cell in row):
                rows.append(row)
        data[sheet_name] = rows
    
    return data

def analyze_fund_holdings(data):
    """分析基金持仓数据"""
    results = {}
    
    # === Two Cities Fund I SP ===
    fund1 = {
        '产品名称': 'Two Cities Fund I SP',
        '持仓货币': 'CNY',
        '总持仓市值': 0,
        '总成本': 0,
        '总估值收益': 0,
        '持仓债券数': 0,
        '债券持仓': [],
        '外汇远期': [],
        '合规检查': {}
    }
    
    # 从基金持仓表提取 Fund I 数据 (行 8-16)
    fund_holdings = data.get('基金持仓', [])
    for i, row in enumerate(fund_holdings):
        if len(row) > 25 and i in [8, 9, 10, 11, 12, 13, 14, 15, 16]:
            try:
                bond = {
                    '序号': row[0] if row[0] else i,
                    '债券名称': row[1] if len(row) > 1 else '',
                    'ISIN': row[2] if len(row) > 2 else '',
                    '简称': row[4] if len(row) > 4 else '',
                    '面值总量': row[5] if len(row) > 5 else 0,
                    '交易价格': row[6] if len(row) > 6 else 0,
                    '到期收益率': row[8] if len(row) > 8 else 0,
                    '交割日期': row[10] if len(row) > 10 else '',
                    '2 月估值': row[12] if len(row) > 12 else 0,
                    '3 月估值': row[13] if len(row) > 13 else 0,
                    '4 月估值': row[14] if len(row) > 14 else 0,
                    '5 月估值': row[15] if len(row) > 15 else 0,
                    '6 月估值': row[16] if len(row) > 16 else 0,
                    '7 月估值': row[17] if len(row) > 17 else 0,
                    '当前市值': row[25] if len(row) > 25 else 0,
                    '估值收益': row[26] if len(row) > 26 else 0,
                    '到期日': row[22] if len(row) > 22 else '',
                    '到期年限': row[24] if len(row) > 24 else 0,
                }
                fund1['债券持仓'].append(bond)
                fund1['总持仓市值'] += float(bond['当前市值'] or 0)
                fund1['估值收益'] += float(bond['估值收益'] or 0)
                fund1['持仓债券数'] += 1
            except Exception as e:
                pass
    
    # 外汇远期数据 (行 19-23)
    for i, row in enumerate(fund_holdings):
        if len(row) > 20 and i in [20, 21, 22]:
            try:
                fx = {
                    '交易日期': row[1] if len(row) > 1 else '',
                    '交易品种': row[2] if len(row) > 2 else '',
                    '远期汇率': row[3] if len(row) > 3 else 0,
                    'USD 金额': row[4] if len(row) > 4 else 0,
                    'CNY 金额': row[5] if len(row) > 5 else 0,
                    '到期日': row[19] if len(row) > 19 else '',
                    '平仓盈亏': row[20] if len(row) > 20 else 0,
                }
                fund1['外汇远期'].append(fx)
            except Exception as e:
                pass
    
    # 汇总行 17
    fund1['总持仓市值'] = 30676912.2
    fund1['总估值收益'] = -161735.0
    fund1['需平仓 USD'] = 15044039.0
    
    results['Two Cities Fund I SP'] = fund1
    
    # === Two Cities Fund II SP ===
    fund2 = {
        '产品名称': 'Two Cities Fund II SP',
        '持仓货币': 'CNY/USD',
        '总持仓市值': 0,
        '总成本': 0,
        '持仓债券数': 0,
        '债券持仓': []
    }
    
    for i, row in enumerate(fund_holdings):
        if len(row) > 25 and i in [27, 28, 29]:
            try:
                bond = {
                    '序号': row[0] if row[0] else i,
                    '债券名称': row[1] if len(row) > 1 else '',
                    'ISIN': row[2] if len(row) > 2 else '',
                    '简称': row[4] if len(row) > 4 else '',
                    '面值总量': row[5] if len(row) > 5 else 0,
                    '交易价格': row[6] if len(row) > 6 else 0,
                    '到期收益率': row[8] if len(row) > 8 else 0,
                    '当前市值': row[25] if len(row) > 25 else 0,
                    '估值收益': row[26] if len(row) > 26 else 0,
                    '到期日': row[22] if len(row) > 22 else '',
                    '到期年限': row[24] if len(row) > 24 else 0,
                }
                fund2['债券持仓'].append(bond)
                fund2['总持仓市值'] += float(bond['当前市值'] or 0)
                fund2['持仓债券数'] += 1
            except Exception as e:
                pass
    
    results['Two Cities Fund II SP'] = fund2
    
    # === 银河国际账户 1 ===
    galaxy1 = {
        '产品名称': '银河国际账户 1',
        '总持仓市值': 10787910.47,
        '总成本': 9827716.0,
        '总估值收益': 394500.84,
        '持仓债券数': 0,
        '债券持仓': [],
        '货基持仓': 303162.92,
        '现金': 71403.31
    }
    
    holdings1 = data.get('银河持仓 1', [])
    for i, row in enumerate(holdings1):
        if len(row) > 20 and i in [2, 3, 4, 5, 6, 7, 8]:
            try:
                bond = {
                    '债券名称': row[2] if len(row) > 2 else '',
                    'ISIN': row[3] if len(row) > 3 else '',
                    '买卖方向': row[4] if len(row) > 4 else '',
                    '净价': row[5] if len(row) > 5 else 0,
                    '数量 (面值)': row[6] if len(row) > 6 else 0,
                    '交割金额': row[7] if len(row) > 7 else 0,
                    '券种': row[8] if len(row) > 8 else '',
                    '交易对手': row[9] if len(row) > 9 else '',
                    '成本': row[10] if len(row) > 10 else 0,
                    '估值 + 收益': row[11] if len(row) > 11 else 0,
                    '本月市值': row[12] if len(row) > 12 else 0,
                    'BBG 价格': row[17] if len(row) > 17 else 0,
                    '0227 估值': row[18] if len(row) > 18 else 0,
                    '到期日': row[19] if len(row) > 19 else '',
                    '到期年限': row[20] if len(row) > 20 else 0,
                }
                galaxy1['债券持仓'].append(bond)
                galaxy1['持仓债券数'] += 1
            except Exception as e:
                pass
    
    results['银河国际账户 1'] = galaxy1
    
    # === 银河国际账户 2 ===
    galaxy2 = {
        '产品名称': '银河国际账户 2',
        '总持仓市值': 10121453.88,
        '总成本': 3834215.0,
        '总估值收益': 76162.97,
        '持仓债券数': 0,
        '债券持仓': [],
        '现金': 11395.53
    }
    
    holdings2 = data.get('银河持仓 2', [])
    for i, row in enumerate(holdings2):
        if len(row) > 20 and i in [2, 3, 4, 5, 6, 7, 8]:
            try:
                bond = {
                    '债券名称': row[2] if len(row) > 2 else '',
                    'ISIN': row[3] if len(row) > 3 else '',
                    '买卖方向': row[4] if len(row) > 4 else '',
                    '净价': row[5] if len(row) > 5 else 0,
                    '收益率': row[6] if len(row) > 6 else 0,
                    '数量 (面值)': row[7] if len(row) > 7 else 0,
                    '交割金额': row[8] if len(row) > 8 else 0,
                    '券种': row[9] if len(row) > 9 else '',
                    '交易对手': row[10] if len(row) > 10 else '',
                    '成本': row[11] if len(row) > 11 else 0,
                    '估值 + 收益': row[12] if len(row) > 12 else 0,
                    '本月市值': row[13] if len(row) > 13 else 0,
                    '到期日': row[20] if len(row) > 20 else '',
                    '到期年限': row[22] if len(row) > 22 else 0,
                }
                galaxy2['债券持仓'].append(bond)
                galaxy2['持仓债券数'] += 1
            except Exception as e:
                pass
    
    results['银河国际账户 2'] = galaxy2
    
    return results

def check_compliance(fund_data):
    """合规检查"""
    compliance = {
        '单一债券集中度': [],
        '单一省份城投集中度': defaultdict(float),
        '久期检查': [],
        '杠杆率': 0
    }
    
    total_value = fund_data.get('总持仓市值', 0)
    if total_value == 0:
        return compliance
    
    for bond in fund_data.get('债券持仓', []):
        bond_value = float(bond.get('当前市值') or bond.get('本月市值') or 0)
        if bond_value > 0:
            concentration = bond_value / total_value * 100
            compliance['单一债券集中度'].append({
                '债券': bond.get('债券名称', ''),
                '市值': bond_value,
                '集中度%': round(concentration, 2)
            })
            
            # 检查是否超过 20%
            if concentration > 20:
                compliance['单一债券集中度'][-1]['超标'] = True
        
        # 提取省份信息（从简称中）
        name = bond.get('简称', '') or bond.get('债券名称', '')
        province_map = {
            '山东': '山东', '威海': '山东', '滨州': '山东',
            '洛阳': '河南', '青岛': '山东', '齐河': '山东',
            '潍坊': '山东', '成都': '四川', '达州': '四川',
            '江油': '四川', '枣发': '山东'
        }
        for prov, prov_name in province_map.items():
            if prov in name:
                compliance['单一省份城投集中度'][prov_name] += bond_value
                break
        
        # 久期检查
        duration = float(bond.get('到期年限') or 0)
        if duration > 3:
            compliance['久期检查'].append({
                '债券': bond.get('债券名称', ''),
                '久期': duration,
                '超标': True
            })
    
    # 省份集中度检查
    for province, value in compliance['单一省份城投集中度'].items():
        pct = value / total_value * 100 if total_value > 0 else 0
        compliance['单一省份城投集中度'][province] = {
            '金额': value,
            '集中度%': round(pct, 2),
            '超标': pct > 20
        }
    
    return compliance

def generate_report(results):
    """生成分析报告"""
    report = []
    report.append("=" * 80)
    report.append("双城国际持仓分析报告")
    report.append(f"报告日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 80)
    report.append("")
    
    # 总体概览
    report.append("【总体概览】")
    report.append("-" * 40)
    total_aum = 0
    for name, data in results.items():
        aum = data.get('总持仓市值', 0)
        total_aum += aum
        report.append(f"  {name}: {aum:,.2f}")
    report.append(f"  合计：{total_aum:,.2f}")
    report.append("")
    
    # 各产品详情
    for prod_name, data in results.items():
        report.append("=" * 80)
        report.append(f"【{prod_name}】")
        report.append("=" * 80)
        report.append(f"  总持仓市值：{data.get('总持仓市值', 0):,.2f}")
        report.append(f"  总成本：{data.get('总成本', 0):,.2f}")
        report.append(f"  估值收益：{data.get('总估值收益', 0):,.2f}")
        report.append(f"  持仓债券数：{data.get('持仓债券数', 0)}")
        report.append("")
        
        # 债券持仓明细
        report.append("  【债券持仓明细】")
        report.append("  " + "-" * 70)
        for i, bond in enumerate(data.get('债券持仓', []), 1):
            report.append(f"  {i}. {bond.get('债券名称', '')}")
            report.append(f"     ISIN: {bond.get('ISIN', '')}")
            report.append(f"     面值：{bond.get('面值总量', bond.get('数量 (面值)', 0)):,.0f}")
            report.append(f"     价格：{bond.get('交易价格', bond.get('净价', 0))}")
            report.append(f"     收益率：{bond.get('到期收益率', bond.get('收益率', 'N/A'))}")
            report.append(f"     市值：{bond.get('当前市值', bond.get('本月市值', 0)):,.2f}")
            report.append(f"     到期日：{bond.get('到期日', 'N/A')}")
            report.append(f"     久期：{bond.get('到期年限', 'N/A')} 年")
            report.append("")
        
        # 合规检查
        compliance = check_compliance(data)
        report.append("  【合规检查】")
        report.append("  " + "-" * 70)
        
        # 单一债券集中度
        report.append("  单一债券集中度 (限制≤20%):")
        for item in compliance['单一债券集中度']:
            flag = " ⚠️ 超标" if item.get('超标') else " ✓"
            report.append(f"    - {item['债券'][:30]}: {item['集中度%']}%{flag}")
        
        # 省份集中度
        report.append("  单一省份城投集中度 (限制≤20%):")
        for prov, info in compliance['单一省份城投集中度'].items():
            if isinstance(info, dict):
                flag = " ⚠️ 超标" if info.get('超标') else " ✓"
                report.append(f"    - {prov}: {info['集中度%']}%{flag}")
        
        # 久期检查
        report.append("  久期检查 (限制≤3 年):")
        if compliance['久期检查']:
            for item in compliance['久期检查']:
                report.append(f"    - {item['债券'][:30]}: {item['久期']} 年 ⚠️ 超标")
        else:
            report.append("    ✓ 所有债券久期符合要求")
        
        report.append("")
    
    return "\n".join(report)

def main():
    print("正在解析 Excel 文件...")
    data = parse_excel()
    
    print(f"找到 {len(data)} 个工作表：{list(data.keys())}")
    print("\n正在分析持仓数据...")
    
    results = analyze_fund_holdings(data)
    
    print("\n生成分析报告...")
    report = generate_report(results)
    
    # 保存报告
    report_path = '/home/admin/openclaw/workspace/双城国际持仓分析报告_20260316.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存 JSON 数据
    json_path = '/home/admin/openclaw/workspace/双城国际持仓数据_20260316.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析报告已保存：{report_path}")
    print(f"✅ JSON 数据已保存：{json_path}")
    print("\n" + report)

if __name__ == '__main__':
    main()
