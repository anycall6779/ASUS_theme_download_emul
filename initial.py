import requests,json,pathlib,datetime,socket
base=pathlib.Path('outputs/ASUS_ROG_Elysia_Original')
for d in ['original','extracted','evidence','analysis']: (base/d).mkdir(parents=True,exist_ok=True)
s=requests.Session()
log=[]
urls={'shortA':'https://rog.gg/ROGxHonkai3','shortB':'https://rog.gg/ROGxHonkai3Elysia','official':'https://rog.asus.com/protection-and-gadgets/cases-and-protection/rog-hi3-elysia-special-collection/','uptodown':'https://zenui-asus-computer-inc-themes.en.uptodown.com/android/download'}
for name,u in urls.items():
 for variant,ua in ([('desktop','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36'),('android','Mozilla/5.0 (Linux; Android 15; ASUS_AI2501) AppleWebKit/537.36 Chrome/131.0.0.0 Mobile Safari/537.36')] if name.startswith('short') else [('desktop','Mozilla/5.0')]):
  for method in (['GET','HEAD'] if name.startswith('short') else ['GET']):
   key=f'{name}_{variant}_{method}'
   try:
    r=s.request(method,u,headers={'User-Agent':ua},allow_redirects=False,timeout=30)
    (base/'evidence'/f'{key}.body').write_bytes(r.content)
    item={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'name':key,'method':method,'url':u,'status':r.status_code,'headers':dict(r.headers),'bytes':len(r.content)}
   except Exception as e: item={'name':key,'url':u,'error':str(e)}
   log.append(item); print(json.dumps(item,ensure_ascii=False))
(base/'evidence'/'initial_http.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
try: (base/'evidence'/'dns.json').write_text(json.dumps(socket.getaddrinfo('rog.gg',443),indent=2))
except Exception as e: print(e)
