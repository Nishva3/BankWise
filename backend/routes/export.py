from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
import re
from .common import db, owner, oid
from exports.csv_export import make_csv
from exports.excel_export import make_excel

bp = Blueprint("export", __name__, url_prefix="/api/export")


def rows():
    q = {"owner_id": owner()}; sid = oid(request.args.get("statement_id", "")); cat = request.args.get("category")
    if sid: q["statement_id"] = sid
    if cat: q["final_category"] = cat
    date_from = request.args.get("date_from"); date_to = request.args.get("date_to")
    if date_from or date_to:
        q["date"] = {}
        if date_from: q["date"]["$gte"] = date_from
        if date_to: q["date"]["$lte"] = date_to
    search = request.args.get("search", "").strip()
    if search: q["description"] = {"$regex": re.escape(search), "$options": "i"}
    return list(db().transactions.find(q).sort("date", -1).limit(50000)), (db().bank_statements.find_one({"_id": sid, "owner_id": owner()}) if sid else None)


@bp.get("/csv")
@jwt_required()
def csv_export(): return Response(make_csv(rows()[0]), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=bankwise-transactions.csv"})


@bp.get("/excel")
@jwt_required()
def excel_export():
    transactions, statement = rows()
    return Response(make_excel(transactions, statement), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=bankwise-report.xlsx"})
