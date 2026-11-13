import fs from 'node:fs/promises';
import path from 'node:path';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const root = process.cwd();
const workDir = path.join(root, 'tmp', 'bankwise_sample_2');
const outDir = path.join(root, 'outputs', 'bankwise_sample_2_20261113');
await fs.mkdir(outDir, { recursive: true });

const openingBalance = 25000;
const rows = [];
const add = (date, description, debit, credit, category, flag = 'No', note = '') => {
  rows.push({ date, description, debit, credit, category, flag, note,
    reference: `BW${String(rows.length + 1).padStart(7, '0')}` });
};

// Deterministic 100-row synthetic retail account statement spanning three months.
add('2026-08-01', 'UPI/DR/RENT HOME', 18000, 0, 'Housing');
add('2026-08-02', 'UPI/DR/GROCERY MART', 1840.75, 0, 'Groceries');
add('2026-08-03', 'SALARY CREDIT ACME SYSTEMS', 0, 68000, 'Salary & Income');
add('2026-08-04', 'UPI/DR/METRO TRANSIT', 240, 0, 'Transport');
add('2026-08-05', 'CARD/DR/PHARMACY PLUS', 730, 0, 'Healthcare');
add('2026-08-06', 'UPI/DR/COFFEE CAFE', 195, 0, 'Dining');
add('2026-08-07', 'UPI/DR/COFFEE CAFE', 220, 0, 'Dining');
add('2026-08-08', 'UPI/DR/COFFEE CAFE', 180, 0, 'Dining');
add('2026-08-09', 'UPI/DR/COFFEE CAFE', 210, 0, 'Dining');
add('2026-08-10', 'UPI/DR/COFFEE CAFE', 205, 0, 'Dining');
add('2026-08-11', 'UPI/DR/COFFEE CAFE', 175, 0, 'Dining');
add('2026-08-12', 'UPI/DR/COFFEE CAFE', 235, 0, 'Dining');
add('2026-08-13', 'UPI/DR/COFFEE CAFE', 190, 0, 'Dining');
add('2026-08-14', 'NEFT/CR/FREELANCE DESIGN', 0, 12500, 'Business Income');
add('2026-08-15', 'CARD/DR/ONLINE BOOKS', 1299, 0, 'Shopping');
add('2026-08-16', 'UPI/DR/ELECTRICITY BILL', 1680, 0, 'Utilities');
add('2026-08-17', 'UPI/DR/RESTAURANT NORTH', 1180, 0, 'Dining');
add('2026-08-18', 'UPI/DR/FUEL STATION', 2200, 0, 'Transport');
add('2026-08-19', 'CARD/DR/STREAMING SERVICE', 649, 0, 'Subscriptions');
add('2026-08-20', 'NEFT/CR/RENTAL INCOME', 0, 9500, 'Rental Income');
add('2026-08-21', 'UPI/DR/GROCERY MART', 2340.20, 0, 'Groceries');
add('2026-08-22', 'CARD/DR/SHOES ONLINE', 3499, 0, 'Shopping');
add('2026-08-23', 'UPI/DR/DOCTOR CLINIC', 950, 0, 'Healthcare');
add('2026-08-24', 'UPI/DR/METRO TRANSIT', 260, 0, 'Transport');
add('2026-08-25', 'UPI/DR/WATER BILL', 540, 0, 'Utilities');
add('2026-08-26', 'CARD/DR/RESTAURANT EAST', 1780, 0, 'Dining');
add('2026-08-27', 'UPI/DR/PETROL PUMP', 1950, 0, 'Transport');
add('2026-08-28', 'UPI/CR/MERCHANT REFUND', 0, 499, 'Refund');
add('2026-08-29', 'UPI/DR/GROCERY MART', 860, 0, 'Groceries');
add('2026-08-30', 'NEFT/DR/INVESTMENT SIP', 5000, 0, 'Investments');
add('2026-08-31', 'UPI/DR/PHONE BILL', 799, 0, 'Utilities');

