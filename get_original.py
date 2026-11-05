import requests,pathlib,json,gzip,hashlib,zipfile,datetime
base=pathlib.Path('outputs/ASUS_ROG_Elysia_Original')
j=json.loads(gzip.decompress((base/'evidence/theme_list.json.gz').read_bytes()))
e=next(x for x in j['data'] if x['sku_id']=='th01082025001')
(base/'analysis/elysia_catalog_entry.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
u='https://dlcdnamaxthemedata.asus.com/Rel/App/'+e['download_url'];print('GET',u,flush=True)
r=requests.get(u,timeout=120);r.raise_for_status();p=base/'original/th01082025001.zip';p.write_bytes(r.content)
meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':u,'final_url':r.url,'status':r.status_code,'headers':dict(r.headers),'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest()}
(base/'evidence/original_download.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta,indent=2))
with zipfile.ZipFile(p) as z:
 print('entries',len(z.infolist()),'bad_crc',z.testzip());print('\n'.join(z.namelist()[:100]))
 (base/'analysis/archive_inventory.json').write_text(json.dumps([{'path':i.filename,'size':i.file_size,'compressed_size':i.compress_size,'crc32':f'{i.CRC:08x}'} for i in z.infolist()],indent=2),encoding='utf-8')
 for i in z.infolist():
  dst=(base/'extracted'/i.filename).resolve()
  if not dst.is_relative_to((base/'extracted').resolve()):raise RuntimeError('Unsafe ZIP path')
 z.extractall(base/'extracted')
