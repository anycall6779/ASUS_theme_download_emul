import requests,pathlib,re,json,concurrent.futures
base=pathlib.Path('work'); ev=pathlib.Path('outputs/ASUS_ROG_Elysia_Original/evidence')
urls={
'uptodown_download_js':'https://stc.utdstc.com/1793780937306/download.js',
'apkmirror':'https://www.apkmirror.com/apk/zenui-asus-computer-inc/themes-zenui-asus-computer-inc/asus-themes-stylish-themes-12-0-0-23_250317-release/asus-themes-stylish-themes-12-0-0-23_250317-android-apk-download/',
'apkpure':'https://d.apkpure.net/b/APK/com.asus.themeapp?version=latest',
'jadx':'https://github.com/skylot/jadx/releases/download/v1.5.6/jadx-1.5.6.zip'}
def run(k,u):
 try:
  r=requests.get(u,timeout=90); p=base/({'jadx':'jadx.zip','apkpure':'themeapp.apk'}.get(k,k+'.txt')); p.write_bytes(r.content)
  meta={'url':u,'final_url':r.url,'status':r.status_code,'headers':dict(r.headers),'file':str(p),'size':len(r.content)}
  (ev/(k+'_request.json')).write_text(json.dumps(meta,indent=2)); print(k,r.status_code,len(r.content),r.url)
 except Exception as e: print(k,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(lambda kv:run(*kv),urls.items()))
