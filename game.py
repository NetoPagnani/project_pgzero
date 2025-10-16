import os,random
try:
    from pgzero.builtins import screen, sounds, music, keyboard, keys, images
except Exception:
    pass
from pgzero.rect import Rect

WIDTH,HEIGHT=800,480
TITLE="Quadrado em Fuga"
VOL=0.01

state={"menu":True,"victory":False,"dead":False,"dt":0,"music_on":True,"track":"bg_loop","watch":None,"mtime":None}

class P:
    def __init__(self):
        self.w,self.h=28,32; self.x,self.y=80,HEIGHT-100; self.vx=self.vy=0; self.on=False; self.jump=0; self.prev_y=self.y
    def r(self):
        return Rect(int(self.x-self.w/2),int(self.y-self.h/2),self.w,self.h)
    def upd(self,dt,plats):
        ax=(-1 if (keyboard.left or keyboard.a) else 0)+(1 if (keyboard.right or keyboard.d) else 0)
        self.vx=ax*200
        if (keyboard.space or keyboard.up or keyboard.w) and (self.on or self.jump<2):
            self.vy=-450; self.on=False; self.jump+=1
            try: sounds.jump.play()
            except: pass
        self.prev_y=self.y
        self.vy+=800*dt; self.x+=self.vx*dt; self.y+=self.vy*dt
        self.on=False; p=self.r()
        for plat in plats:
            if p.colliderect(plat):
                if self.vy>0 and (p.bottom-plat.top)<40:
                    self.y=plat.top-self.h/2; self.vy=0; self.on=True; self.jump=0; p=self.r(); break
                elif self.vy<0 and (plat.bottom-p.top)<40:
                    self.y=plat.bottom+self.h/2; self.vy=0; p=self.r()

class E:
    def __init__(self,x,y,a,b):
        self.x,self.y=x,y; self.vx=random.choice([-80,80]); self.a,self.b=a,b; self.w,self.h=28,32
    def r(self):
        return Rect(int(self.x-self.w/2),int(self.y-self.h/2),self.w,self.h)
    def upd(self,dt):
        self.x+=self.vx*dt
        if self.x<self.a: self.x=self.a; self.vx*=-1
        if self.x>self.b: self.x=self.b; self.vx*=-1

def gen():
    global plats,spikes,enemies,flag,dz,player
    plats=[]; spikes=[]; dz=[]
    floor=Rect(0,HEIGHT-32,WIDTH,32); plats.append(floor)
    plats+= [Rect(100,360,200,32),Rect(350,280,180,32),Rect(580,200,200,32)]
    player=P()
    enemies=[E(200,360-16,100,300),E(440,280-16,350,530),E(680,200-16,580,780)]
    flag=(750,200)
    for hp in [plats[2],plats[3]]:
        h=max(0,floor.top-(hp.y+hp.height))
        if h>0: dz.append(Rect(hp.x,hp.y+hp.height,hp.width,h))
    for x in range(350,WIDTH,32): spikes.append(Rect(x,HEIGHT-16,32,16))

def play_music():
    if not state["music_on"]:
        try: music.stop()
        except: pass
        state.update({"watch":None,"mtime":None}); return
    try: music.stop()
    except: pass
    base=os.path.dirname(__file__); name=None; path=None
    for n in [state["track"],"bg_loop","bg","music","theme","background","track","main_theme"]:
        for ext in (".ogg",".wav",".mp3"):
            p=os.path.join(base,"music",f"{n}{ext}")
            if os.path.exists(p): name,path=n,p; break
        if name: break
    if not name:
        try:
            files=sorted(os.listdir(os.path.join(base,"music")))
            for f in files:
                if f.lower().endswith((".ogg",".wav",".mp3")):
                    name=os.path.splitext(f)[0]; path=os.path.join(base,"music",f); break
        except: pass
    if name:
        try: music.set_volume(VOL)
        except: pass
        try: music.play_once(name)
        except: pass
        state["track"]=name; state["watch"]=path
        try: state["mtime"]=os.path.getmtime(path)
        except: state["mtime"]=None
    else:
        if hasattr(sounds,"bg_loop"):
            try: sounds.bg_loop.set_volume(VOL)
            except: pass
            try: sounds.bg_loop.play()
            except: pass
            for ext in (".ogg",".wav",".mp3"):
                p=os.path.join(base,"sounds",f"bg_loop{ext}")
                if os.path.exists(p):
                    state["watch"]=p
                    try: state["mtime"]=os.path.getmtime(p)
                    except: state["mtime"]=None
                    break

