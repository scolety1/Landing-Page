import json, shutil, base64, time
from playwright.sync_api import sync_playwright
from urllib.request import urlopen
for _ in range(20):
 try: urlopen('http://127.0.0.1:8765/').close();break
 except Exception: time.sleep(.3)
sizes=[(320,480,True),(320,568,True),(360,560,True),(360,640,True),(375,620,True),(390,650,True),(390,670,True),(390,700,True),(390,730,True),(390,760,True),(390,844,True),(393,656,True),(414,660,True),(414,896,True),(430,750,True),(768,1024,True),(844,390,True),(1024,600,False),(1280,720,False),(1440,900,False)]
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
   page.wait_for_timeout(85)
   result=page.evaluate("""id=>{let c=document.getElementById(id),n=document.querySelector('.chapter-navigation').getBoundingClientRect();let controls=[...c.querySelectorAll('a[href],button,input,summary')].filter(e=>e.getClientRects().length&&getComputedStyle(e).visibility==='visible'&&!e.closest('[hidden]'));let overlaps=controls.filter(e=>{let r=e.getBoundingClientRect();return r.bottom>n.top&&r.top<n.bottom&&r.right>n.left&&r.left<n.right}).map(e=>e.textContent.trim().slice(0,50));return {id,scroll:c.scrollHeight-c.clientHeight,horizontal:c.scrollWidth-c.clientWidth,active:ChapterNavigation.activeId,fit:c.classList.contains('fit-ready'),bounds:(()=>{let i=c.querySelector('.chapter-inner'),r=i.getBoundingClientRect(),st=getComputedStyle(i);return {top:Math.round(r.top+parseFloat(st.paddingTop)),bottom:Math.round(r.bottom-parseFloat(st.paddingBottom)),header:Math.round(document.querySelector('.site-header').getBoundingClientRect().bottom),nav:Math.round(n.top)}})(),compact:c.classList.contains('fit-compact'),tight:c.classList.contains('fit-tight'),overlaps}}""",id)
   print('CHAPTER',w,h,json.dumps(result),flush=True)
   if result['scroll']>2 or result['horizontal']>2 or result['active']!=id or result['overlaps'] or not result['fit']:failures.append((w,h,result))
  page.evaluate("ChapterNavigation.selectId('ux',{instant:true})")
  page.wait_for_timeout(100)
  if (w,h) in [(320,480),(390,650),(390,844),(844,390),(1440,900)]:
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
  if (w,h) in [(390,650),(393,656),(390,844),(320,568)]:
   page.evaluate("ChapterNavigation.selectId('development',{instant:true})");page.wait_for_timeout(100)
   session=page.context.new_cdp_session(page)
   def swipe():
    x=w//2; start=h-100; end=130
    session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':start}]})
    for step in range(1,9):
     session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':start+(end-start)*step/8}]})
     page.wait_for_timeout(20)
    session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    page.wait_for_timeout(550)
   swipe()
   got=page.evaluate('ChapterNavigation.activeId')
   print('NATIVE_SWIPE',w,h,got,flush=True)
   if got!='ux':failures.append((w,h,'native swipe development',got))
   if got=='ux':
    swipe()
    if page.evaluate('ChapterNavigation.activeId')!='headliners':failures.append((w,h,'native swipe UX',page.evaluate('ChapterNavigation.activeId')))
   page.evaluate("ChapterNavigation.selectId('development',{instant:true})")
   page.set_viewport_size({'width':w,'height':h-50});page.wait_for_timeout(150)
   r=page.evaluate("()=>{let c=document.querySelector('.chapter-active');return {id:c.id,scroll:c.scrollHeight-c.clientHeight,fit:c.classList.contains('fit-ready')}}")
   print('CHROME_RESIZE',w,h,json.dumps(r),flush=True)
   if r['scroll']>2 or not r['fit']:failures.append((w,h,'chrome resize',r))
  page.close()
 b.close()
print('FINAL',json.dumps(failures),flush=True)
assert not failures, failures
