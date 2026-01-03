#!/usr/bin/env python3
"""
Setup script for yt-studio visualization tool.

Install with:
    pip install -e .

This installs:
    - plot_quokka: Python library for QUOKKA data visualization
    - yt-studio: Command-line tool to start the web interface
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for the long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="yt-studio",
    version="2.0.0",
    author="QUOKKA Team",
    description="A visualization tool for QUOKKA simulation data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chongchonghe/yt-studio",
    license="MIT",
    
    # Packages to include
    packages=find_packages(include=["plot_quokka", "plot_quokka.*", "yt_studio", "yt_studio.*", "backend"]),
    
    # Include backend and frontend as package data
    package_data={
        "": [
            "backend/*.py",
            "frontend/**/*",
        ],
    },
    
    # Include non-Python files from the project root
    data_files=[
        ("yt_studio_data", [
            "backend/main.py",
        ]),
    ],
    
    # Include everything in MANIFEST.in
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.9",
    
    # Dependencies
    install_requires=[
        "yt>=4.0.0",
        "unyt>=2.9.0",
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "PyYAML>=5.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "pydantic>=1.8.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    
    # Entry points for console scripts
    entry_points={
        "console_scripts": [
            "yt-studio=yt_studio.cli:main",
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    
    # Keywords for search
    keywords="astronomy visualization simulation quokka amr",
)
