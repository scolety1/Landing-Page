import json, shutil, base64, os
from playwright.sync_api import sync_playwright
sizes=[(320,568,True),(360,640,True),(390,844,True),(414,896,True),(768,1024,True),(844,390,True),(1024,600,False),(1280,720,False),(1440,900,False)]
ids=['top','story','development','headliners','playground','collection','world','future']
url=os.environ.get('TEST_URL','https://spencercolety.com/')
failures=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 for w,h,touch in sizes:
  page=b.new_page(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,reduced_motion='reduce',device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  response=page.goto(url,wait_until='load',timeout=25000)
  page.wait_for_function('window.ChapterNavigation')
  assert page.locator('#chapter-next').count()==1, 'Live production has not received the new chapter build'
  auto=page.evaluate('ChapterNavigation.guided')
  if not auto: page.locator('#scroll-mode').click()
  page.wait_for_timeout(80)
  print('VIEW',json.dumps({'size':f'{w}x{h}','http':response.status,'url':page.url,'auto':auto,'guided':page.evaluate('ChapterNavigation.guided'),'width':page.evaluate('innerWidth')}),flush=True)
  for id in ids:
   page.locator('#chapter-menu-toggle').click()
   menu=page.locator('#chapter-menu').bounding_box()
   try: page.locator('[data-chapter-target="'+id+'"]').click(timeout=1800)
   except Exception as exc:
    failures.append((f'{w}x{h}',id,'menu click'));print('MENU_FAIL',json.dumps({'size':f'{w}x{h}','id':id,'error':str(exc)[:500]}),flush=True)
    page.locator('[data-chapter-target="'+id+'"]').evaluate('(e)=>e.click()')
   if not page.locator('#chapter-menu').is_hidden(): page.locator('#chapter-menu-toggle').click()
   page.wait_for_timeout(90)
   r=page.evaluate("""id=>{
    const s=document.getElementById(id),i=s.querySelector('.chapter-inner'),n=document.querySelector('.chapter-navigation'),nr=n.getBoundingClientRect(),sr=s.getBoundingClientRect(),ir=i.getBoundingClientRect();
    const orig=s.scrollTop;s.scrollTop=s.scrollHeight;const max=s.scrollTop;
    const controls=[...s.querySelectorAll('a[href],button,input,select,textarea,summary')].filter(e=>{let r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility==='visible'&&!e.closest('[hidden]')});
    const clipped=controls.filter(e=>{let r=e.getBoundingClientRect();for(let a=e.parentElement;a&&a!==s;a=a.parentElement){let st=getComputedStyle(a);if(/hidden|clip/.test(st.overflowY)){let ar=a.getBoundingClientRect();if(r.bottom>ar.bottom+2||r.top<ar.top-2)return true}}return false}).map(e=>e.textContent.trim().slice(0,55)||e.getAttribute('aria-label')).slice(0,8);
    const bottom=controls.filter(e=>{const r=e.getBoundingClientRect();return r.bottom>nr.top&&r.top<nr.bottom&&r.left<nr.right&&r.right>nr.left}).map(e=>e.textContent.trim().slice(0,55)||e.getAttribute('aria-label')).slice(0,8);
    const below=controls.filter(e=>e.getBoundingClientRect().bottom>sr.bottom+2).map(e=>e.textContent.trim().slice(0,55)||e.getAttribute('aria-label')).slice(0,8);
    s.scrollTop=0;
    return {id,active:ChapterNavigation.activeId,guided:ChapterNavigation.guided,visible:!s.inert&&getComputedStyle(s).visibility==='visible',overflow:s.scrollWidth-s.clientWidth,bodyOverflow:document.documentElement.scrollWidth-innerWidth,scroll:s.scrollHeight-s.clientHeight,max,innerHeight:Math.round(ir.height),menuTop:Math.round(nr.top),clipped,bottom,below,broken:[...s.querySelectorAll('img')].filter(e=>e.complete&&!e.naturalWidth).length};
   }""",id)
   r.update(size=f'{w}x{h}',menuFits=bool(menu and menu['y']>=-1 and menu['x']>=-1 and menu['x']+menu['width']<=w+1))
   print('CHAPTER',json.dumps(r),flush=True)
   if r['scroll']>2 or r['overflow']>2 or r['bodyOverflow']>2 or r['clipped'] or r['bottom'] or r['below'] or not r['menuFits'] or r['active']!=id or not r['visible']: failures.append((f'{w}x{h}',id,{k:r[k] for k in ['scroll','overflow','clipped','bottom','below','menuFits']}))
   if (w,h,id) in [(320,568,'collection'),(320,568,'development'),(390,844,'story'),(390,844,'headliners'),(844,390,'collection'),(1024,600,'collection'),(1024,600,'headliners'),(1440,900,'collection')]:
    jpeg=page.screenshot(type='jpeg',quality=40,animations='disabled')
    data=base64.b64encode(jpeg).decode()
    for k in range(0,len(data),10000):print('VISUAL',f'{w}x{h}_{id}',k//10000,data[k:k+10000],flush=True)
  # Verify every inter-chapter edge without manually scrolling to a chapter boundary.
  for idx,id in enumerate(ids[:-1]):
   page.evaluate("(id)=>ChapterNavigation.selectId(id,{instant:true})",id)
   page.wait_for_timeout(80)
   page.mouse.move(w//2,h//2);page.mouse.wheel(0,500);page.wait_for_timeout(220)
   got=page.evaluate("ChapterNavigation.activeId")
   if got!=ids[idx+1]: failures.append((f'{w}x{h}',id,'wheel to next',got))
  # check boundary navigation forward and reverse using actual wheel / keyboard
  page.locator('#chapter-menu-toggle').click();page.locator('[data-chapter-target="top"]').evaluate('(e)=>e.click()');
  if not page.locator('#chapter-menu').is_hidden(): page.locator('#chapter-menu-toggle').click()
  page.wait_for_timeout(100)
  page.evaluate("document.querySelector('#top').scrollTop=1e7")
  page.mouse.move(w//2,h//2);page.mouse.wheel(0,600);page.wait_for_timeout(300)
  forward=page.evaluate('ChapterNavigation.activeId')
  page.evaluate("document.querySelector('.chapter-active').scrollTop=0")
  page.mouse.wheel(0,-600);page.wait_for_timeout(300)
  backward=page.evaluate('ChapterNavigation.activeId')
  # touch dispatch on chapter surface at bottom, if touch
  swipe=None
  if touch:
   page.locator('#chapter-menu-toggle').click();page.locator('[data-chapter-target="top"]').evaluate('(e)=>e.click()');
   if not page.locator('#chapter-menu').is_hidden(): page.locator('#chapter-menu-toggle').click()
   page.wait_for_timeout(100)
   page.evaluate("""()=>{const e=document.querySelector('#top');e.scrollTop=e.scrollHeight;const t=(y)=>new Touch({identifier:1,target:e,clientX:80,clientY:y});e.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[t(220)],changedTouches:[t(220)]}));e.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[],changedTouches:[t(80)]}))}""")
   page.wait_for_timeout(300);swipe=page.evaluate('ChapterNavigation.activeId')
  page.evaluate("ChapterNavigation.selectId('collection',{instant:true})");page.wait_for_timeout(100)
  count_before=page.locator('#collection-count').inner_text()
  page.locator('#catalog-next').click();page.wait_for_timeout(100)
  count_after=page.locator('#collection-count').inner_text()
  if count_before==count_after or page.evaluate('ChapterNavigation.activeId')!='collection': failures.append((f'{w}x{h}','catalog pagination',count_before,count_after))
  page.locator('#catalog-previous').click()
  page.locator('#scroll-mode').click();page.wait_for_timeout(120)
  continuous=page.evaluate("({guided:ChapterNavigation.guided,overflow:document.documentElement.scrollWidth-innerWidth})")
  print('INPUT',json.dumps({'size':f'{w}x{h}','wheelForward':forward,'wheelBack':backward,'swipe':swipe,'continuous':continuous,'errors':errors}),flush=True)
  if forward!='story' or backward!='top' or (touch and swipe!='story') or continuous['guided'] or errors: failures.append((f'{w}x{h}','input',forward,backward,swipe,errors))
  # Resize a desktop-sized chapter while guided mode is explicitly selected.
  if w==1440:
   if not page.evaluate('ChapterNavigation.guided'): page.locator('#scroll-mode').click()
   page.evaluate("ChapterNavigation.selectId('development',{instant:true})")
   page.set_viewport_size({'width':390,'height':568})
   page.wait_for_timeout(200)
   resize=page.evaluate("""()=>{const c=document.querySelector('.chapter-active');return {guided:ChapterNavigation.guided,id:c.id,scroll:c.scrollHeight-c.clientHeight,overflow:c.scrollWidth-c.clientWidth}}""")
   print('RESIZE',json.dumps(resize),flush=True)
   if not resize['guided'] or resize['id']!='development' or resize['scroll']>2 or resize['overflow']>2: failures.append(('resize',resize))
  page.close()
 b.close()
print('FINAL',json.dumps(failures),flush=True)
assert not failures, failures
