from pathlib import Path
import base64, hashlib, json

root = Path(__file__).parent
m = json.loads((root / 'manifest.json').read_text())
s = ''.join((root / p['name']).read_text().strip() for p in m['parts'])
assert len(s) == m['base64_chars'], (len(s), m['base64_chars'])
data = base64.b64decode(s, validate=True)
assert len(data) == m['archive_bytes'], (len(data), m['archive_bytes'])
h = hashlib.sha256(data).hexdigest()
assert h == m['archive_sha256'], (h, m['archive_sha256'])
out = root / m['archive']
out.write_bytes(data)
print(out)
print(h)
