#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from ssq_mcp.crawler import AsyncSSQCrawler

async def test_get_recent_data():
    """测试获取最近数据功能"""
    print("测试获取最近数据功能...")
    crawler = AsyncSSQCrawler()
    df = await crawler.fetch_data(limit=5)
    if df is not None and not df.empty:
        print("成功获取最近数据:")
        print(crawler.format_to_markdown(df))
        return True
    else:
        print("获取最近数据失败")
        return False

async def test_get_data_by_issue_range():
    """测试获取指定期号范围数据功能"""
    print("\n测试获取指定期号范围数据功能...")
    crawler = AsyncSSQCrawler()
    # 获取2023001-2023010期的数据
    df = await crawler.fetch_by_issue_range("2023001", "2023010")
    if df is not None and not df.empty:
        print("成功获取指定期号范围数据:")
        print(crawler.format_to_markdown(df))
        return True
    else:
        print("获取指定期号范围数据失败")
        return False

async def test_get_data_by_issue():
    """测试获取指定期号数据功能"""
    print("\n测试获取指定期号数据功能...")
    crawler = AsyncSSQCrawler()
    # 获取2023001期的数据
    df = await crawler.fetch_by_issue("2023001")
    if df is not None and not df.empty:
        print("成功获取指定期号数据:")
        print(crawler.format_to_markdown(df))
        return True
    else:
        print("获取指定期号数据失败")
        return False

async def test_analyze_frequency():
    """测试分析号码出现频率功能"""
    print("\n测试分析号码出现频率功能...")
    crawler = AsyncSSQCrawler()
    df = await crawler.fetch_data(limit=50)
    if df is not None and not df.empty:
        freq_data = await crawler.analyze_frequency(df)
        if freq_data is not None:
            print("成功分析号码出现频率:")
            print(crawler.format_frequency_to_markdown(freq_data))
            return True
    print("分析号码出现频率失败")
    return False

async def test_analyze_missing_periods():
    """测试分析号码遗漏期数功能"""
    print("\n测试分析号码遗漏期数功能...")
    crawler = AsyncSSQCrawler()
    df = await crawler.fetch_data(limit=50)
    if df is not None and not df.empty:
        missing_data = await crawler.analyze_missing_periods(df)
        if missing_data is not None:
            print("成功分析号码遗漏期数:")
            print(crawler.format_missing_to_markdown(missing_data))
            return True
    print("分析号码遗漏期数失败")
    return False

async def main():
    """主函数"""
    print("开始测试双色球数据爬虫功能...")
    
    # 测试获取最近数据
    test1 = await test_get_recent_data()
    
    # 测试获取指定期号范围数据
    test2 = await test_get_data_by_issue_range()
    
    # 测试获取指定期号数据
    test3 = await test_get_data_by_issue()
    
    # 测试分析号码出现频率
    test4 = await test_analyze_frequency()
    
    # 测试分析号码遗漏期数
    test5 = await test_analyze_missing_periods()
    
    # 输出测试结果
    print("\n测试结果汇总:")
    print(f"获取最近数据: {'通过' if test1 else '失败'}")
    print(f"获取指定期号范围数据: {'通过' if test2 else '失败'}")
    print(f"获取指定期号数据: {'通过' if test3 else '失败'}")
    print(f"分析号码出现频率: {'通过' if test4 else '失败'}")
    print(f"分析号码遗漏期数: {'通过' if test5 else '失败'}")
    
    if all([test1, test2, test3, test4, test5]):
        print("\n所有测试通过！")
    else:
        print("\n部分测试失败！")

if __name__ == "__main__":
    asyncio.run(main())
