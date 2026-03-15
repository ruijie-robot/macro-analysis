---
name: macro-analysis
description: 宏观市场分析 - 基于大宗商品期货涨跌分析A股影响。支持渐进式调用：阶段1-数据采集，阶段2-涨跌排序，阶段3-A股关联分析，阶段4-报告生成。可通过参数指定起始阶段。
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
  - Skill
---

# 宏观市场分析 Skill

通过分析大宗商品期货涨跌情况，关联分析受影响的 A 股。支持分阶段执行，每个阶段完成后向用户汇报并等待确认。

## 调用方式

```
/macro-analysis [--stage=N] [--date=YYYYMMDD]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--stage=N` | 从第 N 阶段开始执行（1-4） | 1 |
| `--date=YYYYMMDD` | 分析日期 | 最近交易日 |

## 执行流程

```
阶段1 数据采集 ──→ futures_raw.csv
       ↓ 用户确认
阶段2 涨跌排序 ──→ futures_ranked.csv
       ↓ 用户确认
阶段3 A股关联  ──→ stock_impact.csv
       ↓ 用户确认
阶段4 报告生成 ──→ macro_report.md
```

## 数据存储

所有中间数据存储在：`~/.openclaw/workspace/temp/macro/`

---

## 阶段详情

### 阶段 1：数据采集

**目标**：获取期货大宗商品主力合约的收益率数据

**脚本**：[scripts/stage1_fetch_data.py](scripts/stage1_fetch_data.py)

**执行**：
```bash
python scripts/stage1_fetch_data.py [YYYYMMDD]
```

**产出**：`futures_raw.csv`

**完成后**：向用户展示采集到的数据条数，询问是否继续

---

### 阶段 2：涨跌排序

**目标**：对期货收益率排序，筛选涨跌幅前 10

**前置条件**：`futures_raw.csv` 存在

**脚本**：[scripts/stage2_rank_data.py](scripts/stage2_rank_data.py)

**执行**：
```bash
python scripts/stage2_rank_data.py [top_n]
```

**产出**：`futures_ranked.csv`

**完成后**：向用户展示涨跌幅前 10 的合约，询问是否继续

---

### 阶段 3：A股关联分析

**目标**：根据大宗商品涨跌情况，分析受影响的 A 股行业

**前置条件**：`futures_ranked.csv` 存在

**脚本**：[scripts/stage3_analyze_stocks.py](scripts/stage3_analyze_stocks.py)

**执行**：
```bash
python scripts/stage3_analyze_stocks.py
```

**产出**：`stock_impact.csv`

**参考**：[reference/commodity_industry_map.json](reference/commodity_industry_map.json)

**完成后**：向用户展示受影响的行业列表，询问是否继续

---

### 阶段 4：报告生成

**目标**：生成完整的宏观分析报告

**前置条件**：`futures_ranked.csv` 和 `stock_impact.csv` 存在

**脚本**：[scripts/stage4_generate_report.py](scripts/stage4_generate_report.py)

**执行**：
```bash
python scripts/stage4_generate_report.py
```

**产出**：`macro_report.md`

**模板**：[reference/report_template.md](reference/report_template.md)

**完成后**：向用户展示报告摘要，提供报告文件路径

---

## 渐进式调用示例

### 完整执行
```
用户：/macro-analysis
AI：开始阶段1-数据采集...
    [执行完成，展示结果]
    是否继续到阶段2？
用户：继续
AI：开始阶段2-涨跌排序...
```

### 从指定阶段继续
```
用户：/macro-analysis --stage=3
AI：检测到中间数据存在，从阶段3开始...
```

### 指定日期分析
```
用户：/macro-analysis --date=20250312
AI：分析 2025-03-12 的数据...
```

---

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 中间数据不存在 | 提示用户从阶段1开始 |
| API 调用失败 | 重试3次，失败则报错并保留已获取数据 |
| 数据为空 | 提示用户检查日期是否为交易日 |

## 依赖

- `tushare-finance` skill（用于获取金融数据）
- Python 库：tushare, pandas
