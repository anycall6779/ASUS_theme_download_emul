from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib,zipfile,io,json
base=Path('outputs/ASUS_ROG_Elysia_Original'); key=hashlib.md5(b'asus1234asus1234').digest();iv=b'asus#1234'.ljust(16,b'\0'); rep=[]
for p in sorted((base/'extracted/assets').iterdir()):
 if not p.is_file() or p.suffix not in ['.apk','.zip']:continue
 data=unpad(AES.new(key,AES.MODE_CBC,iv).decrypt(p.read_bytes()),16)
 z=zipfile.ZipFile(io.BytesIO(data)); encrypted=any(i.flag_bits & 1 for i in z.infolist());bad=None if encrypted else z.testzip();assert bad is None
 out=base/'extracted/decrypted_modules'/p.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 dest=base/'extracted/module_resources'/p.stem
 for f in z.infolist():
  if not (dest/f.filename).resolve().is_relative_to(dest.resolve()):raise ValueError('Bad ZIP path')
 
 if not encrypted: z.extractall(dest)
 media=[n for n in z.namelist() if n.endswith(('.mp4','.ogg','.gif','.webm','.bin','.json','.xml'))]
 rep.append({'module':p.name,'decrypted_size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'entries':len(z.infolist()),'inner_zip_encrypted':encrypted,'bad_crc':bad,'crc_tested':not encrypted,'files':[{'path':i.filename,'size':i.file_size} for i in z.infolist()]})
 print(p.name,len(data),len(z.infolist()));print('\n'.join(media[:35]))
(base/'analysis/decrypted_module_inventory.json').write_text(json.dumps(rep,indent=2),encoding='utf-8')
