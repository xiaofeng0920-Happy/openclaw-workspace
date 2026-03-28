#!/usr/bin/env python3
"""
Draw.io CLI - Setup Script

Installation:
    pip install -e .

Usage:
    cli-anything-drawio [OPTIONS] COMMAND [ARGS]...
"""

from setuptools import setup, find_namespace_packages

setup(
    name='cli-anything-drawio',
    version='1.0.0',
    description='Draw.io CLI for investment analysis diagram creation',
    long_description=open('cli_anything/drawio/README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='OpenClaw Agent',
    author_email='agent@openclaw.local',
    url='https://github.com/openclaw/workspace/drawio',
    license='MIT',
    
    # Namespace package
    packages=find_namespace_packages(include=['cli_anything.*']),
    
    # Command line entry point
    entry_points={
        'console_scripts': [
            'cli-anything-drawio=cli_anything.drawio.drawio_cli:main',
        ],
    },
    
    # Dependencies
    install_requires=[
        'click>=8.0.0',
    ],
    
    # Development dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
    
    # Python version
    python_requires='>=3.8',
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Multimedia :: Graphics :: Editors',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
    
    # Include package data
    package_data={
        'cli_anything.drawio': [
            'README.md',
            'py.typed',
        ],
    },
)
