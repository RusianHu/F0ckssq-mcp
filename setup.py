#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README.md作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ssq_mcp",
    version="1.0.0",
    description="双色球数据爬虫 MCP 服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rusian Huu",
    author_email="hu_bo_cheng@qq.com",
    url="https://github.com/RusianHu/F0ckssq-mcp",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ssq_mcp": ["config.json"],
    },
    install_requires=[
        "fastmcp>=0.1.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.10.0",
        "pandas>=1.3.0",
        "tabulate>=0.8.9",
        "lxml>=4.6.3",
        "pydantic>=1.9.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
