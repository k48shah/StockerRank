def _safe_div(a, b):
    return a / b if a is not None and b else None


METRICS = {
    "forwardPE": {
        "label": "Forward P/E (as earnings yield)",
        "source": "summary_detail",
        "field": "forwardPE",
        "transform": lambda v: (1 / v * 100) if v and v > 0 else None,
        "higher_is_better": True,
        "historical_derive": lambda bs, inc, price: _safe_div(
            price,
            _safe_div(
                inc.get("NetIncome") or inc.get("netIncome"),
                bs.get("OrdinarySharesNumber") or bs.get("ordinaryShares") or bs.get("sharesOutstanding")
            )
        ),
    },
    "cps": {
        "label": "Cash Per Share",
        "source": "financial_data",
        "field": "totalCashPerShare",
        "transform": lambda v: v,
        "higher_is_better": True,
        "historical_derive": lambda bs, *_: _safe_div(
            bs.get("CashAndCashEquivalents") or bs.get("cashAndCashEquivalents") or bs.get("cash"),
            bs.get("OrdinarySharesNumber") or bs.get("ordinaryShares") or bs.get("sharesOutstanding")
        ),
    },
    "roe": {
        "label": "Return on Equity",
        "source": "financial_data",
        "field": "returnOnEquity",
        "transform": lambda v: v,
        "higher_is_better": True,
        "historical_derive": lambda bs, inc, *_: _safe_div(
            inc.get("NetIncome") or inc.get("netIncome"),
            bs.get("TotalEquityGrossMinorityInterest") or bs.get("totalStockholderEquity")
        ),
    },
}
