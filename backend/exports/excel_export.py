import io
import pandas as pd
from openpyxl.styles import Font, PatternFill


def make_excel(transactions, statement=None):
    output = io.BytesIO()
    tx_columns = ["Date", "Description", "Debit", "Credit", "Balance", "Category", "Classification Method", "Confidence Score"]
    tx = pd.DataFrame([{"Date": t.get("date"), "Description": t.get("description"), "Debit": t.get("debit"), "Credit": t.get("credit"), "Balance": t.get("balance"), "Category": t.get("final_category"), "Classification Method": t.get("method"), "Confidence Score": t.get("confidence")} for t in transactions], columns=tx_columns)
    summary = {"Bank name": None, "Account holder": None, "Masked account number": None, "Statement period": None, "Opening balance": None, "Closing balance": None, "Total credits": sum(float(t.get("credit") or 0) for t in transactions), "Total debits": sum(float(t.get("debit") or 0) for t in transactions)}
    if statement:
        parsed = (statement.get("result") or {}).get("parsed", {})
        summary.update({"Bank name": parsed.get("bank_name"), "Account holder": parsed.get("account_holder"), "Statement period": parsed.get("statement_period"), "Opening balance": parsed.get("opening_balance"), "Closing balance": parsed.get("closing_balance")})
        account = parsed.get("account_number"); summary["Masked account number"] = ("*" * max(0, len(str(account))-4) + str(account)[-4:]) if account else None
    cat_columns = ["Category", "Transaction count", "Total debit", "Total credit"]
    cats = pd.DataFrame([{"Category": k, "Transaction count": sum(t.get("final_category") == k for t in transactions), "Total debit": sum(float(t.get("debit") or 0) for t in transactions if t.get("final_category") == k), "Total credit": sum(float(t.get("credit") or 0) for t in transactions if t.get("final_category") == k)} for k in sorted({t.get("final_category") for t in transactions if t.get("final_category")})], columns=cat_columns)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        tx.to_excel(writer, sheet_name="Transactions", index=False); pd.DataFrame([summary]).to_excel(writer, sheet_name="Account Summary", index=False); cats.to_excel(writer, sheet_name="Category Summary", index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]: cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="163A5F")
            for column in ws.columns: ws.column_dimensions[column[0].column_letter].width = min(48, max(12, max(len(str(c.value or "")) for c in column)+2))
    return output.getvalue()
