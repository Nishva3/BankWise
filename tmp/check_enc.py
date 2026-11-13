from pathlib import Path
s=Path('frontend/app.js').read_text(encoding='utf-8-sig')
for line in s.splitlines():
 if any(ord(c)>127 for c in line):
  print(line.encode('unicode_escape').decode()[:240])
