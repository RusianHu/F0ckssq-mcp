#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
双色球数据爬虫 MCP 服务
"""

import asyncio
import json
import os
from typing import Optional, Dict, List, Any, Union
import pandas as pd
from pydantic import BaseModel, Field

from fastmcp import FastMCP, Context
from .crawler import AsyncSSQCrawler


# 定义数据模型
class SSQData(BaseModel):
    """双色球数据模型"""
    issue: str = Field(..., description="期号")
    red_balls: List[int] = Field(..., description="红球号码，6个1-33之间的数字")
    blue_ball: int = Field(..., description="蓝球号码，1个1-16之间的数字")
    draw_date: Optional[str] = Field(None, description="开奖日期")


class SSQDataList(BaseModel):
    """双色球数据列表模型"""
    data: List[SSQData] = Field(..., description="双色球数据列表")
    total: int = Field(..., description="数据总数")
    markdown: str = Field(..., description="Markdown格式的数据表格")


class FrequencyAnalysis(BaseModel):
    """频率分析结果模型"""
    red_freq: Dict[int, int] = Field(..., description="红球出现频率")
    blue_freq: Dict[int, int] = Field(..., description="蓝球出现频率")
    markdown: str = Field(..., description="Markdown格式的分析结果")


class MissingAnalysis(BaseModel):
    """遗漏期数分析结果模型"""
    red_missing: Dict[int, int] = Field(..., description="红球遗漏期数")
    blue_missing: Dict[int, int] = Field(..., description="蓝球遗漏期数")
    latest_issue: Optional[str] = Field(None, description="最新一期期号")
    markdown: str = Field(..., description="Markdown格式的分析结果")


# 创建 MCP 服务
mcp = FastMCP(name="双色球数据服务")


# 加载配置
def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"proxy": None}


# 创建爬虫实例
config = load_config()
crawler = AsyncSSQCrawler(proxy=config.get("proxy"))


@mcp.tool()
async def get_recent_data(limit: int = 10, ctx: Context = None) -> SSQDataList:
    """
    获取最近N期的双色球数据
    
    Args:
        limit: 获取的期数，默认为10
        ctx: MCP上下文
    
    Returns:
        SSQDataList: 双色球数据列表
    """
    if ctx:
        await ctx.info(f"正在获取最近{limit}期双色球数据...")
    
    df = await crawler.fetch_data(limit=limit)
    
    if df is None or df.empty:
        return SSQDataList(data=[], total=0, markdown="没有找到数据")
    
    # 转换为SSQData列表
    data_list = []
    for _, row in df.iterrows():
        data = SSQData(
            issue=row['期号'],
            red_balls=[
                int(row['红球1']), int(row['红球2']), int(row['红球3']),
                int(row['红球4']), int(row['红球5']), int(row['红球6'])
            ],
            blue_ball=int(row['蓝球']),
            draw_date=row['开奖日期'] if '开奖日期' in row else None
        )
        data_list.append(data)
    
    # 生成Markdown表格
    markdown = crawler.format_to_markdown(df)
    
    return SSQDataList(
        data=data_list,
        total=len(data_list),
        markdown=markdown
    )


@mcp.tool()
async def get_data_by_issue_range(start_issue: str, end_issue: str, ctx: Context = None) -> SSQDataList:
    """
    获取指定期号范围的双色球数据
    
    Args:
        start_issue: 起始期号
        end_issue: 结束期号
        ctx: MCP上下文
    
    Returns:
        SSQDataList: 双色球数据列表
    """
    if ctx:
        await ctx.info(f"正在获取第{start_issue}期至第{end_issue}期双色球数据...")
    
    df = await crawler.fetch_by_issue_range(start_issue, end_issue)
    
    if df is None or df.empty:
        return SSQDataList(data=[], total=0, markdown="没有找到数据")
    
    # 转换为SSQData列表
    data_list = []
    for _, row in df.iterrows():
        data = SSQData(
            issue=row['期号'],
            red_balls=[
                int(row['红球1']), int(row['红球2']), int(row['红球3']),
                int(row['红球4']), int(row['红球5']), int(row['红球6'])
            ],
            blue_ball=int(row['蓝球']),
            draw_date=row['开奖日期'] if '开奖日期' in row else None
        )
        data_list.append(data)
    
    # 生成Markdown表格
    markdown = crawler.format_to_markdown(df)
    
    return SSQDataList(
        data=data_list,
        total=len(data_list),
        markdown=markdown
    )


@mcp.tool()
async def get_data_by_issue(issue: str, ctx: Context = None) -> SSQDataList:
    """
    获取指定期号的双色球数据
    
    Args:
        issue: 期号
        ctx: MCP上下文
    
    Returns:
        SSQDataList: 双色球数据列表
    """
    if ctx:
        await ctx.info(f"正在获取第{issue}期双色球数据...")
    
    df = await crawler.fetch_by_issue(issue)
    
    if df is None or df.empty:
        return SSQDataList(data=[], total=0, markdown="没有找到数据")
    
    # 转换为SSQData列表
    data_list = []
    for _, row in df.iterrows():
        data = SSQData(
            issue=row['期号'],
            red_balls=[
                int(row['红球1']), int(row['红球2']), int(row['红球3']),
                int(row['红球4']), int(row['红球5']), int(row['红球6'])
            ],
            blue_ball=int(row['蓝球']),
            draw_date=row['开奖日期'] if '开奖日期' in row else None
        )
        data_list.append(data)
    
    # 生成Markdown表格
    markdown = crawler.format_to_markdown(df)
    
    return SSQDataList(
        data=data_list,
        total=len(data_list),
        markdown=markdown
    )


@mcp.tool()
async def analyze_frequency(limit: int = 100, ctx: Context = None) -> FrequencyAnalysis:
    """
    分析双色球号码出现频率
    
    Args:
        limit: 分析的期数，默认为100
        ctx: MCP上下文
    
    Returns:
        FrequencyAnalysis: 频率分析结果
    """
    if ctx:
        await ctx.info(f"正在分析最近{limit}期双色球号码出现频率...")
    
    df = await crawler.fetch_data(limit=limit)
    
    if df is None or df.empty:
        return FrequencyAnalysis(
            red_freq={},
            blue_freq={},
            markdown="没有找到数据"
        )
    
    # 分析频率
    freq_data = await crawler.analyze_frequency(df)
    
    if freq_data is None:
        return FrequencyAnalysis(
            red_freq={},
            blue_freq={},
            markdown="分析失败"
        )
    
    # 转换为字典
    red_freq_dict = {int(k): int(v) for k, v in freq_data['red_freq'].items()}
    blue_freq_dict = {int(k): int(v) for k, v in freq_data['blue_freq'].items()}
    
    # 生成Markdown表格
    markdown = crawler.format_frequency_to_markdown(freq_data)
    
    return FrequencyAnalysis(
        red_freq=red_freq_dict,
        blue_freq=blue_freq_dict,
        markdown=markdown
    )


@mcp.tool()
async def analyze_missing_periods(limit: int = 100, ctx: Context = None) -> MissingAnalysis:
    """
    分析双色球号码遗漏期数
    
    Args:
        limit: 分析的期数，默认为100
        ctx: MCP上下文
    
    Returns:
        MissingAnalysis: 遗漏期数分析结果
    """
    if ctx:
        await ctx.info(f"正在分析最近{limit}期双色球号码遗漏期数...")
    
    df = await crawler.fetch_data(limit=limit)
    
    if df is None or df.empty:
        return MissingAnalysis(
            red_missing={},
            blue_missing={},
            latest_issue=None,
            markdown="没有找到数据"
        )
    
    # 分析遗漏期数
    missing_data = await crawler.analyze_missing_periods(df)
    
    if missing_data is None:
        return MissingAnalysis(
            red_missing={},
            blue_missing={},
            latest_issue=None,
            markdown="分析失败"
        )
    
    # 转换为字典
    red_missing_dict = {int(k): int(v) for k, v in missing_data['red_missing'].items()}
    blue_missing_dict = {int(k): int(v) for k, v in missing_data['blue_missing'].items()}
    
    # 生成Markdown表格
    markdown = crawler.format_missing_to_markdown(missing_data)
    
    return MissingAnalysis(
        red_missing=red_missing_dict,
        blue_missing=blue_missing_dict,
        latest_issue=missing_data.get('latest_issue'),
        markdown=markdown
    )


@mcp.tool()
async def get_proxy_status(ctx: Context = None) -> Dict[str, Any]:
    """
    获取当前代理配置状态
    
    Args:
        ctx: MCP上下文
    
    Returns:
        Dict: 代理配置信息
    """
    config = load_config()
    return {
        "proxy": config.get("proxy"),
        "enabled": config.get("proxy") is not None
    }


if __name__ == "__main__":
    mcp.run()
