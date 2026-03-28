#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送邮件 - 使用 QQ 邮箱 SMTP
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "openclaw@qq.com"  # 需要配置
SENDER_PASSWORD = ""  # 需要配置授权码
RECEIVER_EMAIL = "30355627@qq.com"

def send_email_with_attachment(subject, body, attachment_path, receiver):
    """发送带附件的邮件"""
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver
    msg['Subject'] = subject
    
    # 添加正文
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加附件
    if attachment_path:
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{Path(attachment_path).name}"'
            )
            msg.attach(part)
    
    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 邮件已发送至 {receiver}")
        return True
    except Exception as e:
        print(f"❌ 发送失败：{e}")
        return False

if __name__ == '__main__':
    # 测试
    subject = "📊 产品持仓明细 Excel 报表 (2026-03-26)"
    body = """
锋哥，

产品持仓 Excel 报表已生成，请查收附件。

汇总数据：
- 产品数量：13 只
- 总投资成本：¥14,221,247.10
- 总持仓收益：¥-148,671.04 (-1.05%)

AI 助手
2026-03-26
"""
    attachment = Path(__file__).parent / 'data' / '产品持仓明细_20260326.xlsx'
    send_email_with_attachment(subject, body, attachment, RECEIVER_EMAIL)
