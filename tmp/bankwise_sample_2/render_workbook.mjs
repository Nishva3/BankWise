import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const file = 'outputs/bankwise_sample_2_20261113/bankwise_sample_dataset_2.xlsx';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
for (const [sheetName, range, output] of [
  ['Transactions', 'A1:J14', 'tmp/bankwise_sample_2/transactions_preview.png'],
  ['Dataset Notes', 'A1:B12', 'tmp/bankwise_sample_2/notes_preview.png'],
]) {
  const preview = await wb.render({ sheetName, range, scale: 1.5 });
  await fs.writeFile(output, new Uint8Array(await preview.arrayBuffer()));
}
console.log('Rendered workbook sheets for visual review.');
