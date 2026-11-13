"""Build a deterministic synthetic starter corpus; it is not a bank-provided dataset."""
import csv
from pathlib import Path

MERCHANTS = {
    "Food & Dining": ["Zomato", "Swiggy", "Dominos Pizza", "McDonalds", "Cafe Coffee Day", "EatSure", "restaurant bill", "food delivery"],
    "Groceries": ["BigBasket", "DMart", "Blinkit", "JioMart", "Reliance Fresh", "More Supermarket", "grocery store", "Nature Basket"],
    "Shopping": ["Amazon India", "Flipkart", "Myntra", "Ajio", "Tata Cliq", "Croma", "Nykaa", "Decathlon"],
    "Transportation": ["Uber", "Ola Cabs", "Rapido", "Namma Metro", "FASTag toll", "Delhi Metro", "BMTC bus", "auto rickshaw"],
    "Entertainment": ["Netflix", "Spotify", "BookMyShow", "SonyLiv", "Hotstar", "PVR Cinemas", "YouTube Premium", "Steam Games"],
    "Healthcare": ["Apollo Pharmacy", "Fortis Hospital", "MedPlus", "Practo", "diagnostic lab", "pharmacy purchase", "clinic consultation", "healthcare bill"],
    "Education": ["school tuition", "university fee", "Coursera", "Udemy", "BYJUs", "college fees", "exam registration", "education books"],
    "Utilities": ["electricity bill", "BESCOM", "Airtel Postpaid", "Jio Fiber", "water board", "gas bill", "Tata Power", "mobile recharge"],
    "Housing & Rent": ["monthly house rent", "apartment rent", "landlord payment", "housing society maintenance", "property maintenance", "rental payment", "flat rent", "residential lease"],
    "Travel": ["IndiGo Airlines", "Air India", "MakeMyTrip", "IRCTC", "Yatra booking", "hotel reservation", "airport transfer", "holiday package"],
    "Insurance": ["HDFC Life premium", "LIC premium", "ICICI Lombard", "health insurance premium", "motor insurance", "policy renewal", "term insurance", "insurance payment"],
    "Salary & Income": ["monthly salary credit", "payroll credit", "employer salary", "salary payment", "monthly wages", "bonus credit", "professional income", "salary transfer"],
    "Investments": ["mutual fund SIP", "Zerodha investment", "Groww mutual fund", "stock purchase", "demat investment", "NPS contribution", "investment subscription", "SIP installment"],
    "ATM & Cash Withdrawal": ["ATM cash withdrawal", "cash withdrawal ATM", "ATM WDL", "cash dispensed ATM", "ATM withdrawal fee", "cash machine withdrawal", "branch cash withdrawal", "ATM transaction"],
    "Bank Charges": ["monthly bank service charge", "SMS alert charge", "debit card annual fee", "bank processing charge", "NEFT service fee", "minimum balance charge", "account maintenance fee", "GST bank charges"],
    "Loan & EMI": ["personal loan EMI", "home loan installment", "car loan EMI", "loan repayment", "monthly EMI debit", "education loan installment", "mortgage payment", "consumer loan repayment"],
    "Transfers": ["NEFT fund transfer", "IMPS transfer", "UPI person transfer", "RTGS transfer", "funds transferred", "bank transfer", "P2P payment", "account transfer"],
    "Other / Uncategorized": ["miscellaneous payment", "general merchant purchase", "unclassified transaction", "other debit entry", "unknown POS purchase", "merchant payment", "miscellaneous credit", "unrecognized bill payment"],
}
PREFIXES = ("UPI", "CARD PAYMENT", "POS", "NETBANKING")
SUFFIXES = ("PAYMENT", "PURCHASE", "TXN", "ONLINE")


def build_rows():
    for category, merchants in MERCHANTS.items():
        for i, merchant in enumerate(merchants):
            yield (f"{PREFIXES[i % len(PREFIXES)]} {merchant} {SUFFIXES[i % len(SUFFIXES)]}", category)
            yield (f"{merchant} {PREFIXES[(i + 1) % len(PREFIXES)]} TRANSACTION", category)


if __name__ == "__main__":
    target = Path(__file__).with_name("transactions.csv")
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle); writer.writerow(("description", "category")); writer.writerows(build_rows())
    print(f"Wrote {target}")
