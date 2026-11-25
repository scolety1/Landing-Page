import json, shutil, base64
from playwright.sync_api import sync_playwright
sizes=[(320,568,True),(360,640,True),(390,844,True),(414,896,True),(768,1024,True),(844,390,True),(1024,600,False),(1280,720,False),(1440,900,False)]
ids=['top','story','development','headliners','playground','collection','world','future']
url='https://spencercolety.com/'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 for w,h,touch in sizes:
  page=b.new_page(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,reduced_motion='reduce',device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  response=page.goto(url,wait_until='load',timeout=25000)
  page.wait_for_function('window.ChapterNavigation')
  auto=page.evaluate('ChapterNavigation.guided')
  if not auto: page.locator('#scroll-mode').click()
  page.wait_for_timeout(80)
  print('VIEW',json.dumps({'size':f'{w}x{h}','http':response.status,'url':page.url,'auto':auto,'guided':page.evaluate('ChapterNavigation.guided'),'width':page.evaluate('innerWidth')}),flush=True)
  for id in ids:
   page.locator('#chapter-menu-toggle').click()
   menu=page.locator('#chapter-menu').bounding_box()
   page.locator('[data-chapter-target="'+id+'"]').click()
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
   if (w,h,id) in [(320,568,'collection'),(320,568,'development'),(390,844,'story'),(390,844,'headliners'),(844,390,'collection'),(1024,600,'collection'),(1024,600,'headliners'),(1440,900,'collection')]:
    jpeg=page.screenshot(type='jpeg',quality=40,animations='disabled')
    data=base64.b64encode(jpeg).decode()
    for k in range(0,len(data),10000):print('VISUAL',f'{w}x{h}_{id}',k//10000,data[k:k+10000],flush=True)
  # check boundary navigation forward and reverse using actual wheel / keyboard
  page.locator('#chapter-menu-toggle').click();page.locator('[data-chapter-target="top"]').click()
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
   page.locator('#chapter-menu-toggle').click();page.locator('[data-chapter-target="top"]').click();page.wait_for_timeout(100)
   page.evaluate("""()=>{const e=document.querySelector('#top');e.scrollTop=e.scrollHeight;const t=(y)=>new Touch({identifier:1,target:e,clientX:80,clientY:y});e.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[t(220)],changedTouches:[t(220)]}));e.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[],changedTouches:[t(80)]}))}""")
   page.wait_for_timeout(300);swipe=page.evaluate('ChapterNavigation.activeId')
  page.locator('#scroll-mode').click();page.wait_for_timeout(120)
  continuous=page.evaluate("({guided:ChapterNavigation.guided,overflow:document.documentElement.scrollWidth-innerWidth})")
  print('INPUT',json.dumps({'size':f'{w}x{h}','wheelForward':forward,'wheelBack':backward,'swipe':swipe,'continuous':continuous,'errors':errors}),flush=True)
  page.close()
 b.close()
