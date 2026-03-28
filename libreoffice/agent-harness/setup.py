#!/usr/bin/env python3
"""
LibreOffice CLI - Installation Script

Install with: pip3 install -e .
Or: python3 setup.py install
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="cli-anything-libreoffice",
    version="1.0.0",
    author="OpenClaw Workspace",
    author_email="admin@openclaw.workspace",
    description="LibreOffice CLI for Investment Report Generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/workspace",
    
    # Main CLI script
    py_modules=["cli_lo"],
    
    # Entry points
    entry_points={
        "console_scripts": [
            "cli-anything-libreoffice=cli_lo:cli",
            "clo=cli_lo:cli",  # Short alias
        ],
    },
    
    # Dependencies
    install_requires=[
        "click>=8.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
        "odf": [
            "odfpy>=1.4.0",  # For proper ODT/ODS generation
        ],
    },
    
    # Python version
    python_requires=">=3.8",
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    
    # Keywords
    keywords="libreoffice cli investment reports pdf generation automation",
    
    # Package data
    package_data={
        "": ["README.md", "TEST.md"],
    },
    
    # Include additional files
    include_package_data=True,
)