const standard = [
  ['UPI/DR/GROCERY MART', 920, 'Groceries'], ['UPI/DR/METRO TRANSIT', 240, 'Transport'],
  ['CARD/DR/PHARMACY PLUS', 460, 'Healthcare'], ['UPI/DR/RESTAURANT NORTH', 980, 'Dining'],
  ['UPI/DR/ELECTRICITY BILL', 1430, 'Utilities'], ['CARD/DR/ONLINE BOOKS', 790, 'Shopping'],
  ['UPI/DR/FUEL STATION', 1850, 'Transport'], ['UPI/DR/GROCERY MART', 1730, 'Groceries'],
  ['CARD/DR/STREAMING SERVICE', 649, 'Subscriptions'], ['UPI/DR/DOCTOR CLINIC', 700, 'Healthcare'],
  ['UPI/DR/RESTAURANT EAST', 1290, 'Dining'], ['UPI/DR/WATER BILL', 510, 'Utilities'],
  ['CARD/DR/SHOES ONLINE', 2190, 'Shopping'], ['UPI/DR/METRO TRANSIT', 260, 'Transport'],
  ['UPI/DR/GROCERY MART', 2100, 'Groceries'], ['UPI/DR/PHONE BILL', 799, 'Utilities'],
  ['UPI/DR/PETROL PUMP', 2010, 'Transport'], ['CARD/DR/RESTAURANT NORTH', 1490, 'Dining'],
  ['CARD/DR/PHARMACY PLUS', 340, 'Healthcare'], ['UPI/DR/ONLINE MARKET', 1350, 'Shopping'],
  ['UPI/DR/GROCERY MART', 1140, 'Groceries'], ['UPI/DR/COFFEE CAFE', 210, 'Dining'],
  ['UPI/DR/ELECTRICITY BILL', 1590, 'Utilities'], ['NEFT/DR/INVESTMENT SIP', 5000, 'Investments'],
  ['UPI/DR/RESTAURANT EAST', 1070, 'Dining'], ['UPI/DR/METRO TRANSIT', 220, 'Transport'],
  ['CARD/DR/ONLINE BOOKS', 1160, 'Shopping'], ['UPI/DR/GROCERY MART', 1920, 'Groceries'],
];
const day = (n) => String(n).padStart(2, '0');
for (const [month, startDay] of [['2026-09', 1], ['2026-10', 1]]) {
  add(`${month}-${day(startDay)}`, 'UPI/DR/RENT HOME', 18000, 0, 'Housing');
  add(`${month}-${day(startDay + 1)}`, 'SALARY CREDIT ACME SYSTEMS', 0, 68000, 'Salary & Income');
  add(`${month}-${day(startDay + 2)}`, 'NEFT/CR/FREELANCE DESIGN', 0, month === '2026-09' ? 8700 : 16200, 'Business Income');
  add(`${month}-${day(startDay + 3)}`, 'NEFT/CR/RENTAL INCOME', 0, 9500, 'Rental Income');
  for (let i = 0; i < 27; i++) {
    const [description, amount, category] = standard[(i + (month === '2026-10' ? 7 : 0)) % standard.length];
    const d = ((i * 3 + 6) % 27) + 4;
    add(`${month}-${day(d)}`, description, amount + ((i % 4) * 17.5), 0, category);
  }
}
// Clear synthetic anomalies: one extreme debit, a same-day repeated row, and one unusual credit.
add('2026-10-28', 'CARD/DR/ELECTRONICS STORE', 128500, 0, 'Shopping', 'Yes', 'Unusually large debit compared with the rest of this statement.');
add('2026-10-29', 'UPI/DR/GROCERY MART', 645.50, 0, 'Groceries');
add('2026-10-29', 'UPI/DR/GROCERY MART', 645.50, 0, 'Groceries', 'Yes', 'Exact duplicate row on the same date and for the same amount.');
add('2026-10-30', 'NEFT/CR/UNEXPECTED CREDIT', 0, 42500, 'Other Credit', 'Yes', 'Unusual credit included to exercise credit classification and review.');
while (rows.length < 100) {
  const i = rows.length;
  const [description, amount, category] = standard[i % standard.length];
  const month = i % 2 ? '2026-09' : '2026-10';
  add(`${month}-${day((i % 27) + 4)}`, description, amount + ((i % 5) * 12.25), 0, category);
}
if (rows.length !== 100) throw new Error(`Expected 100 rows, got ${rows.length}`);

rows.sort((a, b) => a.date.localeCompare(b.date) || a.reference.localeCompare(b.reference));
let balance = openingBalance;
for (const row of rows) {
  balance += row.credit - row.debit;
  row.balance = Number(balance.toFixed(2));
  row.type = row.debit > 0 ? 'Debit' : 'Credit';
}
const closingBalance = Number(balance.toFixed(2));
await fs.writeFile(path.join(workDir, 'transactions.json'), JSON.stringify({ openingBalance, closingBalance, rows }, null, 2));

