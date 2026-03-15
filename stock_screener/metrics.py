METRICS = {
    "forwardPE": {
        "label": "Forward P/E (as earnings yield)",
        "source": "summary_detail",
        "field": "forwardPE",
        "transform": lambda v: (1 / v * 100) if v and v > 0 else None,
        "higher_is_better": True,
    },
    "cps": {
        "label": "Cash Per Share",
        "source": "financial_data",
        "field": "totalCashPerShare",
        "transform": lambda v: v,
        "higher_is_better": True,
    },
    "roc": {
        "label": "Return on Equity",
        "source": "financial_data",
        "field": "returnOnEquity",
        "transform": lambda v: v,
        "higher_is_better": True,
    },
}