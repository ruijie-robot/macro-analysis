"""
阶段2：涨跌排序
对期货收益率进行排序，筛选涨跌幅前10
"""
import pandas as pd
import os
import sys

def rank_futures_data(top_n=10):
    """对期货数据进行涨跌幅排序"""
    output_dir = os.path.expanduser('~/.openclaw/workspace/temp/macro')
    input_path = f'{output_dir}/futures_raw.csv'

    # 检查前置数据
    if not os.path.exists(input_path):
        print(f"错误：找不到数据文件 {input_path}")
        print("请先执行阶段1（stage1_fetch_data.py）")
        return None

    print(f"正在读取数据: {input_path}")
    df = pd.read_csv(input_path)

    # 排序
    df_sorted = df.sort_values('pct_chg', ascending=False)

    # 涨幅前N
    top_gainers = df_sorted.head(top_n).copy()
    top_gainers['category'] = '涨幅前10'

    # 跌幅前N
    top_losers = df_sorted.tail(top_n).copy()
    top_losers['category'] = '跌幅前10'

    # 合并保存
    df_ranked = pd.concat([top_gainers, top_losers])
    output_path = f'{output_dir}/futures_ranked.csv'
    df_ranked.to_csv(output_path, index=False)

    print(f"\n=== 阶段2完成 ===")
    print(f"已保存排序结果到: {output_path}")

    print("\n=== 涨幅前10 ===")
    print(top_gainers[['name', 'pct_chg']].to_string(index=False))

    print("\n=== 跌幅前10 ===")
    print(top_losers[['name', 'pct_chg']].to_string(index=False))

    return df_ranked

if __name__ == '__main__':
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    rank_futures_data(top_n)