const wb = Workbook.create();
const txSheet = wb.worksheets.add('Transactions');
txSheet.showGridLines = false;
const headers = ['Date', 'Description', 'Debit (INR)', 'Credit (INR)', 'Balance (INR)', 'Category', 'Reference', 'Type', 'Test Anomaly', 'Test Note'];
const values = [headers, ...rows.map(r => [new Date(`${r.date}T00:00:00Z`), r.description, r.debit, r.credit, r.balance, r.category, r.reference, r.type, r.flag, r.note])];
txSheet.getRange(`A1:J${values.length}`).values = values;
txSheet.getRange('A1:J1').format = { fill: '#12523E', font: { bold: true, color: '#FFFFFF' }, wrapText: true, verticalAlignment: 'center' };
txSheet.getRange('A1:J1').format.rowHeight = 32;
txSheet.getRange(`A2:A${values.length}`).format.numberFormat = 'dd-mmm-yyyy';
txSheet.getRange(`C2:E${values.length}`).format.numberFormat = '#,##0.00';
txSheet.getRange(`A2:J${values.length}`).format.verticalAlignment = 'center';
txSheet.getRange(`J2:J${values.length}`).format.wrapText = true;
for (const [col, width] of [['A', 14], ['B', 34], ['C', 15], ['D', 15], ['E', 17], ['F', 22], ['G', 16], ['H', 12], ['I', 14], ['J', 62]]) txSheet.getRange(`${col}:${col}`).format.columnWidth = width;
txSheet.tables.add(`A1:J${values.length}`, true, 'SampleTransactions').style = 'TableStyleMedium2';
txSheet.freezePanes.freezeRows(1);

const notes = wb.worksheets.add('Dataset Notes');
notes.showGridLines = false;
notes.getRange('A1:B12').values = [
  ['BankWise Synthetic Test Statement', ''],
  ['Dataset size', 100],
  ['Period', '1 Aug 2026 to 30 Oct 2026'],
  ['Opening balance (INR)', openingBalance],
  ['Closing balance (INR)', closingBalance],
  ['Data provenance', 'Entirely synthetic; no real account or customer data.'],
  ['Upload format', 'The BankWise upload screen accepts PDF statements. Use the matching PDF companion to test upload.'],
  ['Anomaly 1', '128,500 INR electronics debit, intended to exercise high-value anomaly detection.'],
  ['Anomaly 2', 'Two identical grocery debits on 29 Oct 2026, intended to exercise duplicate detection.'],
  ['Anomaly 3', '42,500 INR unexpected credit, intended to exercise credit and review handling.'],
  ['Regular patterns', 'Monthly salary, freelance and rental income; utilities; rent; investments; transport; groceries; dining; healthcare; subscriptions; shopping; refund.'],
  ['Note', 'Dates and balances are real Excel values. Test Anomaly and Test Note are labels for checking expected behavior.'],
];
notes.getRange('A1:B1').format = { fill: '#12523E', font: { bold: true, color: '#FFFFFF', size: 15 }, rowHeight: 30 };
notes.getRange('A2:A12').format = { fill: '#EAF5EF', font: { bold: true, color: '#173B2D' }, wrapText: true };
notes.getRange('B1:B12').format.wrapText = true;
notes.getRange('A:A').format.columnWidth = 25;
notes.getRange('B:B').format.columnWidth = 100;
notes.getRange('A4:B5').format.numberFormat = '#,##0.00';
notes.getRange('A1:B12').format.verticalAlignment = 'center';
notes.getRange('A1:B12').format.rowHeight = 24;
notes.getRange('B6:B12').format.rowHeight = 40;
notes.freezePanes.freezeRows(1);

wb.recalculate();
const inspection = await wb.inspect({ kind: 'table', range: 'Transactions!A1:J8', include: 'values', tableMaxRows: 8, tableMaxCols: 10 });
await fs.writeFile(path.join(workDir, 'workbook_inspection.ndjson'), inspection.ndjson);
const exported = await SpreadsheetFile.exportXlsx(wb);
await exported.save(path.join(outDir, 'bankwise_sample_dataset_2.xlsx'));
console.log(JSON.stringify({ rows: rows.length, openingBalance, closingBalance, xlsx: path.join(outDir, 'bankwise_sample_dataset_2.xlsx') }));