def poll_music():
    p=state.get("watch")
    if not p or not os.path.exists(p): return
    try: m=os.path.getmtime(p)
    except: return
    if state.get("mtime") is None or m>state["mtime"]+0.001:
        state["mtime"]=m
        try: music.stop()
        except: pass
        t=state.get("track")
        if t:
            try:
                music.play_once(t)
                try: music.set_volume(VOL)
                except: pass
                return
            except: pass
        play_music()

def draw():
    screen.clear()
    for plat in plats: screen.draw.filled_rect(plat,(120,80,40))
    spans=[]
    for r in dz:
        sx=max(0,r.x-2); ex=min(WIDTH,r.x+r.width+2)
        if ex>sx: spans.append((sx,ex))
    if spans:
        mn=min(s for s,_ in spans); mx=max(e for _,e in spans)
        rect=Rect(mn,HEIGHT-32,mx-mn,32)
        screen.draw.filled_rect(rect,(40,120,220))
        y=HEIGHT-32+3
        for i in range(mn,mx,10): screen.draw.line((i,y),(i+6,y-3),(210,230,255))
    for e in enemies: screen.draw.filled_rect(e.r(),(200,50,50))
    # Hero: usa sprite se existir, senão fallback retângulo
    if hasattr(images,"hero_idle_0"):
        img=getattr(images,"hero_idle_0"); dx=int(player.x-img.get_width()/2); dy=int(player.y+player.h/2-img.get_height()); screen.blit("hero_idle_0",(dx,dy))
    else:
        screen.draw.filled_rect(player.r(),(80,160,240))
    for s in spikes:
        screen.draw.filled_rect(s,(150,0,0))
        for i in range(0,s.width,8): screen.draw.line((s.x+i,s.y+s.height),(s.x+i+4,s.y),(200,0,0))
    fx,fy=flag; screen.draw.line((fx,fy),(fx,fy-40),(139,69,19)); screen.draw.filled_rect(Rect(fx+2,fy-40,25,15),(255,0,0))
    if state["menu"]: screen.draw.textbox("Quadrado em Fuga\nClick START",Rect(WIDTH//2-120,HEIGHT//2-60,240,120))
    if state["victory"]: screen.draw.textbox("PARABENS!\nClique para reiniciar",Rect(WIDTH//2-140,HEIGHT//2-70,280,140))

def die():
    state["dead"]=True; state["dt"]=1.0
    try: sounds.hit.play()
    except: pass

def reset_player():
    player.x,player.y=80,HEIGHT-100; player.vx=player.vy=0; player.on=False; player.jump=0

def update(dt):
    poll_music()
    if state["menu"] or state["victory"]: return
    if state["dead"]:
        state["dt"]-=dt
        if state["dt"]<=0: state["dead"]=False; reset_player()
        return
    player.upd(dt,plats)
    for r in dz:
        if player.r().colliderect(r): die(); return
    fx,fy=flag
    if player.r().colliderect(Rect(fx-5,fy-40,30,40)): state["victory"]=True; return
    if player.y>HEIGHT: die(); return
    for s in spikes:
        if player.r().colliderect(s): die(); return
    for e in list(enemies):
        e.upd(dt)
        if player.r().colliderect(e.r()):
            prev=player.prev_y+player.h/2
            if player.vy>0 and prev<=e.r().top+3:
                try: enemies.remove(e)
                except: pass
                try: sounds.hit.play()
                except: pass
                player.vy=-280
            else:
                die(); return

def on_mouse_down(pos):
    if state["victory"]: gen(); state["victory"]=False; return
    if state["menu"]:
        x,y=pos
        start=Rect(WIDTH//2-110,HEIGHT//2+10,220,36)
        if start.collidepoint(x,y):
            state["menu"]=False
            if state["music_on"]: play_music()

def on_key_down(key):
    if state["victory"]: gen(); state["victory"]=False; return
    if state["menu"]:
        state["menu"]=False
        if state["music_on"]: play_music()
        return
    if key==keys.M:
        state["music_on"]=not state["music_on"]
        if state["music_on"]: play_music()
        else:
            try: music.stop()
            except: pass
    if key==keys.R: play_music()

gen()
if state.get("music_on",True): play_music()
