"""Play-test bot for Spooky House Rescue.
1) Follows the game's own hints from start to finish at every level (wrong answer first, then right).
2) Random-tap runs: many random taps and answers, then follows hints; the game must still be winnable.
3) Sound: every tune lines up, each room plays its music, taps make sounds.
4) Real clicks on the canvas walk the characters and trigger things.  5) Save and continue.
Usage: python3 tests/run.py [chrome path]"""
import sys, os, glob
from playwright.sync_api import sync_playwright
CH=(sys.argv[1] if len(sys.argv)>1 and sys.argv[1] else (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or ['/usr/bin/google-chrome'])[0])
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL='file://'+ROOT+'/index.html'
JS="""
window.ansRight=function(wrongFirst){ const A=__SH; if(!A.quiz) return 0; const ok=A.quiz.opts.findIndex(o=>o.ok); if(wrongFirst){ if(A.answer((ok+1)%3)!==false) throw 'wrong answer accepted'; } if(A.answer(ok)!==true) throw 'right answer refused'; return 1; };
window.follow=function(mode,max,wrongFirst){ const A=__SH; let n=0,q=0;
  while(!A.s.won&&n<max){ n++; const h=A.hint(); if(!h) return {fail:'no hint',room:A.s.room,f:A.s.f,n};
    if(h.inv){ A.hold(h.inv); continue; }
    if(!A.act(h.id)) return {fail:'hint not tappable '+h.id,room:A.s.room};
    q+=ansRight(wrongFirst); }
  return {won:A.s.won,stars:A.s.stars,right:A.s.right,steps:n,q,inv:A.s.inv}; };
window.fuzz=function(mode,seed,taps){ const A=__SH; let r=seed; const rnd=()=>{ r=(r*1103515245+12345)&0x7fffffff; return r/0x7fffffff; };
  A.begin(A.fresh('d',mode));
  for(let i=0;i<taps;i++){ if(A.s.won) break; if(A.quiz){ A.answer(Math.floor(rnd()*3)); continue; }
    if(rnd()<.3&&A.s.inv.length){ A.hold(rnd()<.2?null:A.s.inv[Math.floor(rnd()*A.s.inv.length)]); continue; }
    const hs=A.ROOMS[A.s.room].hs; A.act(hs[Math.floor(rnd()*hs.length)].id); }
  if(A.quiz) ansRight(false);
  return follow(mode,400,false); };
0
"""
fails=0
def check(name,ok,info=''):
    global fails
    print(('PASS ' if ok else 'FAIL ')+name,info)
    if not ok: fails+=1
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1100,'height':700}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text and 'ERR_INTERNET' not in m.text and 'ERR_NAME' not in m.text else None)
    pg.goto(URL); pg.wait_for_timeout(400); pg.evaluate(JS)
    for mode in ['little','kid','adult']:
        pg.evaluate("m=>__SH.begin(__SH.fresh('k',m))",mode)
        r=pg.evaluate("m=>follow(m,400,true)",mode)
        check('full playthrough '+mode, r.get('won') and r['stars']==15 and r['right']==8 and r['inv']==['lantern'], r)
        for k in range(3):
            pg.evaluate("for(const k in __SH.s) 0")
        bank=pg.evaluate("m=>__SH.QUIZ[m].every(q=>q.length>=4&&new Set(q.slice(1,4)).size===3)",mode)
        check('question bank '+mode, bank)
    check('every tune: voices are the same length', pg.evaluate("Object.values(__SH.TRACKS).every(tr=>new Set(tr.v.map(v=>v[2].reduce((a,n)=>a+n[1],0))).size===1)"))
    check('win music plays at the end', pg.evaluate("__SH.music")=='win')
    pg.evaluate("__SH.begin(__SH.fresh('k','little'))"); check('yard music', pg.evaluate("__SH.music")=='title')
    n0=pg.evaluate("__SH.sfxCount"); pg.evaluate("__SH.act('owl')"); check('tapping the owl makes a sound', pg.evaluate("__SH.sfxCount")==n0+1)
    seen=pg.evaluate("""(()=>{ const A=__SH, m={}; let n=0; while(!A.s.won&&n++<400){ const h=A.hint(); if(h.inv){ A.hold(h.inv); continue; } A.act(h.id); ansRight(false); m[A.s.room]=A.music; } return m; })()""")
    check('each room has its music', seen.get('hall')=='sneak' and seen.get('cellar')=='creep' and seen.get('bedroom')=='tiptoe' and seen.get('attic')=='win', seen)
    bad=[]
    for mode in ['little','kid','adult']:
        for seed in range(1,61):
            r=pg.evaluate("([m,s])=>fuzz(m,s,300)",[mode,seed])
            if not (r.get('won') and r['stars']==15): bad.append((mode,seed,r))
    check('180 random-tap runs still winnable', not bad, bad[:2])
    # real clicks
    pg.evaluate("__SH.begin(__SH.fresh('k','little'))")
    box=pg.locator('#cv').bounding_box()
    def click(x,y):
        pg.mouse.click(box['x']+x/960*box['width'], box['y']+y/540*box['height']); pg.wait_for_timeout(2600)
    click(590,385); check('real tap picks up the key', pg.evaluate("__SH.s.inv.includes('goldkey')"))
    click(700,350); check('real tap on door opens a question', pg.evaluate("!!__SH.quiz"))
    ok=pg.evaluate("__SH.quiz.opts.findIndex(o=>o.ok)"); pg.click('#quiz-%d'%ok); pg.wait_for_timeout(200)
    check('answer button unlocks the door', pg.evaluate("!!__SH.s.f.doorOpen"))
    click(700,350); check('real tap walks into the hall', pg.evaluate("__SH.s.room")=='hall')
    pg.reload(); pg.wait_for_timeout(400)
    check('Keep playing button appears', pg.is_visible('#bCont')); pg.click('#bCont'); pg.wait_for_timeout(200)
    check('save restored', pg.evaluate("__SH.s.room")=='hall' and pg.evaluate("__SH.s.stars")==2)
    check('no page errors', not errs, errs[:3])
    if len(sys.argv)>2:
        out=sys.argv[2]; os.makedirs(out,exist_ok=True); pg.evaluate(JS)
        pg.evaluate("__SH.begin(__SH.fresh('k','little'))"); pg.wait_for_timeout(300); pg.screenshot(path=out+'/yard.png')
        n=0
        while not pg.evaluate("__SH.s.won"):
            h=pg.evaluate("__SH.hint()"); room=pg.evaluate("__SH.s.room")
            pg.evaluate("id=>__SH.act(id)",h['id'])
            if pg.evaluate("!!__SH.quiz"):
                if n==0: pg.wait_for_timeout(200); pg.screenshot(path=out+'/quiz.png')
                n+=1; pg.evaluate("ansRight(false)")
            r2=pg.evaluate("__SH.s.room")
            if r2!=room or pg.evaluate("__SH.s.won"): pg.wait_for_timeout(700); pg.screenshot(path=out+'/%s_%d.png'%(r2,pg.evaluate("__SH.s.stars")))
        pg.set_viewport_size({'width':780,'height':360}); pg.wait_for_timeout(300); pg.screenshot(path=out+'/phone_landscape.png')
        pg.evaluate("document.getElementById('bHome').click()"); pg.wait_for_timeout(200); pg.screenshot(path=out+'/title_phone.png')
    b.close()
print('ALL PASS' if not fails else '%d FAILED'%fails); sys.exit(1 if fails else 0)
