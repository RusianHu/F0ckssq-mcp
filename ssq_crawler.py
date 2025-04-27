#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 需要安装以下依赖包： pip install requests beautifulsoup4 pandas tabulate lxml

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import argparse
from tabulate import tabulate
import datetime
import lxml.html
import io

class SSQCrawler:
    """双色球数据爬虫类"""

    def __init__(self):
        self.base_url = "https://datachart.500.com/ssq/history/newinc/history.php"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_data(self, limit=500, sort=0):
        """
        获取双色球数据

        Args:
            limit: 获取的期数
            sort: 排序方式，0为按期号降序，1为按期号升序

        Returns:
            DataFrame: 包含双色球数据的DataFrame
        """
        params = {
            "limit": limit,
            "sort": sort
        }

        try:
            # 尝试使用代理（如果需要）
            proxies = None
            # 如果需要代理，取消下面的注释并设置代理
            # proxies = {
            #     'http': 'socks5://127.0.0.1:10808',
            #     'https': 'socks5://127.0.0.1:10808'
            # }

            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                proxies=proxies,
                timeout=30
            )

            # 尝试自动检测编码
            response.encoding = response.apparent_encoding

            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                return None

            # 打印一些调试信息
            print(f"成功获取数据，编码: {response.encoding}")

            # 尝试使用直接解析方法
            try:
                # 使用更精确的正则表达式提取数据
                # 查找包含期号和球号的行
                pattern = r'<tr[^>]*><!--<td>\d+</td>--><td>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td><td[^>]*>(\d+)</td>'
                matches = re.findall(pattern, response.text, re.DOTALL)

                if matches:
                    # 创建DataFrame
                    data = []
                    for match in matches:
                        if len(match) >= 8 and len(match[0]) >= 4:  # 确保期号至少有4位数字
                            try:
                                # 提取开奖日期
                                date_pattern = r'<td>{}.*?<td>(\d{{4}}-\d{{2}}-\d{{2}})</td>'.format(match[0])
                                date_match = re.search(date_pattern, response.text)
                                date = date_match.group(1) if date_match else ""

                                row = {
                                    '期号': match[0],
                                    '红球1': int(match[1]),
                                    '红球2': int(match[2]),
                                    '红球3': int(match[3]),
                                    '红球4': int(match[4]),
                                    '红球5': int(match[5]),
                                    '红球6': int(match[6]),
                                    '蓝球': int(match[7]),
                                    '开奖日期': date
                                }
                                # 验证红球和蓝球的范围
                                valid = True
                                for i in range(1, 7):
                                    if not (1 <= row[f'红球{i}'] <= 33):
                                        valid = False
                                        break
                                if not (1 <= row['蓝球'] <= 16):
                                    valid = False

                                if valid:
                                    data.append(row)
                            except (ValueError, IndexError) as e:
                                print(f"处理行时出错: {e}")
                                continue

                    if data:
                        df = pd.DataFrame(data)
                        # 按期号降序排序
                        df = df.sort_values('期号', ascending=False).reset_index(drop=True)
                        # 只保留前limit条记录
                        if len(df) > limit:
                            df = df.iloc[:limit]
                        return df

                # 如果直接解析方法失败，尝试使用BeautifulSoup解析
                print("直接解析失败，尝试使用BeautifulSoup解析...")
                return self._parse_html(response.text)
            except Exception as e:
                print(f"直接解析失败: {e}")
                return self._parse_html(response.text)
        except Exception as e:
            print(f"获取数据时出错: {e}")
            return None

    def fetch_by_issue_range(self, start_issue, end_issue):
        """
        获取指定期号范围的双色球数据

        Args:
            start_issue: 起始期号
            end_issue: 结束期号

        Returns:
            DataFrame: 包含指定期号范围的双色球数据
        """
        # 获取足够多的数据以覆盖指定范围
        df = self.fetch_data(limit=1000, sort=1)

        if df is None:
            return None

        # 筛选期号范围
        mask = (df['期号'] >= str(start_issue)) & (df['期号'] <= str(end_issue))
        return df[mask].reset_index(drop=True)

    def fetch_by_issue(self, issue):
        """
        获取指定期号的双色球数据

        Args:
            issue: 期号

        Returns:
            DataFrame: 包含指定期号的双色球数据
        """
        # 获取足够多的数据以覆盖指定期号
        df = self.fetch_data(limit=1000, sort=1)

        if df is None:
            return None

        # 筛选期号
        return df[df['期号'] == str(issue)].reset_index(drop=True)

    def _parse_html(self, html_content):
        """
        解析HTML内容

        Args:
            html_content: HTML内容

        Returns:
            DataFrame: 解析后的数据
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # 尝试找到表格 - 网站可能使用不同的类名或ID
        table = soup.find('table', id='tablelist')

        if not table:
            print("未找到数据表格，尝试其他方式查找...")
            # 尝试找到所有表格
            tables = soup.find_all('table')
            if tables:
                # 选择最可能包含数据的表格（通常是最大的表格）
                table = max(tables, key=lambda t: len(t.find_all('tr')))
            else:
                print("网页中没有找到任何表格")
                return None

        # 获取表头行
        header_row = table.find('tr')
        if not header_row:
            print("表格中没有找到表头行")
            return None

        # 提取表头
        headers = []
        for td in header_row.find_all(['td', 'th']):
            header_text = td.get_text().strip()
            if '期号' in header_text:
                headers.append('期号')
            elif '红球号码' in header_text or '红球' in header_text:
                # 添加6个红球列
                headers.extend(['红球1', '红球2', '红球3', '红球4', '红球5', '红球6'])
            elif '蓝球' in header_text:
                headers.append('蓝球')
            elif '开奖日期' in header_text:
                headers.append('开奖日期')
            elif '奖池奖金' in header_text:
                headers.append('奖池奖金')
            elif '一等奖注数' in header_text or '一等奖' in header_text:
                headers.append('一等奖注数')
            elif '一等奖奖金' in header_text:
                headers.append('一等奖奖金')
            elif '二等奖注数' in header_text or '二等奖' in header_text:
                headers.append('二等奖注数')
            elif '二等奖奖金' in header_text:
                headers.append('二等奖奖金')
            elif '总投注额' in header_text:
                headers.append('总投注额')
            else:
                # 对于其他列，使用原始文本
                headers.append(header_text)

        # 如果没有找到足够的列名，使用默认列名
        if len(headers) < 10:
            print(f"警告：只找到 {len(headers)} 个列名，使用默认列名")
            headers = ['期号', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '开奖日期']

        # 获取数据行
        rows = []
        data_rows = table.find_all('tr')[1:]  # 跳过表头行

        for tr in data_rows:
            cells = tr.find_all(['td', 'th'])
            if len(cells) < 8:  # 至少需要期号、6个红球和1个蓝球
                continue

            row = []
            red_balls_added = 0

            for i, td in enumerate(cells):
                cell_text = td.get_text().strip()

                # 处理期号
                if i == 0 and cell_text.isdigit():
                    row.append(cell_text)  # 期号
                # 处理红球
                elif 1 <= i <= 6:
                    if cell_text.isdigit() and 1 <= int(cell_text) <= 33:
                        row.append(cell_text)
                        red_balls_added += 1
                # 处理蓝球
                elif i == 7 and cell_text.isdigit() and 1 <= int(cell_text) <= 16:
                    row.append(cell_text)  # 蓝球
                # 处理开奖日期
                elif i > 7 and re.match(r'\d{4}-\d{2}-\d{2}', cell_text):
                    row.append(cell_text)  # 开奖日期
                # 其他数据
                elif i > 7:
                    row.append(cell_text)

            # 确保红球数量正确
            if red_balls_added != 6:
                # 尝试从行中提取红球
                red_balls = []
                for td in cells:
                    for span in td.find_all('span', class_='ball_1'):
                        ball_text = span.get_text().strip()
                        if ball_text.isdigit() and 1 <= int(ball_text) <= 33:
                            red_balls.append(ball_text)

                # 如果找到了6个红球，替换之前的红球数据
                if len(red_balls) == 6:
                    row = [row[0]] + red_balls + row[red_balls_added+1:]

            if len(row) >= 8:  # 至少有期号、6个红球和1个蓝球
                rows.append(row)

        if not rows:
            print("未找到有效的数据行")

            # 尝试直接提取所有球号
            all_rows = []
            for tr in data_rows:
                issue = tr.find('td')
                if not issue:
                    continue

                issue_text = issue.get_text().strip()
                if not issue_text.isdigit():
                    continue

                # 查找所有球号
                red_spans = tr.find_all('span', class_='ball_1')
                blue_span = tr.find('span', class_='ball_2')

                if len(red_spans) == 6 and blue_span:
                    red_balls = [span.get_text().strip() for span in red_spans]
                    blue_ball = blue_span.get_text().strip()

                    # 查找开奖日期
                    date_cell = None
                    for td in tr.find_all('td'):
                        if re.match(r'\d{4}-\d{2}-\d{2}', td.get_text().strip()):
                            date_cell = td.get_text().strip()
                            break

                    row = [issue_text] + red_balls + [blue_ball]
                    if date_cell:
                        row.append(date_cell)

                    all_rows.append(row)

            if all_rows:
                rows = all_rows
                if len(headers) != len(rows[0]):
                    headers = ['期号', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球']
                    if len(rows[0]) > 8:
                        headers.append('开奖日期')

        if not rows:
            print("尝试使用lxml解析...")
            try:
                # 尝试使用lxml解析
                html_tree = lxml.html.parse(io.StringIO(html_content))
                root = html_tree.getroot()

                # 尝试找到表格
                tables = root.xpath('//table')
                if tables:
                    table_element = tables[0]  # 使用第一个表格

                    # 获取所有行
                    tr_elements = table_element.xpath('.//tr')

                    if len(tr_elements) > 1:
                        # 提取数据
                        lxml_rows = []
                        for tr in tr_elements[1:]:  # 跳过表头
                            cells = tr.xpath('.//td')
                            if len(cells) >= 8:
                                row_data = []
                                for i, cell in enumerate(cells):
                                    text = cell.text_content().strip()
                                    if i == 0 and text.isdigit():  # 期号
                                        row_data.append(text)
                                    elif 1 <= i <= 6:  # 红球
                                        if text.isdigit() and 1 <= int(text) <= 33:
                                            row_data.append(text)
                                    elif i == 7 and text.isdigit() and 1 <= int(text) <= 16:  # 蓝球
                                        row_data.append(text)
                                    elif i > 7:  # 其他数据
                                        row_data.append(text)

                                if len(row_data) >= 8:
                                    lxml_rows.append(row_data)

                        if lxml_rows:
                            rows = lxml_rows
                            headers = ['期号', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球']
                            if len(rows[0]) > 8:
                                headers.append('开奖日期')
            except Exception as e:
                print(f"lxml解析失败: {e}")

        if not rows:
            print("尝试所有方法后仍未找到数据")
            return None

        # 创建DataFrame
        df = pd.DataFrame(rows)

        # 检查是否有空行或无效行（第一行可能是表头）
        if len(df) > 0 and df.iloc[0][0] == '1' and not df.iloc[0][1].isdigit():
            df = df.iloc[1:].reset_index(drop=True)

        # 确保至少有8列（期号、6个红球、1个蓝球）
        if len(df.columns) < 8:
            print(f"警告：列数不足 ({len(df.columns)})")
            return None

        # 重新设置列名，不依赖于之前解析的headers
        num_cols = len(df.columns)
        new_headers = []

        # 添加基本列名
        if num_cols >= 1:
            new_headers.append('期号')

        # 添加红球列名
        for i in range(1, 7):
            if len(new_headers) < num_cols:
                new_headers.append(f'红球{i}')

        # 添加蓝球列名
        if len(new_headers) < num_cols:
            new_headers.append('蓝球')

        # 添加开奖日期列名
        if len(new_headers) < num_cols:
            new_headers.append('开奖日期')

        # 添加其他列名
        while len(new_headers) < num_cols:
            new_headers.append(f'列{len(new_headers)+1}')

        # 设置列名
        df.columns = new_headers

        # 检查数据有效性
        if len(df) > 0:
            # 删除无效行
            valid_rows = []
            for i, row in df.iterrows():
                # 检查期号是否是数字
                if not str(row['期号']).isdigit():
                    continue

                # 检查是否有足够的红球数据
                red_balls_valid = True
                for j in range(1, 7):
                    col_name = f'红球{j}'
                    if col_name in df.columns and pd.isna(row[col_name]):
                        red_balls_valid = False
                        break

                if not red_balls_valid:
                    continue

                valid_rows.append(i)

            # 只保留有效行
            if valid_rows:
                df = df.iloc[valid_rows].reset_index(drop=True)
            elif len(df) > 1:  # 如果没有有效行但有多行，可能第一行是表头
                df = df.iloc[1:].reset_index(drop=True)

        # 确保红球和蓝球列是数字
        for col in df.columns:
            if '红球' in col or col == '蓝球':
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 处理红球和蓝球列
        for i in range(1, 7):
            col_name = f'红球{i}'
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')

        if '蓝球' in df.columns:
            df['蓝球'] = pd.to_numeric(df['蓝球'], errors='coerce')

        return df

    def format_to_markdown(self, df):
        """
        将DataFrame格式化为Markdown表格

        Args:
            df: DataFrame数据

        Returns:
            str: Markdown格式的表格
        """
        if df is None or df.empty:
            return "没有找到数据"

        # 选择要显示的列
        display_columns = ['期号']
        # 添加红球列
        for i in range(1, 7):
            col_name = f'红球{i}'
            if col_name in df.columns:
                display_columns.append(col_name)

        # 添加蓝球列
        if '蓝球' in df.columns:
            display_columns.append('蓝球')

        # 添加开奖日期列（如果存在）
        if '开奖日期' in df.columns:
            display_columns.append('开奖日期')

        # 确保所有选择的列都在DataFrame中
        display_columns = [col for col in display_columns if col in df.columns]

        if not display_columns:
            return "没有找到有效的列"

        display_df = df[display_columns].copy()

        # 删除包含NaN的行
        display_df = display_df.dropna(how='all').reset_index(drop=True)

        # 格式化为Markdown
        markdown_table = tabulate(display_df, headers='keys', tablefmt='pipe', showindex=False)
        return markdown_table

    def analyze_frequency(self, df, top_n=10):
        """
        分析号码出现频率

        Args:
            df: DataFrame数据
            top_n: 显示前N个高频号码

        Returns:
            dict: 包含红球和蓝球频率分析的字典
        """
        if df is None or df.empty:
            return None

        # 分析红球频率
        red_balls_list = []
        for i in range(1, 7):
            col_name = f'红球{i}'
            if col_name in df.columns:
                red_balls_list.append(df[col_name])

        # 使用concat合并非空列表
        if red_balls_list:
            red_balls = pd.concat(red_balls_list)
        else:
            red_balls = pd.Series()

        red_freq = red_balls.value_counts().head(top_n)

        # 分析蓝球频率
        blue_freq = df['蓝球'].value_counts().head(top_n)

        return {
            'red_freq': red_freq,
            'blue_freq': blue_freq
        }

    def format_frequency_to_markdown(self, freq_data):
        """
        将频率分析结果格式化为Markdown

        Args:
            freq_data: 频率分析结果

        Returns:
            str: Markdown格式的频率分析
        """
        if freq_data is None:
            return "没有数据可供分析"

        red_freq_df = pd.DataFrame({'红球号码': freq_data['red_freq'].index, '出现次数': freq_data['red_freq'].values})
        blue_freq_df = pd.DataFrame({'蓝球号码': freq_data['blue_freq'].index, '出现次数': freq_data['blue_freq'].values})

        red_markdown = tabulate(red_freq_df, headers='keys', tablefmt='pipe', showindex=False)
        blue_markdown = tabulate(blue_freq_df, headers='keys', tablefmt='pipe', showindex=False)

        return f"## 红球出现频率（Top {len(red_freq_df)}）\n\n{red_markdown}\n\n## 蓝球出现频率（Top {len(blue_freq_df)}）\n\n{blue_markdown}"

    def analyze_missing_periods(self, df, top_n=10):
        """
        分析号码遗漏期数

        Args:
            df: DataFrame数据
            top_n: 显示前N个长期遗漏的号码

        Returns:
            dict: 包含红球和蓝球遗漏期数分析的字典
        """
        if df is None or df.empty:
            return None

        # 确保期号是按照降序排列的
        df = df.sort_values('期号', ascending=False).reset_index(drop=True)

        # 所有可能的红球和蓝球号码
        all_red_balls = list(range(1, 34))
        all_blue_balls = list(range(1, 17))

        # 获取最新一期的期号
        latest_issue = df.iloc[0]['期号']

        # 分析红球遗漏
        red_missing = {}
        for num in all_red_balls:
            for i, row in df.iterrows():
                if num in [row[f'红球{j}'] for j in range(1, 7)]:
                    red_missing[num] = i
                    break
            else:
                red_missing[num] = len(df)  # 如果所有期都没出现

        # 分析蓝球遗漏
        blue_missing = {}
        for num in all_blue_balls:
            for i, row in df.iterrows():
                if num == row['蓝球']:
                    blue_missing[num] = i
                    break
            else:
                blue_missing[num] = len(df)  # 如果所有期都没出现

        # 转换为Series并排序
        red_missing_series = pd.Series(red_missing).sort_values(ascending=False).head(top_n)
        blue_missing_series = pd.Series(blue_missing).sort_values(ascending=False).head(top_n)

        return {
            'red_missing': red_missing_series,
            'blue_missing': blue_missing_series,
            'latest_issue': latest_issue
        }

    def format_missing_to_markdown(self, missing_data):
        """
        将遗漏期数分析结果格式化为Markdown

        Args:
            missing_data: 遗漏期数分析结果

        Returns:
            str: Markdown格式的遗漏期数分析
        """
        if missing_data is None:
            return "没有数据可供分析"

        latest_issue = missing_data['latest_issue']

        red_missing_df = pd.DataFrame({'红球号码': missing_data['red_missing'].index,
                                      '遗漏期数': missing_data['red_missing'].values})
        blue_missing_df = pd.DataFrame({'蓝球号码': missing_data['blue_missing'].index,
                                       '遗漏期数': missing_data['blue_missing'].values})

        red_markdown = tabulate(red_missing_df, headers='keys', tablefmt='pipe', showindex=False)
        blue_markdown = tabulate(blue_missing_df, headers='keys', tablefmt='pipe', showindex=False)

        return f"## 红球遗漏期数分析（截至{latest_issue}期）\n\n{red_markdown}\n\n## 蓝球遗漏期数分析（截至{latest_issue}期）\n\n{blue_markdown}"


def main():
    parser = argparse.ArgumentParser(description='双色球数据爬虫')
    parser.add_argument('--recent', type=int, help='获取最近n期的数据')
    parser.add_argument('--range', type=str, help='获取指定期号范围的数据，格式为"起始期号-结束期号"')
    parser.add_argument('--issue', type=str, help='获取指定期号的数据')
    parser.add_argument('--analyze', action='store_true', help='分析号码频率和遗漏期数')

    args = parser.parse_args()

    crawler = SSQCrawler()

    if args.recent:
        print(f"\n## 最近{args.recent}期双色球开奖结果\n")
        df = crawler.fetch_data(limit=args.recent)
        print(crawler.format_to_markdown(df))

        if args.analyze:
            freq_data = crawler.analyze_frequency(df)
            print("\n" + crawler.format_frequency_to_markdown(freq_data))

            missing_data = crawler.analyze_missing_periods(df)
            print("\n" + crawler.format_missing_to_markdown(missing_data))

    elif args.range:
        match = re.match(r'(\d+)-(\d+)', args.range)
        if match:
            start_issue, end_issue = match.groups()
            print(f"\n## 第{start_issue}期至第{end_issue}期双色球开奖结果\n")
            df = crawler.fetch_by_issue_range(start_issue, end_issue)
            print(crawler.format_to_markdown(df))

            if args.analyze:
                freq_data = crawler.analyze_frequency(df)
                print("\n" + crawler.format_frequency_to_markdown(freq_data))

                missing_data = crawler.analyze_missing_periods(df)
                print("\n" + crawler.format_missing_to_markdown(missing_data))
        else:
            print("期号范围格式错误，正确格式为'起始期号-结束期号'")

    elif args.issue:
        print(f"\n## 第{args.issue}期双色球开奖结果\n")
        df = crawler.fetch_by_issue(args.issue)
        print(crawler.format_to_markdown(df))

    else:
        # 默认显示最近10期
        print("\n## 最近10期双色球开奖结果\n")
        df = crawler.fetch_data(limit=10)
        print(crawler.format_to_markdown(df))

        # 默认进行分析
        freq_data = crawler.analyze_frequency(df)
        print("\n" + crawler.format_frequency_to_markdown(freq_data))

        missing_data = crawler.analyze_missing_periods(df)
        print("\n" + crawler.format_missing_to_markdown(missing_data))


if __name__ == "__main__":
    main()
