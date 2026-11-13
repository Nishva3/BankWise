from pathlib import Path
roots=[Path('frontend'),Path('backend')]
markers={'\u00e2':'â','\u00c3':'Ã','\u00c2':'Â','\ufffd':'replacement character','\u00ef\u00bf\u00bd':'UTF-8 replacement sequence'}
for root in roots:
 for path in root.rglob('*'):
  if path.suffix.lower() not in {'.html','.js','.css','.py','.json','.md','.yaml','.yml'}:continue
  try:text=path.read_text(encoding='utf-8-sig')
  except UnicodeDecodeError:continue
  found=[label for needle,label in markers.items() if needle in text]
  if found:print(path,found)
