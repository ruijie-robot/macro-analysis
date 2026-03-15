"""
阶段4：报告生成
生成完整的宏观分析报告
"""
import pandas as pd
import os
from datetime import datetime

def generate_report():
    """生成宏观分析报告"""
    output_dir = os.path.expanduser('~/.openclaw/workspace/temp/macro')

    # 检查前置数据
    required_files = ['futures_ranked.csv', 'stock_impact.csv']
    for f in required_files:
        path = f'{output_dir}/{f}'
        if not os.path.exists(path):
            print(f"错误：找不到数据文件 {path}")
            print("请先执行前置阶段")
            return None

    # 读取数据
    df_ranked = pd.read_csv(f'{output_dir}/futures_ranked.csv')
    df_impact = pd.read_csv(f'{output_dir}/stock_impact.csv')

    # 分离涨跌数据
    top_gainers = df_ranked[df_ranked['category'] == '涨幅前10']
    top_losers = df_ranked[df_ranked['category'] == '跌幅前10']

    # 分离利好利空
    bullish = df_impact[df_impact['impact_type'] == '利好']
    bearish = df_impact[df_impact['impact_type'] == '利空']

    # 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    report = f"""# 宏观市场分析报告

**生成时间**：{timestamp}

---

## 一、大宗商品期货概览

### 涨幅前10

| 品种代码 | 名称 | 涨跌幅(%) |
|----------|------|-----------|
"""

    for _, row in top_gainers.iterrows():
        report += f"| {row['ts_code']} | {row['name']} | {row['pct_chg']:.2f} |\n"

    report += """
### 跌幅前10

| 品种代码 | 名称 | 涨跌幅(%) |
|----------|------|-----------|
"""

    for _, row in top_losers.iterrows():
        report += f"| {row['ts_code']} | {row['name']} | {row['pct_chg']:.2f} |\n"

    report += """
---

## 二、A股影响分析

### 利好行业

"""

    if not bullish.empty:
        report += "| 大宗商品 | 关联行业 | 涨跌幅(%) |\n"
        report += "|----------|----------|----------|\n"
        for _, row in bullish.iterrows():
            report += f"| {row['commodity']} | {row['industry']} | +{row['pct_chg']:.2f} |\n"
    else:
        report += "无明显利好行业\n"

    report += """
### 利空行业

"""

    if not bearish.empty:
        report += "| 大宗商品 | 关联行业 | 涨跌幅(%) |\n"
        report += "|----------|----------|----------|\n"
        for _, row in bearish.iterrows():
            report += f"| {row['commodity']} | {row['industry']} | {row['pct_chg']:.2f} |\n"
    else:
        report += "无明显利空行业\n"

    report += """
---

## 三、投资建议

基于以上分析：

"""

    if not bullish.empty:
        industries = bullish['industry'].unique()
        report += f"- **关注方向**：{', '.join(industries)} 等板块可能受益于大宗商品价格上涨\n"

    if not bearish.empty:
        industries = bearish['industry'].unique()
        report += f"- **规避方向**：{', '.join(industries)} 等板块可能受到大宗商品价格下跌影响\n"

    report += """
---

*本报告仅供参考，不构成投资建议*
"""

    # 保存报告
    output_path = f'{output_dir}/macro_report.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"=== 阶段4完成 ===")
    print(f"报告已保存到: {output_path}")
    print("\n" + "="*50)
    print(report)

    return report

if __name__ == '__main__':
    generate_report()
