#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
富途 OpenD 配置
"""

import os
import configparser
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    'host': '127.0.0.1',
    'port': 11112,
    'password': '',
    'password_md5': '',
}

def load_futu_config():
    """从配置文件加载富途配置"""
    config = DEFAULT_CONFIG.copy()
    
    # 尝试读取 ~/.futu/futu_config.ini
    config_file = Path.home() / '.futu' / 'futu_config.ini'
    if config_file.exists():
        try:
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'client' in parser:
                config['host'] = parser.get('client', 'host', fallback='127.0.0.1')
                config['port'] = parser.getint('client', 'port', fallback=11111)
                config['password'] = parser.get('client', 'password', fallback='')
                config['password_md5'] = parser.get('client', 'password_md5', fallback='')
        except Exception as e:
            print(f"读取配置文件失败：{e}")
    
    return config

# 加载配置
FUTU_CONFIG = load_futu_config()

# 账户信息（从 OpenD 获取后可自动填充）
ACCOUNTS = {}

def get_futu_config():
    """获取富途配置"""
    return FUTU_CONFIG
