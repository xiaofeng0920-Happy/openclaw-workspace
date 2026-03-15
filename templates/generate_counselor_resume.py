#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理咨询师简历 PDF 生成脚本 - 使用 Noto CJK 字体
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# 注册 Noto CJK 中文字体
try:
    pdfmetrics.registerFont(TTFont('Chinese', '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'))
    print("✅ 已加载 Noto Sans CJK 字体")
except Exception as e:
    print(f"⚠️ 字体加载失败：{e}")
    # 备用字体
    try:
        pdfmetrics.registerFont(TTFont('Chinese', '/usr/share/fonts/truetype/arphic/ukai.ttc'))
        print("✅ 已加载 AR PL UKai 字体")
    except:
        print("⚠️ 使用默认字体（中文可能显示异常）")

def create_counselor_resume():
    """创建心理咨询师简历 PDF"""
    
    font_name = 'Chinese'
    
    # 创建文档
    doc = SimpleDocTemplate(
        "resume_counselor.pdf",
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=15,
        fontName=font_name
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10.5,
        fontName=font_name,
        leading=16
    )
    
    # 标题
    story.append(Paragraph("王美玲", title_style))
    story.append(Paragraph("资深心理咨询师 / 心理健康专家", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 基本信息
    story.append(Paragraph("📋 基本信息", section_style))
    basic_info = [
        ["手机：138-0000-0000", "邮箱：wangmeiling@counseling.com"],
        ["微信：meiling_mind", "地址：上海市静安区"],
        ["出生年月：1988.05", ""]
    ]
    basic_table = Table(basic_info, colWidths=[9*cm, 9*cm])
    basic_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 0.4*cm))
    
    # 求职意向
    story.append(Paragraph("🎯 求职意向", section_style))
    job_intent = """
    <b>期望职位：</b>资深心理咨询师 / 心理健康顾问 / 心理培训师
    <b>期望行业：</b>心理咨询/教育培训/健康管理
    <b>工作性质：</b>全职/兼职均可
    <b>期望薪资：</b>面议
    """
    story.append(Paragraph(job_intent, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 核心优势
    story.append(Paragraph("✨ 核心优势", section_style))
    advantages = """
    ✓ 8 年心理咨询临床经验，累计咨询时长 5000+ 小时
    ✓ 国家二级心理咨询师，中国心理学会注册心理师
    ✓ 擅长认知行为疗法 (CBT)、精神分析、家庭治疗
    ✓ 服务人群涵盖青少年、职场人士、婚姻家庭
    ✓ 具备危机干预经验，处理过 100+ 高危个案
    ✓ 优秀的共情能力和沟通技巧，来访者满意度 95%+
    """
    story.append(Paragraph(advantages, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 工作经历
    story.append(Paragraph("💼 工作经历", section_style))
    
    work1 = """
    <b>资深心理咨询师</b> | 心灵港湾心理咨询中心 | 2019.06 - 至今
    • 为来访者提供个体心理咨询、团体辅导和危机干预服务
    • 制定个性化治疗方案，跟踪评估咨询效果
    • 年接待来访者 300+ 人次，咨询满意度 96%
    • 成功干预高危个案 50+ 例，零安全事故
    • 开发"职场压力管理"课程，服务 20+ 家企业
    """
    story.append(Paragraph(work1, normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    work2 = """
    <b>心理咨询师</b> | 阳光心理健康服务中心 | 2016.08 - 2019.05
    • 提供青少年心理咨询、婚姻家庭咨询
    • 参与社区心理健康促进项目
    • 完成青少年咨询案例 400+ 例
    • 主导"考前减压"团体辅导，服务学生 500+ 人
    """
    story.append(Paragraph(work2, normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    work3 = """
    <b>心理咨询助理</b> | 心语工作室 | 2015.03 - 2016.07
    • 协助资深咨询师进行个案记录和档案管理
    • 负责来访者预约和初步访谈
    • 接听心理热线 1000+ 小时
    """
    story.append(Paragraph(work3, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 教育背景
    story.append(Paragraph("🎓 教育背景", section_style))
    edu1 = """
    <b>应用心理学 硕士</b> | 华东师范大学心理与认知科学学院 | 2012.09 - 2015.06
    研究方向：临床与咨询心理学 | GPA: 3.7/4.0
    """
    story.append(Paragraph(edu1, normal_style))
    
    edu2 = """
    <b>心理学 学士</b> | 北京师范大学心理学院 | 2008.09 - 2012.06
    荣誉：校级优秀毕业生、国家励志奖学金
    """
    story.append(Paragraph(edu2, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 专业资质
    story.append(Paragraph("📜 专业资质", section_style))
    certs = [
        ["证书名称", "颁发机构", "获得时间"],
        ["国家二级心理咨询师", "人力资源和社会保障部", "2014.11"],
        ["中国心理学会注册心理师", "中国心理学会", "2017.06"],
        ["CBT 认知行为疗法培训证书", "中国心理卫生协会", "2016.08"],
        ["沙盘游戏治疗师", "国际沙盘游戏治疗学会", "2018.03"]
    ]
    cert_table = Table(certs, colWidths=[5*cm, 6*cm, 3*cm])
    cert_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2c3e50')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(cert_table)
    story.append(Spacer(1, 0.4*cm))
    
    # 专业擅长
    story.append(Paragraph("🛠 专业擅长", section_style))
    skills = """
    <b>咨询流派：</b>认知行为疗法 (CBT)、精神分析与心理动力学、人本主义疗法、家庭系统治疗、正念认知疗法
    <b>擅长领域：</b>情绪问题（抑郁、焦虑）、人际关系、个人成长、压力管理、创伤疗愈
    <b>服务人群：</b>青少年 (12-18 岁)、青年职场人士、已婚夫妇/家庭、中老年群体
    """
    story.append(Paragraph(skills, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # 自我评价
    story.append(Paragraph("🌟 自我评价", section_style))
    self_eval = """
    <b>专业理念：</b>相信每个人都有自我成长的潜能，以真诚、接纳、共情的态度陪伴来访者走过人生低谷。
    
    <b>个人特质：</b>温和耐心，善于倾听 | 敏锐的洞察力和分析能力 | 持续学习，追求专业精进
    
    <b>职业愿景：</b>成为一名值得信赖的心理咨询师，帮助更多人获得心理健康和人生幸福。
    """
    story.append(Paragraph(self_eval, normal_style))
    
    # 生成 PDF
    doc.build(story)
    print("✅ PDF 生成成功：resume_counselor.pdf")
    print(f"📄 文件大小：{doc.pagesize}")

if __name__ == "__main__":
    create_counselor_resume()
