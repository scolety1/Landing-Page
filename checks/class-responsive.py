import json, time, shutil
from playwright.sync_api import sync_playwright
from urllib.request import urlopen
for _ in range(20):
    try:
        urlopen('http://127.0.0.1:8765/', timeout=1).close()
        break
    except Exception: time.sleep(.5)
sizes=[(320,568),(360,640),(390,844),(414,896),(768,1024),(844,390),(1024,600),(1280,720),(1440,900)]
with sync_playwright() as p:
    exe=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
    assert exe, 'Installed Chrome not found'
    browser=p.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox'])
    report=[]
    for width,height in sizes:
        page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        for route in ['/','/design/']:
            response=page.goto('http://127.0.0.1:8765'+route,wait_until='load',timeout=20000)
            page.wait_for_timeout(150)
            data=page.evaluate("""() => ({width:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth,overflow:Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-innerWidth,broken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')).filter(x=>x&&!x.startsWith('data:')),title:document.title})""")
            if route=='/design/':
                for image in page.locator('.evidence-shot img').all():
                    image.scroll_into_view_if_needed()
                    image.evaluate("(i)=>{i.loading='eager'}")
                    image.evaluate("(i)=>i.decode()")
                data['comparisonImages']=page.locator('.evidence-shot img').count()
                data['keyCards']=page.locator('.key-card').count()
                data['comparisonColumns']=page.locator('.evidence-grid.matched').first.evaluate("e=>getComputedStyle(e).gridTemplateColumns")
                data['navLinks']=page.locator('nav a').evaluate_all("els=>els.map(e=>({label:e.textContent,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))")
                data['missingAnchors']=page.locator('a[href^="#"]').evaluate_all("els=>els.map(e=>e.getAttribute('href')).filter(h=>h.length>1&&!document.querySelector(h))")
                for section in ['#key-projects','#fishing','#easylife','#houseos','#wine','#portfolio']:
                    page.locator(section).scroll_into_view_if_needed()
                    assert page.locator(section).is_visible(),section
            else:
                data['designLink']=page.locator('a[href="/design/"]').count()
            data['http']=response.status
            data['errors']=list(errors)
            errors.clear()
            report.append({'viewport':f'{width}x{height}','route':route,**data})
            print('RESPONSIVE',json.dumps(report[-1]),flush=True)
        page.close()
    browser.close()
    failures=[r for r in report if r['overflow']>1 or r['http']!=200 or r['errors'] or r['broken'] or r.get('missingAnchors') or (r['route']=='/design/' and (r.get('comparisonImages')!=4 or r.get('keyCards')!=4))]
    print('SUMMARY',json.dumps({'checks':len(report),'failures':failures}),flush=True)
    assert not failures, 'Responsive QA failures; see summary'
