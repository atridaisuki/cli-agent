---
name: session-analytics
description: 分析会话数据，统计 token 消耗、工具调用频率、活跃时段
invocable: both
argument-hint: "<'today' | '--date YYYY-MM-DD' | '--range N' | '--errors'>"
---

# Session Analytics

分析 JSONL 会话日志，输出统计报告。

**使用方式：**
执行 `python skills/session-analytics/session_analytics.py --log-dir data/sessions` 并将结果展示给用户。

支持的参数：
- `--date YYYY-MM-DD` 指定日期
- `--range N` 最近 N 天
- `--errors` 只看错误
- `--format markdown` Markdown 格式输出
