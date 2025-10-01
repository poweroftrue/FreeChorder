#!/usr/bin/env python3
"""
Setup script for FreeChorder
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="freechorder",
    version="0.1.0",
    author="FreeChorder Team",
    description="Software CharaChorder for macOS using Karabiner-Elements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/freechorder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0",
        "pyyaml>=6.0",
        "pynput>=1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "freechorder=freechorder.cli.main:cli",
        ],
    },
)
