#!/usr/bin/env python3
"""
Setup script for Space Haven Save Editor
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README_PYTHON.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text()

setup(
    name="space-haven-editor",
    version="2.0.0",
    description="Cross-platform save editor for Space Haven",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Original by Moragar, Python port by contributors",
    url="https://github.com/JohnCrafton/Space-Haven-Save-Game-Editor",
    license="MIT",
    py_modules=["space_haven_editor", "models"],
    install_requires=[
        "PyQt6>=6.4.0",
    ],
    entry_points={
        "console_scripts": [
            "space-haven-editor=space_haven_editor:main",
        ],
        "gui_scripts": [
            "space-haven-editor-gui=space_haven_editor:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
)
