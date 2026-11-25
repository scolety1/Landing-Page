import json, shutil, base64, time
from playwright.sync_api import sync_playwright
from urllib.request import urlopen
for _ in range(20):
 try: urlopen('http://127.0.0.1:8765/').close();break
 except Exception: time.sleep(.3)
sizes=[(320,568,True),(360,640,True),(390,844,True),(414,896,True),(768,1024,True),(844,390,True),(1024,600,False),(1280,720,False),(1440,900,False)]
ids=['top','story','development','ux','headliners','playground','collection','world','future']
failures=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 for w,h,touch in sizes:
  page=b.new_page(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,reduced_motion='reduce',device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8765/',wait_until='load')
  page.wait_for_function('window.ChapterNavigation')
  if not page.evaluate('ChapterNavigation.guided'):page.locator('#scroll-mode').click()
  for id in ids:
   page.evaluate("(id)=>ChapterNavigation.selectId(id,{instant:true})",id)
   page.wait_for_timeout(70)
   result=page.evaluate("""id=>{let c=document.getElementById(id),n=document.querySelector('.chapter-navigation').getBoundingClientRect();let controls=[...c.querySelectorAll('a[href],button,input,summary')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility==='visible'&&!e.closest('[hidden]'));let overlaps=controls.filter(e=>{let r=e.getBoundingClientRect();return r.bottom>n.top&&r.top<n.bottom&&r.right>n.left&&r.left<n.right}).map(e=>e.textContent.trim().slice(0,50));return {id,scroll:c.scrollHeight-c.clientHeight,horizontal:c.scrollWidth-c.clientWidth,active:ChapterNavigation.activeId,overlaps}}""",id)
   print('CHAPTER',w,h,json.dumps(result),flush=True)
   if result['scroll']>2 or result['horizontal']>2 or result['active']!=id or result['overlaps']:failures.append((w,h,result))
  page.evaluate("ChapterNavigation.selectId('ux',{instant:true})")
  page.wait_for_timeout(100)
  if (w,h) in [(320,568),(390,844),(844,390),(1440,900)]:
   s=base64.b64encode(page.screenshot(type='jpeg',quality=45,animations='disabled')).decode()
   for i in range(0,len(s),10000):print('VISUAL',f'{w}x{h}_ux',i//10000,s[i:i+10000],flush=True)
  for id in ['fishing','easy','house','wine']:
   page.locator(f'[data-ux-case="{id}"]').click(timeout=3000)
   assert page.locator('#ux-dialog').evaluate('d=>d.open')
   panel=page.locator(f'[data-ux-panel="{id}"]')
   assert panel.is_visible()
   assert panel.locator('.ux-fact').count()==4
   for img in panel.locator('img').all():
    img.evaluate("i=>{i.loading='eager'}")
    img.evaluate("i=>i.decode()")
   if page.locator('#ux-dialog').evaluate('d=>d.scrollWidth-d.clientWidth')>2:failures.append((w,h,id,'dialog overflow'))
   if (w,h,id) in [(390,844,'easy'),(1440,900,'house')]:
    s=base64.b64encode(page.screenshot(type='jpeg',quality=45,animations='disabled')).decode()
    for i in range(0,len(s),10000):print('VISUAL',f'{w}x{h}_{id}',i//10000,s[i:i+10000],flush=True)
   page.locator('#ux-close').click()
   assert not page.locator('#ux-dialog').evaluate('d=>d.open')
   assert page.evaluate('ChapterNavigation.activeId')=='ux'
  page.mouse.move(w//2,h//2);page.mouse.wheel(0,500);page.wait_for_timeout(250)
  if page.evaluate('ChapterNavigation.activeId')!='headliners':failures.append((w,h,'wheel from UX'))
  if errors:failures.append((w,h,errors))
  page.close()
 b.close()
print('FINAL',json.dumps(failures),flush=True)
assert not failures, failures
