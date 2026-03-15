"""
阶段1：数据采集
获取期货大宗商品主力合约的收益率数据
"""
import tushare as ts
import pandas as pd
import os
import sys
from datetime import datetime

def get_trade_date(date_str=None):
    """获取交易日期，默认为最近交易日"""
    if date_str:
        return date_str
    # 默认使用昨天
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    return yesterday

def fetch_futures_data(trade_date):
    """获取期货主力合约数据"""
    pro = ts.pro_api()
    output_dir = os.path.expanduser('~/.openclaw/workspace/temp/macro')
    os.makedirs(output_dir, exist_ok=True)

    print(f"正在获取 {trade_date} 的期货数据...")

    # 获取期货主力合约映射
    df_main = pro.fut_mapping(trade_date=trade_date)

    if df_main.empty:
        print(f"警告：{trade_date} 没有期货数据，可能不是交易日")
        return None

    # 获取各合约行情并计算收益率
    results = []
    total = len(df_main)

    for idx, row in df_main.iterrows():
        ts_code = row['ts_code']
        try:
            df = pro.fut_daily(ts_code=ts_code, trade_date=trade_date)
            if not df.empty:
                results.append({
                    'ts_code': ts_code,
                    'name': row.get('mapping_ts_code', ts_code),
                    'close': df['close'].iloc[0],
                    'pre_close': df['pre_close'].iloc[0],
                    'pct_chg': df['pct_chg'].iloc[0]
                })
        except Exception as e:
            print(f"获取 {ts_code} 失败: {e}")

        # 进度显示
        if (idx + 1) % 10 == 0:
            print(f"进度: {idx + 1}/{total}")

    if not results:
        print("未获取到任何数据")
        return None

    df_result = pd.DataFrame(results)
    output_path = f'{output_dir}/futures_raw.csv'
    df_result.to_csv(output_path, index=False)

    print(f"\n=== 阶段1完成 ===")
    print(f"已保存 {len(results)} 条期货数据到: {output_path}")

    return df_result

if __name__ == '__main__':
    # 从命令行参数获取日期
    trade_date = sys.argv[1] if len(sys.argv) > 1 else None
    trade_date = get_trade_date(trade_date)

    df = fetch_futures_data(trade_date)
    if df is not None:
        print(f"\n数据预览:")
        print(df.head(10).to_string(index=False))
