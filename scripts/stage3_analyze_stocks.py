"""
阶段3：A股关联分析
根据大宗商品涨跌情况，分析受影响的A股
"""
import tushare as ts
import pandas as pd
import os
import json

# 品种-行业映射
COMMODITY_INDUSTRY_MAP = {
    'CU': {'name': '铜', 'industry': '有色金属', 'sw_code': '750100'},
    'AL': {'name': '铝', 'industry': '有色金属', 'sw_code': '750100'},
    'ZN': {'name': '锌', 'industry': '有色金属', 'sw_code': '750100'},
    'PB': {'name': '铅', 'industry': '有色金属', 'sw_code': '750100'},
    'NI': {'name': '镍', 'industry': '有色金属', 'sw_code': '750100'},
    'SN': {'name': '锡', 'industry': '有色金属', 'sw_code': '750100'},
    'RB': {'name': '螺纹钢', 'industry': '钢铁', 'sw_code': '220100'},
    'HC': {'name': '热卷', 'industry': '钢铁', 'sw_code': '220100'},
    'I': {'name': '铁矿石', 'industry': '钢铁', 'sw_code': '220100'},
    'SC': {'name': '原油', 'industry': '石油石化', 'sw_code': '730100'},
    'FU': {'name': '燃油', 'industry': '石油石化', 'sw_code': '730100'},
    'BU': {'name': '沥青', 'industry': '石油石化', 'sw_code': '730100'},
    'J': {'name': '焦炭', 'industry': '煤炭', 'sw_code': '210100'},
    'JM': {'name': '焦煤', 'industry': '煤炭', 'sw_code': '210100'},
    'ZC': {'name': '动力煤', 'industry': '煤炭', 'sw_code': '210100'},
    'A': {'name': '大豆', 'industry': '农业', 'sw_code': '110100'},
    'C': {'name': '玉米', 'industry': '农业', 'sw_code': '110100'},
    'M': {'name': '豆粕', 'industry': '农业', 'sw_code': '110100'},
    'Y': {'name': '豆油', 'industry': '农业', 'sw_code': '110100'},
    'P': {'name': '棕榈油', 'industry': '农业', 'sw_code': '110100'},
    'LH': {'name': '生猪', 'industry': '养殖', 'sw_code': '110200'},
    'AU': {'name': '黄金', 'industry': '贵金属', 'sw_code': '750200'},
    'AG': {'name': '白银', 'industry': '贵金属', 'sw_code': '750200'},
}

def extract_commodity_code(ts_code):
    """从期货代码中提取品种代码"""
    # 例如：CU2403.SHF -> CU
    import re
    match = re.match(r'^([A-Za-z]+)', ts_code)
    return match.group(1).upper() if match else None

def analyze_stock_impact():
    """分析受影响的A股"""
    output_dir = os.path.expanduser('~/.openclaw/workspace/temp/macro')
    input_path = f'{output_dir}/futures_ranked.csv'

    # 检查前置数据
    if not os.path.exists(input_path):
        print(f"错误：找不到数据文件 {input_path}")
        print("请先执行阶段2（stage2_rank_data.py）")
        return None

    print(f"正在读取排序数据: {input_path}")
    df_ranked = pd.read_csv(input_path)

    pro = ts.pro_api()

    # 分析涨跌品种对应的行业
    impact_results = []
    processed_industries = set()

    for _, row in df_ranked.iterrows():
        ts_code = row['ts_code']
        commodity_code = extract_commodity_code(ts_code)

        if commodity_code and commodity_code in COMMODITY_INDUSTRY_MAP:
            mapping = COMMODITY_INDUSTRY_MAP[commodity_code]
            industry = mapping['industry']

            # 避免重复处理同一行业
            if industry in processed_industries:
                continue
            processed_industries.add(industry)

            impact_type = '利好' if row['pct_chg'] > 0 else '利空'

            impact_results.append({
                'commodity': mapping['name'],
                'commodity_code': ts_code,
                'pct_chg': row['pct_chg'],
                'industry': industry,
                'impact_type': impact_type,
                'category': row['category']
            })

    if not impact_results:
        print("未找到可映射的品种-行业关系")
        return None

    df_impact = pd.DataFrame(impact_results)
    output_path = f'{output_dir}/stock_impact.csv'
    df_impact.to_csv(output_path, index=False)

    print(f"\n=== 阶段3完成 ===")
    print(f"已保存影响分析到: {output_path}")

    print("\n=== 利好行业 ===")
    bullish = df_impact[df_impact['impact_type'] == '利好']
    if not bullish.empty:
        print(bullish[['commodity', 'industry', 'pct_chg']].to_string(index=False))
    else:
        print("无")

    print("\n=== 利空行业 ===")
    bearish = df_impact[df_impact['impact_type'] == '利空']
    if not bearish.empty:
        print(bearish[['commodity', 'industry', 'pct_chg']].to_string(index=False))
    else:
        print("无")

    return df_impact

if __name__ == '__main__':
    analyze_stock_impact()
