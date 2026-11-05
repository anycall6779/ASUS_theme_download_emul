"""Download and verify the ASUS original; optional offline resource extraction.

python acquire_verify.py --out NEW_DIRECTORY --decrypt
Only --decrypt requires: python -m pip install pycryptodome
No APK installation/execution or device/account access is used.
"""
import argparse
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

BASE = 'https://dlcdnamaxthemedata.asus.com/Rel/App/'
THEME_ID = 'th01082025001'
EXPECTED_SIZE = 49499531
EXPECTED_SHA256 = '6f4c68788e5fceccaced1d519d8c9575492a3e83fb7a17e74a1c2fa01743aad0'


def fetch(url, path):
    request = urllib.request.Request(url, headers={'User-Agent': 'ElysiaArchiveVerification/1.0'})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
        meta = {'url': url, 'final_url': response.url, 'status': response.status,
                'headers': dict(response.headers), 'bytes': len(data),
                'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'sha256': hashlib.sha256(data).hexdigest()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.with_name(path.name + '.http.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return data, meta


def unpack(archive, destination):
    """Validate every unencrypted entry and extract without path traversal."""
    rows = []
    root = destination.resolve()
    for info in archive.infolist():
        target = (root / info.filename).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Unsafe archive path: ' + info.filename)
        encrypted = bool(info.flag_bits & 1)
        rows.append({'path': info.filename, 'bytes': info.file_size,
                     'zip_encrypted': encrypted, 'crc32': f'{info.CRC:08x}'})
        if encrypted:
            continue
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))  # CRC checked by zipfile
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('ASUS_ROG_Elysia_Reproduction'))
    parser.add_argument('--decrypt', action='store_true')
    args = parser.parse_args()
    root = args.out.resolve()
    # Never overwrite an existing evidence set.
    if root.exists() and any(root.iterdir()):
        raise ValueError('Output directory must be empty: ' + str(root))
    for name in ('original', 'extracted', 'evidence', 'analysis'):
        (root / name).mkdir(parents=True, exist_ok=True)
    catalog_raw, _ = fetch(BASE + 'ThemeData/ThemeApp/theme_list.json.gz',
                           root / 'evidence/theme_list.json.gz')
    catalog = json.loads(gzip.decompress(catalog_raw))
    entry = next(x for x in catalog['data'] if x.get('sku_id') == THEME_ID)
    if entry.get('package_name') != 'com.asus.themes.' + THEME_ID:
        raise ValueError('Unexpected package identity')
    (root / 'analysis/catalog_entry.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
    relative = entry['download_url']
    if relative != f'ThemeData/com.asus.themes.{THEME_ID}/{THEME_ID}.zip':
        raise ValueError('Catalog download path changed; review before downloading')
    data, meta = fetch(BASE + relative, root / f'original/{THEME_ID}.zip')
    if len(data) != EXPECTED_SIZE or meta['sha256'] != EXPECTED_SHA256:
        raise ValueError('Original has changed: retained file must be reviewed; do not label verified')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:
            raise ValueError('Original ZIP CRC failure')
        manifest = json.loads(archive.read('assets/manifest.json'))
        if manifest.get('sku-id') != THEME_ID:
            raise ValueError('Internal theme identity mismatch')
        missing = [x['asset-path'] for x in manifest['theme-module']
                   if 'assets/' + x['asset-path'] not in archive.namelist()]
        if missing:
            raise ValueError('Missing declared modules: ' + repr(missing))
        rows = unpack(archive, root / 'extracted')
    (root / 'analysis/archive_inventory.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    (root / 'SHA256SUMS.txt').write_text(f'{EXPECTED_SHA256}  original/{THEME_ID}.zip\n', encoding='utf-8')
    print(f'VERIFIED original: {THEME_ID}.zip | {len(data)} bytes | SHA256 {meta["sha256"]}')
    print(f'Declared modules present: {len(manifest["theme-module"])}/{len(manifest["theme-module"])}')
    if args.decrypt:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
        # Derived from ASUS Themes 10.0.0.24_230329 y1.d.h/i/k/q and y1.w.n(null).
        if manifest.get('encryption-key') != 1:
            raise ValueError('Unknown module encryption version')
        key = hashlib.md5(b'asus1234asus1234').digest()
        iv = b'asus#1234'.ljust(16, b'\0')
        module_rows = []
        for source in sorted((root / 'extracted/assets').iterdir()):
            if source.suffix not in ('.apk', '.zip') or not source.is_file():
                continue
            plain = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(source.read_bytes()), 16)
            dest = root / 'extracted/decrypted_modules' / source.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(plain)) as archive:
                files = unpack(archive, root / 'extracted/module_resources' / source.stem)
            dest.write_bytes(plain)
            encrypted = sum(x['zip_encrypted'] for x in files)
            module_rows.append({'module': source.name, 'sha256': hashlib.sha256(plain).hexdigest(),
                                'bytes': len(plain), 'unextracted_zip_encrypted_entries': encrypted,
                                'files': files})
            print(f'Extracted {source.name}: {len(files) - encrypted}/{len(files)} entries; encrypted retained: {encrypted}')
        (root / 'analysis/module_inventory.json').write_text(json.dumps(module_rows, indent=2), encoding='utf-8')
    print('Output:', root)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'ERROR: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
