#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理咨询师简历 PDF 生成脚本 - 精美彩色版
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import utils

# 注册中文字体
font_loaded = False
try:
    pdfmetrics.registerFont(TTFont('Chinese', '/usr/share/fonts/truetype/arphic/ukai.ttc'))
    print("✅ 已加载 AR PL UKai 字体")
    font_loaded = True
except Exception as e:
    print(f"⚠️ 字体加载失败：{e}")

# 配色方案
COLOR_PRIMARY = colors.HexColor('#5D3FD3')      # 主色 - 紫色
COLOR_SECONDARY = colors.HexColor('#8B5CF6')    # 次要色 - 浅紫
COLOR_ACCENT = colors.HexColor('#F59E0B')       # 强调色 - 金色
COLOR_TEXT = colors.HexColor('#1F2937')         # 文字色 - 深灰
COLOR_TEXT_LIGHT = colors.HexColor('#6B7280')   # 浅文字
COLOR_BG_LIGHT = colors.HexColor('#F9FAFB')     # 浅背景
COLOR_WHITE = colors.HexColor('#FFFFFF')        # 白色

def create_counselor_resume_colorful():
    """创建精美彩色版心理咨询师简历 PDF"""
    
    font_name = 'Chinese' if font_loaded else 'Helvetica'
    
    # 创建文档
    doc = SimpleDocTemplate(
        "resume_counselor_colorful.pdf",
        pagesize=A4,
        rightMargin=0,
        leftMargin=0,
        topMargin=0,
        bottomMargin=0
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # 自定义样式
    name_style = ParagraphStyle(
        'Name',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=COLOR_WHITE,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_WHITE,
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLOR_WHITE,
        spaceAfter=3,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=COLOR_PRIMARY,
        spaceAfter=10,
        spaceBefore=5,
        fontName=font_name
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10.5,
        fontName=font_name,
        textColor=COLOR_TEXT,
        leading=17
    )
    
    # ========== 页眉（彩色背景）==========
    header_data = [
        [Paragraph("王美玲", name_style)],
        [Paragraph("资深心理咨询师 / 心理健康专家", title_style)],
        [Paragraph("📱 138-0000-0000  |  ✉️ wangmeiling@counseling.com  |  💬 meiling_mind  |  📍 上海市静安区", contact_style)]
    ]
    header_table = Table(header_data, colWidths=[18*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(header_table)
    
    # 装饰线条
    story.append(Spacer(1, 0.3*cm))
    
    # ========== 核心优势（彩色卡片）==========
    story.append(Spacer(1, 0.2*cm))
    
    advantages_title = Paragraph("✨ 核心优势", section_style)
    story.append(advantages_title)
    
    advantages_data = [
        [Paragraph("✓ <b>8 年</b> 心理咨询临床经验，累计咨询时长 <b>5000+ 小时</b>", normal_style)],
        [Paragraph("✓ 国家二级心理咨询师，中国心理学会注册心理师", normal_style)],
        [Paragraph("✓ 擅长认知行为疗法 (CBT)、精神分析、家庭治疗", normal_style)],
        [Paragraph("✓ 服务人群涵盖青少年、职场人士、婚姻家庭", normal_style)],
        [Paragraph("✓ 具备危机干预经验，处理过 100+ 高危个案", normal_style)],
        [Paragraph("✓ 优秀的共情能力，来访者满意度 95%+", normal_style)]
    ]
    
    adv_table = Table(advantages_data, colWidths=[17*cm])
    adv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 2, COLOR_SECONDARY),
        ('ROUNDEDCORNERS', [0, 0, -1, -1], 8),
    ]))
    story.append(adv_table)
    story.append(Spacer(1, 0.4*cm))
    
    # ========== 工作经历 ==========
    section_work = Paragraph("💼 工作经历", section_style)
    story.append(section_work)
    
    # 工作 1
    work1_header = Table([[
        Paragraph("<b>资深心理咨询师</b>", normal_style),
        Paragraph("心灵港湾心理咨询中心", normal_style),
        Paragraph("<i>2019.06 - 至今</i>", normal_style)
    ]], colWidths=[6*cm, 7*cm, 4*cm])
    work1_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (0,0), COLOR_WHITE),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(work1_header)
    
    work1_content = """
    • 为来访者提供个体心理咨询、团体辅导和危机干预服务<br/>
    • 制定个性化治疗方案，跟踪评估咨询效果<br/>
    • 年接待来访者 300+ 人次，咨询满意度 96%<br/>
    • 成功干预高危个案 50+ 例，零安全事故<br/>
    • 开发"职场压力管理"课程，服务 20+ 家企业
    """
    story.append(Paragraph(work1_content, normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 工作 2
    work2_header = Table([[
        Paragraph("<b>心理咨询师</b>", normal_style),
        Paragraph("阳光心理健康服务中心", normal_style),
        Paragraph("<i>2016.08 - 2019.05</i>", normal_style)
    ]], colWidths=[6*cm, 7*cm, 4*cm])
    work2_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (0,0), COLOR_WHITE),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(work2_header)
    
    work2_content = """
    • 提供青少年心理咨询、婚姻家庭咨询<br/>
    • 参与社区心理健康促进项目<br/>
    • 完成青少年咨询案例 400+ 例<br/>
    • 主导"考前减压"团体辅导，服务学生 500+ 人
    """
    story.append(Paragraph(work2_content, normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 工作 3
    work3_header = Table([[
        Paragraph("<b>心理咨询助理</b>", normal_style),
        Paragraph("心语工作室", normal_style),
        Paragraph("<i>2015.03 - 2016.07</i>", normal_style)
    ]], colWidths=[6*cm, 7*cm, 4*cm])
    work3_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COLOR_ACCENT),
        ('TEXTCOLOR', (0,0), (0,0), COLOR_WHITE),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(work3_header)
    
    work3_content = """
    • 协助资深咨询师进行个案记录和档案管理<br/>
    • 负责来访者预约和初步访谈<br/>
    • 接听心理热线 1000+ 小时
    """
    story.append(Paragraph(work3_content, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # ========== 教育背景 ==========
    section_edu = Paragraph("🎓 教育背景", section_style)
    story.append(section_edu)
    
    edu1 = """
    <b>应用心理学 硕士</b> | 华东师范大学心理与认知科学学院 | <i>2012.09 - 2015.06</i><br/>
    研究方向：临床与咨询心理学 | GPA: 3.7/4.0
    """
    story.append(Paragraph(edu1, normal_style))
    
    edu2 = """
    <b>心理学 学士</b> | 北京师范大学心理学院 | <i>2008.09 - 2012.06</i><br/>
    荣誉：校级优秀毕业生、国家励志奖学金
    """
    story.append(Paragraph(edu2, normal_style))
    story.append(Spacer(1, 0.4*cm))
    
    # ========== 专业资质（彩色表格）==========
    section_cert = Paragraph("📜 专业资质", section_style)
    story.append(section_cert)
    
    certs = [
        [Paragraph("<b>证书名称</b>", normal_style), 
         Paragraph("<b>颁发机构</b>", normal_style), 
         Paragraph("<b>获得时间</b>", normal_style)],
        ["国家二级心理咨询师", "人力资源和社会保障部", "2014.11"],
        ["中国心理学会注册心理师", "中国心理学会", "2017.06"],
        ["CBT 认知行为疗法培训证书", "中国心理卫生协会", "2016.08"],
        ["沙盘游戏治疗师", "国际沙盘游戏治疗学会", "2018.03"],
        ["婚姻家庭咨询师", "中国家庭文化促进会", "2020.09"]
    ]
    
    cert_table = Table(certs, colWidths=[5*cm, 7*cm, 3*cm])
    cert_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), COLOR_WHITE),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_SECONDARY),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_WHITE, COLOR_BG_LIGHT]),
    ]))
    story.append(cert_table)
    story.append(Spacer(1, 0.4*cm))
    
    # ========== 专业擅长（彩色标签风格）==========
    section_skills = Paragraph("🛠 专业擅长", section_style)
    story.append(section_skills)
    
    skills_data = [
        [Paragraph("<b>咨询流派：</b>认知行为疗法 (CBT)、精神分析与心理动力学、人本主义疗法、家庭系统治疗、正念认知疗法", normal_style)],
        [Paragraph("<b>擅长领域：</b>情绪问题（抑郁、焦虑）、人际关系、个人成长、压力管理、创伤疗愈", normal_style)],
        [Paragraph("<b>服务人群：</b>青少年 (12-18 岁)、青年职场人士、已婚夫妇/家庭、中老年群体", normal_style)]
    ]
    
    skills_table = Table(skills_data, colWidths=[17*cm])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 2, COLOR_ACCENT),
        ('ROUNDEDCORNERS', [0, 0, -1, -1], 8),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 0.4*cm))
    
    # ========== 自我评价 ==========
    section_self = Paragraph("🌟 自我评价", section_style)
    story.append(section_self)
    
    self_eval = """
    <b>专业理念：</b>相信每个人都有自我成长的潜能，以真诚、接纳、共情的态度陪伴来访者走过人生低谷。<br/><br/>
    <b>个人特质：</b>温和耐心，善于倾听 | 敏锐的洞察力和分析能力 | 持续学习，追求专业精进<br/><br/>
    <b>职业愿景：</b>成为一名值得信赖的心理咨询师，帮助更多人获得心理健康和人生幸福。
    """
    story.append(Paragraph(self_eval, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 底部装饰线
    footer_line = Table([[Paragraph("", normal_style)]], colWidths=[18*cm])
    footer_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 3, COLOR_PRIMARY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(footer_line)
    
    # 生成 PDF
    doc.build(story)
    print("✅ 精美彩色版 PDF 生成成功：resume_counselor_colorful.pdf")

if __name__ == "__main__":
    create_counselor_resume_colorful()
