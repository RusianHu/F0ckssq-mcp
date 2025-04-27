#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from fastmcp import Client

async def main():
    """测试MCP客户端功能"""
    print("开始测试双色球数据爬虫MCP服务...")

    # 创建MCP客户端
    client = Client("http://localhost:8000")

    async with client:
        # 测试获取最近数据
        print("\n测试获取最近数据功能...")
        try:
            result = await client.call_tool("ssq-mcp", "get_recent_data", {"limit": 5})
            print("成功获取最近数据:")
            print(result["markdown"])
            test1 = True
        except Exception as e:
            print(f"获取最近数据失败: {e}")
            test1 = False

        # 测试获取指定期号范围数据
        print("\n测试获取指定期号范围数据功能...")
        try:
            result = await client.call_tool("ssq-mcp", "get_data_by_issue_range", {"start_issue": "2023001", "end_issue": "2023010"})
            print("成功获取指定期号范围数据:")
            print(result["markdown"])
            test2 = True
        except Exception as e:
            print(f"获取指定期号范围数据失败: {e}")
            test2 = False

        # 测试获取指定期号数据
        print("\n测试获取指定期号数据功能...")
        try:
            result = await client.call_tool("ssq-mcp", "get_data_by_issue", {"issue": "2023001"})
            print("成功获取指定期号数据:")
            print(result["markdown"])
            test3 = True
        except Exception as e:
            print(f"获取指定期号数据失败: {e}")
            test3 = False

        # 测试分析号码出现频率
        print("\n测试分析号码出现频率功能...")
        try:
            result = await client.call_tool("ssq-mcp", "analyze_frequency", {"limit": 50})
            print("成功分析号码出现频率:")
            print(result["markdown"])
            test4 = True
        except Exception as e:
            print(f"分析号码出现频率失败: {e}")
            test4 = False

        # 测试分析号码遗漏期数
        print("\n测试分析号码遗漏期数功能...")
        try:
            result = await client.call_tool("ssq-mcp", "analyze_missing_periods", {"limit": 50})
            print("成功分析号码遗漏期数:")
            print(result["markdown"])
            test5 = True
        except Exception as e:
            print(f"分析号码遗漏期数失败: {e}")
            test5 = False

        # 测试获取代理状态
        print("\n测试获取代理状态功能...")
        try:
            result = await client.call_tool("ssq-mcp", "get_proxy_status")
            print("成功获取代理状态:")
            print(result)
            test6 = True
        except Exception as e:
            print(f"获取代理状态失败: {e}")
            test6 = False

    # 输出测试结果
    print("\n测试结果汇总:")
    print(f"获取最近数据: {'通过' if test1 else '失败'}")
    print(f"获取指定期号范围数据: {'通过' if test2 else '失败'}")
    print(f"获取指定期号数据: {'通过' if test3 else '失败'}")
    print(f"分析号码出现频率: {'通过' if test4 else '失败'}")
    print(f"分析号码遗漏期数: {'通过' if test5 else '失败'}")
    print(f"获取代理状态: {'通过' if test6 else '失败'}")

    if all([test1, test2, test3, test4, test5, test6]):
        print("\n所有测试通过！")
    else:
        print("\n部分测试失败！")

if __name__ == "__main__":
    asyncio.run(main())
