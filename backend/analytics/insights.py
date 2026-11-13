import re

import pandas as pd


REFUND_RE = re.compile(r"\b(refund(?:ed)?|reversal|reversed|chargeback|cashback|returned|return credit|merchant credit)\b", re.I)
INCOME_RE = re.compile(r"\b(salary|payroll|pension|dividend|interest credit|rental income|business income)\b", re.I)


def generate_insights(transactions):
    if not transactions:
        return {"available": False, "total_income": 0.0, "total_credits": 0.0,
                "total_expenditure": 0.0, "gross_expenditure": 0.0,
                "total_refunds": 0.0, "total_other_credits": 0.0,
                "net_cash_flow": 0.0, "net_savings": 0.0, "insights": [],
                "category_breakdown": [], "monthly_spending": [],
                "monthly_category_spending": []}

    df = pd.DataFrame(transactions).copy()
    for column in ("debit", "credit"):
        if column not in df:
            df[column] = 0
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).clip(lower=0)
    if "final_category" not in df:
        df["final_category"] = "Other / Uncategorized"
    df["final_category"] = df["final_category"].fillna("Other / Uncategorized").replace("", "Other / Uncategorized")
    descriptions = df.get("description", pd.Series([""] * len(df), index=df.index)).fillna("").astype(str)
    is_refund = descriptions.map(lambda value: bool(REFUND_RE.search(value)))
    is_income = ((df["final_category"] == "Salary & Income") | descriptions.map(lambda value: bool(INCOME_RE.search(value)))) & ~is_refund
    df["_recognized_income"] = df["credit"].where(is_income, 0.0)
    df["_refund_credit"] = df["credit"].where(is_refund, 0.0)
    df["_other_credit"] = (df["credit"] - df["_recognized_income"] - df["_refund_credit"]).clip(lower=0)

    gross_expense = float(df["debit"].sum())
    total_refunds = float(df["_refund_credit"].sum())
    expense = max(0.0, gross_expense - total_refunds)
    income = float(df["_recognized_income"].sum())
    net_savings = income - expense
    total_credits = float(df["credit"].sum())
    net_cash_flow = total_credits - gross_expense
    total_other_credits = float(df["_other_credit"].sum())
    savings_rate = round(net_savings / income * 100, 1) if income else None
    gross = (df["debit"] + df["credit"]).replace(0, pd.NA).dropna()

    by_category = df.groupby("final_category", dropna=False).agg(
        transaction_count=("final_category", "size"), total_debit=("debit", "sum"),
        total_credit=("credit", "sum"), recognized_income=("_recognized_income", "sum"),
        refund_credit=("_refund_credit", "sum"), other_credit=("_other_credit", "sum"),
    ).reset_index().sort_values(["total_debit", "total_credit", "final_category"], ascending=[False, False, True])
    category_breakdown = []
    for row in by_category.to_dict("records"):
        spend = float(row["total_debit"] or 0)
        refunds = float(row["refund_credit"] or 0)
        debit_count = int(((df["final_category"] == row["final_category"]) & (df["debit"] > 0)).sum())
        category_breakdown.append({
            "category": str(row["final_category"]), "transaction_count": int(row["transaction_count"]),
            "total_debit": spend, "total_credit": float(row["total_credit"] or 0),
            "total_income": float(row["recognized_income"] or 0), "total_refunds": refunds,
            "other_credits": float(row["other_credit"] or 0), "net_expense": max(0.0, spend - refunds),
            "net_cash_flow": float(row["total_credit"] or 0) - spend,
            "expense_share_percent": round(max(0.0, spend - refunds) / expense * 100, 1) if expense else 0.0,
            "average_debit": round(spend / debit_count, 2) if debit_count else 0.0,
            "illustrative_10_percent_reduction": round(max(0.0, spend - refunds) * 0.10, 2),
        })

    if "date" in df:
        df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m")
    else:
        df["month"] = None
    dated = df.dropna(subset=["month"])
    monthly = dated.groupby("month").agg(
        debit=("debit", "sum"), credit=("credit", "sum"), income=("_recognized_income", "sum"),
        refunds=("_refund_credit", "sum"), other_credits=("_other_credit", "sum"), transaction_count=("month", "size"),
    ).sort_index()
    monthly_spending = [{
        "month": str(month), "amount": max(0.0, float(row.debit - row.refunds)),
        "gross_expenses": float(row.debit), "refunds": float(row.refunds), "other_credits": float(row.other_credits), "income": float(row.income),
        "net_cash_flow": float(row.credit - row.debit),
        "net_savings": float(row.income - row.debit + row.refunds),
        "transaction_count": int(row.transaction_count),
    } for month, row in monthly.iterrows()]
    month_category = dated.groupby(["month", "final_category"]).agg(
        debit=("debit", "sum"), credit=("credit", "sum"), income=("_recognized_income", "sum"),
        refunds=("_refund_credit", "sum"), other_credits=("_other_credit", "sum"), transaction_count=("month", "size"),
    ).reset_index().sort_values(["month", "debit", "final_category"], ascending=[True, False, True])
    monthly_category_spending = [{
        "month": str(row["month"]), "category": str(row["final_category"]),
        "total_debit": float(row["debit"]), "total_credit": float(row["credit"]),
        "total_income": float(row["income"]), "total_refunds": float(row["refunds"]),
        "other_credits": float(row["other_credits"]),
        "net_expense": max(0.0, float(row["debit"] - row["refunds"])),
        "transaction_count": int(row["transaction_count"]),
    } for row in month_category.to_dict("records")]

    insights = [{
        "type": "net_cash_flow", "amount": round(net_cash_flow, 2), "net_savings": round(net_savings, 2),
        "savings_rate_percent": savings_rate,
        "basis": "Net cash flow includes all credits; net savings uses recognized income less expenses after refunds.",
    }]
    for item in category_breakdown:
        if item["total_debit"] > 0 or item["total_income"] > 0 or item["total_refunds"] > 0:
            insights.append({"type": "category_spending", **item})
    if len(monthly) >= 2:
        previous, latest = float(monthly.iloc[-2]["debit"] - monthly.iloc[-2]["refunds"]), float(monthly.iloc[-1]["debit"] - monthly.iloc[-1]["refunds"])
        change = (latest - previous) / previous * 100 if previous else None
        insights.append({"type": "month_over_month_spending", "previous_month": str(monthly.index[-2]),
                         "current_month": str(monthly.index[-1]), "previous_amount": previous,
                         "current_amount": latest, "change_percent": round(change, 1) if change is not None else None})

    description_column = "normalized_description" if "normalized_description" in df else "description"
    descriptions_for_recurring = df.get(description_column, pd.Series([""] * len(df), index=df.index)).fillna("")
    recurring_df = df.assign(_description=descriptions_for_recurring.map(lambda value: re.sub(r"\s+", " ", str(value).lower()).strip()))
    recurring_df = recurring_df[(recurring_df["_description"] != "") & (recurring_df["debit"] > 0) & recurring_df["month"].notna()]
    recurring = []
    for description, group in recurring_df.groupby("_description"):
        months = sorted(set(group["month"]))
        if len(months) >= 2:
            recurring.append({"description": str(description), "months": months,
                              "average_amount": round(float(group["debit"].mean()), 2), "occurrences": int(len(group))})
    if recurring:
        insights.append({"type": "recurring_payments", "count": len(recurring), "items": recurring[:50]})

    return {"available": True, "total_income": income, "total_credits": total_credits,
            "total_expenditure": expense,
            "gross_expenditure": gross_expense, "total_refunds": total_refunds,
            "total_other_credits": total_other_credits,
            "net_cash_flow": net_cash_flow, "net_savings": net_savings, "savings_rate_percent": savings_rate,
            "illustrative_total_10_percent_reduction": round(expense * 0.10, 2),
            "average_transaction_value": float(gross.mean()) if not gross.empty else 0.0,
            "average_monthly_expenditure": float(monthly_spending and sum(x["amount"] for x in monthly_spending) / len(monthly_spending)) if monthly_spending else None,
            "highest_spending_category": max(category_breakdown, key=lambda x: x["net_expense"])["category"] if category_breakdown else None,
            "largest_debit": float(df["debit"].max()), "most_frequent_merchants": descriptions.value_counts().head(10).to_dict(),
            "income_expense_ratio": income / expense if expense else None,
            "category_breakdown": category_breakdown, "monthly_spending": monthly_spending,
            "monthly_category_spending": monthly_category_spending, "insights": insights}
