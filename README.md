# 双色球数据爬虫 MCP 服务

双色球数据爬虫 MCP，提供双色球历史数据查询和分析功能。

## 功能特点

- 获取最近N期的双色球数据
- 获取指定期号范围的双色球数据
- 获取指定期号的双色球数据
- 分析号码出现频率
- 分析号码遗漏期数
- 支持代理配置

## 安装方法

### 直接从GitHub安装

```bash
pip install git+https://github.com/RusianHu/F0ckssq-mcp.git
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/RusianHu/F0ckssq-mcp.git
cd F0ckssq-mcp

# 安装依赖
pip install -e .
```

## 使用方法

### 作为 MCP 服务使用

在 `mcp_settings.json` 中添加以下配置：

```json
{
  "F0ckssq-mcp": {
    "command": "python",
    "args": [
      "-m",
      "ssq_mcp"
    ],
    "alwaysAllow": [
      "get_recent_data",
      "get_data_by_issue_range",
      "get_data_by_issue",
      "analyze_frequency",
      "analyze_missing_periods",
      "get_proxy_status"
    ],
    "disabled": false
  }
}
```

### 代理配置

如果需要使用代理，可以修改 `ssq_mcp/config.json` 文件：

```json
{
  "proxy": "socks5://127.0.0.1:10808"
}
```

## MCP 工具 说明

### get_recent_data

获取最近N期的双色球数据。

参数：
- `limit`: 获取的期数，默认为10

返回：
- 双色球数据列表，包含期号、红球、蓝球和开奖日期

### get_data_by_issue_range

获取指定期号范围的双色球数据。

参数：
- `start_issue`: 起始期号
- `end_issue`: 结束期号

返回：
- 双色球数据列表，包含期号、红球、蓝球和开奖日期

### get_data_by_issue

获取指定期号的双色球数据。

参数：
- `issue`: 期号

返回：
- 双色球数据列表，包含期号、红球、蓝球和开奖日期

### analyze_frequency

分析双色球号码出现频率。

参数：
- `limit`: 分析的期数，默认为100

返回：
- 频率分析结果，包含红球和蓝球的出现频率

### analyze_missing_periods

分析双色球号码遗漏期数。

参数：
- `limit`: 分析的期数，默认为100

返回：
- 遗漏期数分析结果，包含红球和蓝球的遗漏期数

### get_proxy_status

获取当前代理配置状态。

返回：
- 代理配置信息，包含代理地址和是否启用

## 系统要求

- Python 3.10 或更高版本
- 依赖包：见 `setup.py` 中的 `install_requires` 列表

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
