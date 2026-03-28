#!/usr/bin/env python3
"""
ComfyUI CLI 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-comfyui",
    version="1.0.0",
    author="OpenClaw",
    description="ComfyUI CLI - AI 生成投资可视化图表",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/comfyui-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial Advisors",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "Pillow>=9.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-comfyui=src.cli_comfyui:cli",
            "comfyui-cli=src.cli_comfyui:cli",  # 简写
        ],
    },
)
