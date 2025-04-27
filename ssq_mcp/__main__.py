#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
双色球数据爬虫 MCP 服务入口
"""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
