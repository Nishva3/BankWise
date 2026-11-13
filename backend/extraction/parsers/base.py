import re

DATE_RE = re.compile(r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[- ]+[A-Za-z]{3}[- ]+\d{2,4}|\d{4}-\d{2}-\d{2})\b", re.I)
AMOUNT_RE = re.compile(r"(?<![A-Za-z0-9])(?:(?:₹|INR\s*|Rs\.?\s*))?\(?-?\d[\d,]*\.\d{2}\)?(?:\s*(?:Dr|Cr))?", re.I)
REFERENCE_RE = re.compile(r"\b(?:ref(?:erence)?|utr|cheque|chq)\s*(?:no\.?|#)?\s*[: -]?\s*([A-Z0-9/-]{5,})", re.I)


class BankParser:
    bank_name = "Unknown"
    aliases = ()

    def identifies(self, text):
        return any(re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", text) for alias in self.aliases)

    def parse_line(self, line, columns=None):
        date_match = DATE_RE.match(line)
        if not date_match:
            return None
        if columns:
            aligned = self.parse_aligned_columns(line, columns)
            if aligned:
                return aligned
        tail = line[date_match.end():]
        amounts = list(AMOUNT_RE.finditer(tail))
        if not amounts:
            return None
        description = tail[:amounts[0].start()].strip(" |\t-:")
        if not description:
            return None
        tokens = [m.group().strip() for m in amounts]
        values = [float(re.sub(r"[^\d.]", "", token) or 0) for token in tokens]
        direction = " ".join(tokens).lower()
        narration_direction = re.search(r"\b(?:upi|neft|imps|rtgs)[/-](?:dr|debit|cr|credit)[/-]", description, re.I)
        if narration_direction:
            direction += " " + narration_direction.group().lower()
        debit = credit = 0.0
        balance = None
        notes = []
        if len(values) >= 3:
            debit, credit, balance = values[0], values[1], values[-1]
            if not re.search(r"\b(?:dr|cr)\b", direction, re.I):
                notes.append("Unlabeled amount order assumed to be debit, credit, balance; verify values.")
        elif len(values) == 2:
            balance = values[-1]
            if "cr" in direction: credit = values[0]
            elif "dr" in direction: debit = values[0]
            else:
                debit = values[0]
                notes.append("Two amounts without Dr/Cr marker; debit assignment is uncertain.")
        elif "cr" in direction:
            credit = values[0]
        elif "dr" in direction:
            debit = values[0]
        else:
            notes.append("Single amount without Dr/Cr marker; debit/credit direction is uncertain.")
        ref = REFERENCE_RE.search(description)
        second_date = DATE_RE.search(tail)
        value_date = second_date.group(1) if second_date else None
        if second_date:
            description = (description[:second_date.start()] + description[second_date.end():]).strip(" /|")
        return {"date": date_match.group(1), "value_date": value_date, "description": description,
                "reference": ref.group(1) if ref else None, "debit": debit, "credit": credit,
                "balance": balance, "warnings": notes}

    def parse_aligned_columns(self, line, columns):
        parts = [item.strip() for item in re.split(r"\s{2,}|\|", line.strip().strip("|"))]
        column_count = columns.get("_count", len(parts))
        indices = [index for key, index in columns.items() if key != "_count"]
        if len(parts) != column_count or max(indices, default=-1) >= len(parts):
            return None
        def cell(name):
            index = columns.get(name)
            return parts[index].strip() if index is not None and index < len(parts) else ""
        date_match = DATE_RE.match(cell("date"))
        # Keep reference identifiers out of the merchant narration; appending
        # them made the same merchant look unique on every statement row.
        description = cell("description").strip()
        if not date_match or not description:
            return None
        def amount(name):
            value = cell(name).replace("₹", "").replace(",", "").strip()
            try: return float(re.sub(r"[^\d.+-]", "", value) or 0)
            except ValueError: return 0.0
        value_date = cell("value_date") or None
        return {"date": date_match.group(1), "value_date": value_date, "description": description,
                "reference": cell("reference") or None, "debit": amount("debit"), "credit": amount("credit"),
                "balance": amount("balance") if cell("balance") else None, "warnings": []}
