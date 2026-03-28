#!/usr/bin/env python3
"""
Setup script for CLI-Anything GIMP
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-gimp",
    version="1.0.0",
    author="OpenClaw Agent",
    description="CLI-Anything harness for GIMP - Batch image processing for investment charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-gimp=cli_anything_gimp.cli:main",
            "gimp-cli=cli_anything_gimp.cli:main",  # Alias
        ],
    },
)
