"""Apex Descarga Desktop 0.2 — UI Pro.

Interfaz Tkinter/Pillow independiente del motor. Reutiliza las operaciones, la cola,
la validación de URLs, la persistencia y la gestión de eventos de Desktop 0.1.
"""
from __future__ import annotations

import math
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import webbrowser
import urllib.parse

from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageColor

from .engine import version as engine_version, ffmpeg_path
from .models import THEMES, QUALITIES, display_bytes, display_duration, is_hex_color
from .ui import DesktopApp as LegacyDesktopApp

BG = '#080E19'
NAV = '#0B1322'
SURFACE = '#111D2F'
SURFACE2 = '#16243A'
SURFACE3 = '#1E304A'
OUTLINE = '#263A53'
TEXT = '#F4F7FE'
MUTED = '#9AAEC8'
SOFT = '#7287A3'
GREEN = '#53DDB9'
RED = '#FF8E9F'
AMBER = '#FACF8A'
FONT = 'Segoe UI'


def label(parent, text, size=11, color=TEXT, weight='normal', wrap=None, **kwargs):
    return tk.Label(parent, text=text, bg=parent.cget('bg'), fg=color,
                    font=(FONT, size, weight), justify='left', anchor='w',
                    wraplength=wrap or 0, **kwargs)


def lighten(color, ratio=.12):
    rgb = ImageColor.getrgb(color)
    return '#%02x%02x%02x' % tuple(round(v + (255-v)*ratio) for v in rgb)


def alpha(color, pct):
    base = ImageColor.getrgb(BG)
    top = ImageColor.getrgb(color)
    return '#%02x%02x%02x' % tuple(round(b*(1-pct)+t*pct) for b,t in zip(base,top))


def rounded_image(width, height, background, border=None, radius=18, border_width=1, gradient=None):
    """Raster de tarjeta con curvas reales, fondo degradado y borde de 1px."""
    width, height = max(8, int(width)), max(8, int(height))
    scale = 2
    W, H, radius = width*scale, height*scale, radius*scale
    img = Image.new('RGBA', (W,H))
    if gradient:
        d = ImageDraw.Draw(img)
        start,end = ImageColor.getrgb(gradient[0]),ImageColor.getrgb(gradient[1])
        for y in range(H):
            f=y/max(1,H-1)
            d.line([(0,y),(W,y)],fill=tuple(int(a*(1-f)+b*f) for a,b in zip(start,end))+(255,))
    else:
        ImageDraw.Draw(img).rectangle((0,0,W,H),fill=background)
    mask=Image.new('L',(W,H),0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,W-1,H-1),radius=radius,fill=255)
    img.putalpha(mask)
    if border:
        d=ImageDraw.Draw(img)
        d.rounded_rectangle((scale//2,scale//2,W-scale//2-1,H-scale//2-1),radius=radius,
                            outline=border,width=max(scale,border_width*scale))
    return img.resize((width,height),Image.Resampling.LANCZOS)


class RoundedCard(tk.Frame):
    """Tarjeta de altura natural: evita superposiciones al calcular la geometría.

    El Canvas anterior intentaba redimensionarse desde callbacks de <Configure>.
    Tk podía medirlo antes de que el contenido fuese distribuido por el layout.
    """
    def __init__(self,parent,background=SURFACE,border=OUTLINE,radius=20,pad=22,gradient=None,**kwargs):
        super().__init__(parent,bg=border or background,bd=0,highlightthickness=0,**kwargs)
        self.background=background
        self.inner=tk.Frame(self,bg=background,padx=pad,pady=pad)
        self.inner.pack(fill='both',expand=True,padx=1,pady=1)


def card(parent,pad=22,background=SURFACE,border=OUTLINE,gradient=None):
    obj=RoundedCard(parent,pad=pad,background=background,border=border,gradient=gradient)
    return obj,obj.inner


class PillButton(tk.Canvas):
    """Botón redondeado con hover, foco y rótulo de contraste alto."""
    def __init__(self,parent,text,command,accent='#A16BFA',width=150,height=40,filled=False,disabled=False,icon=None):
        super().__init__(parent,bd=0,highlightthickness=0,bg=parent.cget('bg'),
                         width=width,height=height,cursor='hand2' if not disabled else 'arrow',takefocus=1)
        self.label_text=text if not icon else f'{icon}  {text}'
        self.command=command
        self.accent=accent
        self.filled=filled
        self.disabled=disabled
        self.hover=False
        self._img=None
        self.bind('<Enter>',lambda e:self._hover(True))
        self.bind('<Leave>',lambda e:self._hover(False))
        self.bind('<ButtonRelease-1>',lambda e:self._press())
        self.bind('<Return>',lambda e:self._press())
        self.bind('<space>',lambda e:self._press())
        self._paint()

    def _hover(self,val):
        if not self.disabled:
            self.hover=val
            self._paint()

    def _press(self):
        if not self.disabled:
            self.command()

    def _paint(self):
        w,h=int(self.cget('width')),int(self.cget('height'))
        if self.filled:
            gradient=(self.accent,lighten(self.accent,.23 if self.hover else .15))
            base=self.accent; line=None
        else:
            gradient=None
            base=SURFACE3 if self.hover else SURFACE2
            line=lighten(OUTLINE,.16) if self.hover else OUTLINE
        if self.disabled:base=OUTLINE;gradient=None
        self._img=ImageTk.PhotoImage(rounded_image(w,h,base,border=line,radius=12,gradient=gradient))
        self.delete('all')
        self.create_image(0,0,anchor='nw',image=self._img)
        self.create_text(w//2,h//2,text=self.label_text,fill='#FFFFFF' if self.filled else (SOFT if self.disabled else TEXT),
                         font=(FONT,10,'bold'))


def action(parent,text,fn,width=140,height=40,accent='#A16BFA',filled=False,icon=None,**pack):
    b=PillButton(parent,text,fn,accent,width=width,height=height,filled=filled,icon=icon)
    b.pack(**pack)
    return b


class HeroBanner(tk.Canvas):
    """Cabecera ilustrada por el propio programa con sombras y el isotipo Apex."""
    def __init__(self,parent,accent,asset_path=None):
        super().__init__(parent,height=187,bg=BG,bd=0,highlightthickness=0)
        self.accent=accent
        self.asset_path=asset_path
        self.photo=None
        self._last_width=0
        self.bind('<Configure>',self._resize)

    def _resize(self,e):
        w=max(480,e.width)
        if abs(w-self._last_width)<4:return
        self._last_width=w
        h=187; sc=2; W=w*sc; H=h*sc
        img=Image.new('RGB',(W,H))
        draw=ImageDraw.Draw(img)
        p=ImageColor.getrgb(self.accent)
        for y in range(H):
            f=y/H
            col=(int(19+f*2),int(34+f*5),int(57+f*11))
            draw.line([(0,y),(W,y)],fill=col)
        effects=Image.new('RGBA',(W,H),(0,0,0,0))
        fx=ImageDraw.Draw(effects)
        x=int(W*.84);cy=int(H*.38)
        for i in range(7,0,-1):
            radius=int(24*sc+i*13*sc)
            a=int(15+25*(8-i)/7)
            fx.ellipse((x-radius,cy-radius,x+radius,cy+radius),outline=(*p,a),width=int(sc*1.5))
        glow=Image.new('RGBA',(W,H),(0,0,0,0))
        g=ImageDraw.Draw(glow)
        g.ellipse((int(W*.66),int(-H*.25),int(W*1.13),int(H*.92)),fill=(*p,85))
        glow=glow.filter(ImageFilter.GaussianBlur(45*sc))
        rgba=img.convert('RGBA');rgba=Image.alpha_composite(rgba,glow);rgba=Image.alpha_composite(rgba,effects)
        if self.asset_path and self.asset_path.exists():
            try:
                logo=Image.open(self.asset_path).convert('RGBA');logo.thumbnail((int(130*sc),int(130*sc)),Image.Resampling.LANCZOS)
                rgba.alpha_composite(logo,(int(W*.80)-logo.width//2,int(H*.5)-logo.height//2))
            except OSError:pass
        mask=Image.new('L',(W,H),0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,W-1,H-1),radius=21*sc,fill=255)
        rgba.putalpha(mask)
        self.photo=ImageTk.PhotoImage(rgba.resize((w,h),Image.Resampling.LANCZOS))
        self.delete('all');self.create_image(0,0,anchor='nw',image=self.photo)
        self.create_text(28,27,anchor='nw',text='APEX  /  DESKTOP',font=(FONT,10,'bold'),fill='#76E3F1')
        self.create_text(28,58,anchor='nw',text='Tus medios, a tu manera.',font=(FONT,22,'bold'),fill=TEXT)
        self.create_text(30,105,anchor='nw',text='Descarga, organiza y encuentra tus archivos.',font=(FONT,11),fill='#AFC2DE')
        self.create_text(30,130,anchor='nw',text='Todo desde una aplicación. Sin abrir el navegador.',font=(FONT,10),fill='#AFC2DE')


class DesktopApp(LegacyDesktopApp):
    """Experiencia visual 0.2; delega descargas al coordinador 0.1 sin modificarlo."""
    def __init__(self,engine=None,store=None):
        self._keep_images={}
        super().__init__(engine=engine,store=store)
        self.title('Apex Descarga Desktop 0.2.1 UI Pro — Apex Visual Studio')
        self.geometry('1280x850')
        self.minsize(980,675)

    def _icon_asset(self):
        root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))
        return root/'assets'/'apex_icon.png'

    def _build_shell(self):
        for widget in self.winfo_children():widget.destroy()
        self.configure(bg=BG)
        self.shell=tk.Frame(self,bg=BG)
        self.shell.pack(fill='both',expand=True)
        self.sidebar=tk.Frame(self.shell,bg=NAV,width=246,padx=18,pady=22)
        self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
        self._sidebar_logo()
        sep=tk.Frame(self.sidebar,bg=OUTLINE,height=1)
        sep.pack(fill='x',pady=(25,22))
        label(self.sidebar,'ESPACIO DE TRABAJO',size=9,weight='bold',color=SOFT).pack(anchor='w',padx=13,pady=(0,9))
        self.nav_buttons={}
        icons={'inicio':'⌂','cola':'☷','biblioteca':'▦','ajustes':'⚙','acerca':'ⓘ'}
        names={'inicio':'Inicio','cola':'Descargas','biblioteca':'Biblioteca','ajustes':'Ajustes','acerca':'Acerca de'}
        for key in ('inicio','cola','biblioteca','ajustes','acerca'):
            self._nav_item(key,icons[key],names[key])
        tk.Frame(self.sidebar,bg=NAV).pack(fill='both',expand=True)
        small=card(self.sidebar,pad=14,background='#15243A',border='#203A54')
        small[0].pack(fill='x',pady=(0,15))
        label(small[1],'●  TODO BAJO CONTROL',size=9,color=GREEN,weight='bold').pack(anchor='w')
        label(small[1],'Privado y almacenado en tu PC',size=9,color=MUTED).pack(anchor='w',pady=(7,0))
        label(self.sidebar,'APEX VISUAL STUDIO  ·  v0.2.1',size=9,color=SOFT).pack(anchor='w',padx=11)
        self.content=tk.Frame(self.shell,bg=BG)
        self.content.pack(side='left',fill='both',expand=True)
        self._header()
        self.scroll=self._make_scroller()
        self.scroll.pack(fill='both',expand=True,padx=30)
        self.statusbar=tk.Frame(self.content,bg=NAV,height=46,padx=26)
        self.statusbar.pack(side='bottom',fill='x')
        self.statusbar.pack_propagate(False)
        self.status_text=label(self.statusbar,self._toast,size=9,color=MUTED)
        self.status_text.pack(side='left',fill='x',expand=True,pady=14)
        label(self.statusbar,'DATOS LOCALES     ·     SIN CUENTA',size=9,color=SOFT).pack(side='right',pady=14)
        self._render()

    def _sidebar_logo(self):
        group=tk.Frame(self.sidebar,bg=NAV)
        group.pack(fill='x',pady=(2,4))
        if self.store.settings.get('show_logo',True):
            asset=self._icon_asset()
            if asset.is_file():
                try:
                    im=Image.open(asset).convert('RGBA').resize((57,57),Image.Resampling.LANCZOS)
                    photo=ImageTk.PhotoImage(im)
                    self._keep_images['brand']=photo
                    tk.Label(group,image=photo,bg=NAV).pack(side='left',padx=(2,11))
                except OSError:pass
        txt=tk.Frame(group,bg=NAV)
        txt.pack(side='left',fill='x')
        label(txt,'APEX',size=20,weight='bold').pack(anchor='w')
        label(txt,'D E S C A R G A',size=9,weight='bold',color=self.accent).pack(anchor='w')
        label(txt,'DESKTOP EDITION',size=8,color=SOFT).pack(anchor='w',pady=(4,0))

    def _nav_item(self,key,icon,name):
        active=key==self.page
        cont=tk.Frame(self.sidebar,bg=NAV,height=53)
        cont.pack(fill='x',pady=4);cont.pack_propagate(False)
        color=SURFACE3 if active else NAV
        stripe=tk.Frame(cont,bg=self.accent if active else NAV,width=3)
        stripe.pack(side='left',fill='y',pady=5)
        b=tk.Button(cont,text=f'  {icon}     {name}',bg=color,fg=TEXT if active else MUTED,
                    activebackground=SURFACE3,activeforeground=TEXT,anchor='w',font=(FONT,11,'bold' if active else 'normal'),
                    relief='flat',bd=0,highlightthickness=0,cursor='hand2',command=lambda p=key:self.navigate(p))
        b.pack(fill='both',expand=True,padx=(7,2))
        self.nav_buttons[key]=(cont,stripe,b)

    def _header(self):
        head=tk.Frame(self.content,bg=BG,padx=31,pady=21)
        head.pack(fill='x')
        titles={'inicio':'Inicio','cola':'Gestor de descargas','biblioteca':'Biblioteca multimedia',
                'ajustes':'Personalización','acerca':'Acerca de Apex'}
        left=tk.Frame(head,bg=BG);left.pack(side='left')
        self.page_title=label(left,titles[self.page],size=22,weight='bold')
        self.page_title.pack(anchor='w')
        self.page_subtitle=label(left,'APEX DESCARGA   /   WINDOWS 11',size=9,color=SOFT,weight='bold')
        self.page_subtitle.pack(anchor='w',pady=(4,0))
        right=tk.Frame(head,bg=BG)
        right.pack(side='right',pady=(6,0))
        ffmpeg_ok=ffmpeg_path() is not None
        color=GREEN if engine_version()!='No instalado' else RED
        label(right,'●  yt-dlp '+engine_version(),size=10,color=color,weight='bold').pack(side='left',padx=(0,19))
        label(right,'●  FFmpeg listo' if ffmpeg_ok else '○  FFmpeg pendiente',size=10,color=GREEN if ffmpeg_ok else AMBER).pack(side='left',padx=(0,16))
        # action() ya empaqueta el botón; no añadir un segundo pack.
        action(right,'Abrir carpeta',self._open_folder,width=132,accent=self.accent,icon='↗',side='left')

    def _make_scroller(self):
        from .ui import ScrollBody
        return ScrollBody(self.content)

    def navigate(self,page):
        if page not in ('inicio','cola','biblioteca','ajustes','acerca'):
            return
        self.page=page
        for key,(cont,stripe,b) in self.nav_buttons.items():
            selected=key==page
            stripe.configure(bg=self.accent if selected else NAV)
            b.configure(bg=SURFACE3 if selected else NAV,fg=TEXT if selected else MUTED,
                        font=(FONT,11,'bold' if selected else 'normal'))
        self._render()

    def _render(self):
        titles={'inicio':'Inicio','cola':'Gestor de descargas','biblioteca':'Biblioteca multimedia',
                'ajustes':'Personalización','acerca':'Acerca de Apex'}
        self.scroll.clear()
        self.page_title.configure(text=titles.get(self.page,'Inicio'))
        p=self.scroll.inner
        p.configure(bg=BG)
        if self.page=='inicio':self._home(p)
        elif self.page=='cola':self._queue_page(p)
        elif self.page=='biblioteca':self._library_page(p)
        elif self.page=='ajustes':self._settings(p)
        elif self.page=='acerca':self._about(p)
        self._needs_redraw=False

    def _section(self,parent,heading,subtitle=None,space=13):
        line=tk.Frame(parent,bg=BG)
        line.pack(fill='x',pady=(space,14))
        label(line,heading,size=15,weight='bold').pack(side='left')
        if subtitle:label(line,subtitle,size=9,color=MUTED).pack(side='right',pady=5)
        return line

    def _stats(self,parent):
        active=sum(j.state in ('analizando','descargando','procesando') for j in self.store.jobs)
        waiting=sum(j.state=='pendiente' for j in self.store.jobs)
        completed=sum(j.state=='completado' for j in self.store.jobs)
        boxes=tk.Frame(parent,bg=BG)
        boxes.pack(fill='x',pady=(16,16))
        for i,(number,title,note,col) in enumerate([
            (str(completed),'Completadas','Archivos en biblioteca',GREEN),
            (str(active),'En progreso','Transferencias activas',self.accent),
            (str(waiting),'En espera','Pendientes en cola','#55CEE2'),
        ]):
            boxes.grid_columnconfigure(i,weight=1,uniform='metrics')
            el,c=card(boxes,pad=16,background=SURFACE,border=OUTLINE)
            el.grid(row=0,column=i,sticky='nsew',padx=(0,10) if i<2 else 0)
            label(c,number,size=24,weight='bold',color=col).pack(anchor='w')
            label(c,title,size=11,weight='bold').pack(anchor='w',pady=(1,0))
            label(c,note,size=9,color=MUTED).pack(anchor='w',pady=(3,0))

    def _home(self,parent):
        hero=HeroBanner(parent,self.accent,self._icon_asset() if self.store.settings.get('show_logo',True) else None)
        hero.pack(fill='x',pady=(0,0))
        self._stats(parent)
        self._section(parent,'Nueva descarga','PEGAR  /  ANALIZAR  /  DESCARGAR',space=7)
        columns=tk.Frame(parent,bg=BG)
        columns.pack(fill='x',pady=(0,18))
        columns.grid_columnconfigure(0,weight=11,uniform='home')
        columns.grid_columnconfigure(1,weight=9,uniform='home')
        left,c=card(columns,pad=22)
        left.grid(row=0,column=0,sticky='nsew',padx=(0,12))
        label(c,'ENLACE DEL CONTENIDO',size=9,weight='bold',color=MUTED).pack(anchor='w',pady=(0,10))
        self.link_entry=tk.Entry(c,textvariable=self.url,bg=BG,fg=TEXT,insertbackground=TEXT,
                                 font=(FONT,11),highlightthickness=1,highlightcolor=self.accent,
                                 highlightbackground=OUTLINE,bd=0,relief='flat')
        self.link_entry.pack(fill='x',ipady=13)
        actions=tk.Frame(c,bg=SURFACE);actions.pack(fill='x',pady=(11,18))
        action(actions,'Pegar',self._paste,width=102,accent=self.accent,side='left')
        action(actions,'Analizar',self._probe,width=155,accent=self.accent,filled=True,icon='◇',side='left',padx=9)
        label(c,'FORMATO DE SALIDA',size=9,weight='bold',color=MUTED).pack(anchor='w',pady=(3,10))
        fm=tk.Frame(c,bg=SURFACE)
        fm.pack(fill='x',pady=(0,16))
        for val,text in [('video','▣   Video MP4'),('audio','♫   Audio MP3')]:
            tk.Radiobutton(fm,text=text,variable=self.media_type,value=val,
                           font=(FONT,10,'bold'),fg=TEXT,bg=SURFACE,
                           activeforeground=TEXT,activebackground=SURFACE,selectcolor=BG,
                           indicatoron=0,bd=0,pady=11,padx=16,relief='flat',
                           command=self._switch_format).pack(side='left',padx=(0,9))
        label(c,'CALIDAD PREFERIDA',size=9,weight='bold',color=MUTED).pack(anchor='w',pady=(0,10))
        self.quality_selector=ttk.Combobox(c,textvariable=self.quality,values=QUALITIES,
                    width=22,state='readonly',style='Apex.TCombobox',font=(FONT,10))
        self.quality_selector.pack(fill='x',ipady=7)
        self._switch_format()
        action(c,'AGREGAR A LA COLA',self._add_download,width=238,height=42,accent=self.accent,filled=True,icon='↓',anchor='w',pady=(19,0))
        label(c,'Solo medios propios o autorizados',size=9,color=SOFT).pack(anchor='w',pady=(10,0))

        right,p=card(columns,pad=22,background=SURFACE2,border=OUTLINE)
        right.grid(row=0,column=1,sticky='nsew')
        label(p,'VISTA PREVIA',size=9,weight='bold',color=self.accent).pack(anchor='w',pady=(0,10))
        preview=tk.Frame(p,bg=NAV,height=130)
        preview.pack(fill='x');preview.pack_propagate(False)
        self.preview_art=tk.Label(preview,text='▶',font=(FONT,40,'bold'),fg=self.accent,bg=NAV)
        self.preview_art.pack(fill='both',expand=True)
        pre=self.preview if self.preview and self.preview_url==self.url.get().strip() else None
        if pre and pre.get('thumbnail'):
            self._set_art(self.preview_art,pre['thumbnail'],(285,130))
        ttl=(pre.get('title') or 'Tu siguiente descarga') if pre else 'Tu siguiente descarga'
        label(p,ttl,size=15,weight='bold',wrap=300).pack(anchor='w',pady=(16,8))
        meta=('%s  •  %s'%(pre.get('uploader') or 'Origen',display_duration(pre.get('duration')))) if pre else 'La portada y los detalles aparecerán aquí.'
        label(p,meta,size=10,color=MUTED,wrap=320).pack(anchor='w')
        tk.Frame(p,bg=OUTLINE,height=1).pack(fill='x',pady=(19,15))
        label(p,'COMPROBACIÓN DE ENLACES',size=9,weight='bold',color=GREEN).pack(anchor='w')
        label(p,'Analiza primero para consultar título,\nautor y duración antes de descargar.',size=9,color=MUTED).pack(anchor='w',pady=(7,0))

        self._section(parent,'Actividad reciente','ÚLTIMOS MOVIMIENTOS',space=6)
        latest=list(reversed(self.store.jobs[-2:]))
        if not latest:self._empty(parent,'Todavía no hay descargas. Analiza un enlace para empezar.')
        for job in latest:self._job_card(parent,job)
        if len(self.store.jobs)>2:
            action(parent,'Ver todas las descargas',lambda:self.navigate('cola'),width=230,accent=self.accent,icon='→',pady=(4,18))

    def _queue_page(self,parent):
        self._section(parent,'Estado de transferencias','UNA DESCARGA A LA VEZ',space=10)
        self._stats(parent)
        bar=tk.Frame(parent,bg=BG);bar.pack(fill='x',pady=(5,15))
        for title in ('Todas','Pendientes','Descargando','Completadas','Errores'):
            active=self.filter_status==title
            b=tk.Button(bar,text=title,command=lambda x=title:self._set_filter(x),
                        bg=SURFACE3 if active else SURFACE,fg=self.accent if active else MUTED,
                        activebackground=SURFACE3,activeforeground=TEXT,bd=0,relief='flat',
                        font=(FONT,10,'bold' if active else 'normal'),padx=16,pady=10,cursor='hand2')
            b.pack(side='left',padx=(0,8))
        jobs=list(reversed(self.store.jobs))
        if self.filter_status=='Pendientes':jobs=[j for j in jobs if j.state in ('pendiente','interrumpido')]
        elif self.filter_status=='Descargando':jobs=[j for j in jobs if j.state in ('analizando','descargando','procesando')]
        elif self.filter_status=='Completadas':jobs=[j for j in jobs if j.state=='completado']
        elif self.filter_status=='Errores':jobs=[j for j in jobs if j.state in ('cancelado','error')]
        if not jobs:self._empty(parent,'No hay descargas que mostrar en este filtro.')
        for job in jobs:self._job_card(parent,job)
        if any(j.state in ('completado','cancelado','error','interrumpido') for j in self.store.jobs):
            action(parent,'Limpiar trabajos finalizados',self._clear_finished,width=265,accent=self.accent,pady=(8,18))

    def _clear_finished(self):
        if not messagebox.askyesno('Limpiar historial','Se quitarán los trabajos terminados de la cola y biblioteca.\nLos archivos descargados NO se borrarán.',parent=self):return
        self.store.jobs=[j for j in self.store.jobs if j.state not in ('completado','cancelado','error','interrumpido')]
        self.store.save_jobs();self._say('Historial limpiado, archivos conservados.');self._render()

    def _job_card(self,parent,job,library=False):
        outer,box=card(parent,pad=12 if self.store.settings.get('compact_mode',False) else 17,background=SURFACE,border=OUTLINE)
        outer.pack(fill='x',pady=(0,11))
        r=tk.Frame(box,bg=SURFACE);r.pack(fill='x')
        artbox=tk.Frame(r,bg=NAV,width=114,height=78);artbox.pack(side='left',padx=(0,15));artbox.pack_propagate(False)
        art=tk.Label(artbox,text='♫' if job.kind=='audio' else '▶',bg=NAV,fg=self.accent,font=(FONT,24))
        art.pack(fill='both',expand=True)
        if job.thumbnail:self._set_art(art,job.thumbnail,(110,76))
        info=tk.Frame(r,bg=SURFACE);info.pack(side='left',fill='both',expand=True)
        label(info,job.title[:85],size=12,weight='bold',wrap=410).pack(anchor='w',pady=(0,6))
        format_='MP3' if job.kind=='audio' else job.quality
        label(info,f'{job.uploader or "Enlace multimedia"}   ·   {format_}   ·   {display_duration(job.duration)}',size=9,color=MUTED).pack(anchor='w')
        colors={'completado':GREEN,'descargando':self.accent,'procesando':self.accent,'analizando':self.accent,
                'error':RED,'cancelado':RED,'pendiente':SOFT,'interrumpido':AMBER}
        label(info,'●  '+job.state.upper(),size=9,weight='bold',color=colors.get(job.state,MUTED)).pack(anchor='w',pady=(10,0))
        actions=tk.Frame(r,bg=SURFACE);actions.pack(side='right',padx=(7,0))
        if job.state in ('pendiente','descargando','procesando'):
            action(actions,'Cancelar',lambda j=job:self._cancel(j),width=105,accent=self.accent,pady=(0,5))
        if job.state in ('error','cancelado','interrumpido'):
            action(actions,'Reintentar',lambda j=job:self._retry(j),width=106,accent=self.accent,filled=True,pady=(0,5))
        if job.can_open:
            action(actions,'Abrir archivo',lambda j=job:self._open_file(j),width=115,accent=self.accent,pady=(0,5))
            action(actions,'Carpeta',lambda j=job:self._open_job_folder(j),width=115,accent=self.accent,pady=(0,5))
            if library:action(actions,'Copiar ruta',lambda j=job:self._copy_path(j),width=115,accent=self.accent,pady=(0,5))
        if library:
            action(actions,'Quitar registro',lambda j=job:self._remove_history(j),width=115,accent=self.accent,pady=(0,5))
        if job.state in ('completado','descargando','procesando','analizando'):
            prog=tk.Canvas(box,bg=SURFACE,height=7,highlightthickness=0,bd=0)
            prog.pack(fill='x',pady=(16,7))
            prog.bind('<Configure>',lambda e,p=prog,progress=job.progress:self._bar_draw(p,e.width,progress))
            parts=[f'{job.progress:.0f}%']
            if job.downloaded:parts.append(display_bytes(job.downloaded))
            if job.total:parts.append('de '+display_bytes(job.total))
            if job.speed:parts.append(display_bytes(job.speed)+'/s')
            if job.eta is not None:parts.append('Restante '+display_duration(job.eta))
            label(box,'    ·    '.join(parts),size=9,color=MUTED).pack(anchor='w')
        if job.error and job.state in ('error','interrumpido'):
            label(box,job.error[:175],size=9,color=RED,wrap=650).pack(anchor='w',pady=(10,0))

    def _bar_draw(self,canvas,width,progress):
        canvas.delete('all')
        canvas.create_rectangle(0,0,max(width,1),7,fill=OUTLINE,outline='')
        if progress>0:canvas.create_rectangle(0,0,max(1,width*max(0,min(100,progress))/100),7,fill=self.accent,outline='')

    def _open_job_folder(self,job):
        if not job.file_path:return
        try:
            folder=Path(job.file_path).resolve().parent
            if os.name=='nt':os.startfile(str(folder))
            else:webbrowser.open(folder.as_uri())
        except OSError as e:messagebox.showerror('Carpeta',str(e),parent=self)

    def _copy_path(self,job):
        self.clipboard_clear();self.clipboard_append(job.file_path);self._say('Ruta de archivo copiada.')

    def _remove_history(self,job):
        if job.state!='completado':return
        if not messagebox.askyesno('Quitar del historial','¿Quitar esta entrada de la biblioteca?\nEl archivo permanecerá en el disco.',parent=self):return
        self.store.jobs=[j for j in self.store.jobs if j.id!=job.id]
        self.store.save_jobs();self._say('Registro quitado; archivo conservado.');self._render()

    def _library_page(self,parent):
        self._section(parent,'Todos tus archivos','GUARDADOS LOCALMENTE',space=11)
        query=tk.StringVar(value=self.search_query)
        inp=tk.Entry(parent,textvariable=query,bg=SURFACE,fg=TEXT,insertbackground=TEXT,
                     font=(FONT,11),highlightthickness=1,highlightbackground=OUTLINE,
                     highlightcolor=self.accent,bd=0)
        inp.pack(fill='x',ipady=13,pady=(0,10))
        inp.bind('<Return>',lambda _e:self._search_library(query.get()))
        searchrow=tk.Frame(parent,bg=BG);searchrow.pack(fill='x',pady=(0,15))
        label(searchrow,'⌕  Buscar título o autor y pulsar Enter',size=9,color=MUTED).pack(side='left',pady=11)
        action(searchrow,'Buscar',lambda:self._search_library(query.get()),width=110,accent=self.accent,side='right')
        f=tk.Frame(parent,bg=BG);f.pack(fill='x',pady=(0,12))
        selected=getattr(self,'library_filter','Todos')
        for filterName in ('Todos','Videos','Audio'):
            active=filterName==selected
            b=tk.Button(f,text=filterName,bg=SURFACE3 if active else SURFACE,
                        fg=self.accent if active else MUTED,padx=16,pady=9,font=(FONT,10,'bold' if active else 'normal'),
                        relief='flat',bd=0,cursor='hand2',command=lambda name=filterName:self._filter_library(name))
            b.pack(side='left',padx=(0,8))
        jobs=[j for j in reversed(self.store.jobs) if j.state=='completado']
        if selected=='Videos':jobs=[j for j in jobs if j.kind=='video']
        if selected=='Audio':jobs=[j for j in jobs if j.kind=='audio']
        q=self.search_query.strip().casefold()
        if q:jobs=[j for j in jobs if q in (j.title+' '+j.uploader).casefold()]
        self._section(parent,f'{len(jobs)} archivos','FILTRADOS',space=4)
        if not jobs:self._empty(parent,'No encontramos archivos con ese filtro.')
        for j in jobs:self._job_card(parent,j,library=True)
        action(parent,'Abrir carpeta de descargas',self._open_folder,width=260,accent=self.accent,pady=(6,22))

    def _search_library(self,query):
        self.search_query=query
        self._render()

    def _filter_library(self,name):
        self.library_filter=name
        self._render()

    def _settings(self,parent):
        self._section(parent,'Personaliza la experiencia','CAMBIOS GUARDADOS EN ESTE EQUIPO',space=12)
        box,p=card(parent);box.pack(fill='x',pady=(0,15))
        label(p,'APARIENCIA',size=10,weight='bold',color=self.accent).pack(anchor='w',pady=(0,12))
        label(p,'Elige tu color de identidad',size=15,weight='bold').pack(anchor='w')
        row=tk.Frame(p,bg=SURFACE);row.pack(fill='x',pady=(13,13))
        for name,color in THEMES.items():
            b=tk.Button(row,text='●   '+name,font=(FONT,9,'bold'),fg=color,
                        bg=SURFACE3 if self.store.settings['theme']==name else SURFACE2,
                        activebackground=SURFACE3,activeforeground=color,
                        relief='flat',bd=0,padx=12,pady=10,cursor='hand2',
                        command=lambda c=color,n=name:self._change_theme(n,c))
            b.pack(side='left',padx=(0,8))
        picker=tk.Frame(p,bg=SURFACE);picker.pack(fill='x',pady=(0,9))
        label(picker,'Color HEX',size=10,color=MUTED).pack(side='left',padx=(0,11))
        self.hex_value=tk.StringVar(value=self.accent)
        ent=tk.Entry(picker,textvariable=self.hex_value,width=12,font=(FONT,11),bg=BG,fg=TEXT,
                     insertbackground=TEXT,bd=0,highlightthickness=1,
                     highlightbackground=OUTLINE,highlightcolor=self.accent)
        ent.pack(side='left',ipady=9)
        action(picker,'Aplicar',self._custom_hex,width=100,accent=self.accent,filled=True,side='left',padx=10)
        self.logo_value=tk.BooleanVar(value=self.store.settings.get('show_logo',True))
        tk.Checkbutton(p,text='Mostrar logotipo en la barra lateral',variable=self.logo_value,
                       bg=SURFACE,fg=TEXT,activebackground=SURFACE,activeforeground=TEXT,
                       selectcolor=BG,font=(FONT,10),command=self._set_logo).pack(anchor='w',pady=(12,0))
        self.compact_value=tk.BooleanVar(value=self.store.settings.get('compact_mode',False))
        tk.Checkbutton(p,text='Modo compacto (tarjetas más juntas)',variable=self.compact_value,
                       bg=SURFACE,fg=TEXT,activebackground=SURFACE,activeforeground=TEXT,
                       selectcolor=BG,font=(FONT,10),command=self._set_compact).pack(anchor='w',pady=(5,0))

        box,p=card(parent);box.pack(fill='x',pady=(0,15))
        label(p,'DESCARGAS Y ALMACENAMIENTO',size=10,weight='bold',color=self.accent).pack(anchor='w')
        label(p,'Carpeta de destino',size=14,weight='bold').pack(anchor='w',pady=(13,5))
        label(p,str(self.store.folder()),size=10,color=MUTED,wrap=660).pack(anchor='w',pady=(0,15))
        row=tk.Frame(p,bg=SURFACE);row.pack(fill='x')
        action(row,'Cambiar carpeta',self._choose_folder,width=160,accent=self.accent,side='left')
        action(row,'Abrir carpeta',self._open_folder,width=150,accent=self.accent,side='left',padx=9)
        label(p,'La cola se procesa de forma secuencial para reducir consumo.',size=9,color=SOFT).pack(anchor='w',pady=(14,0))

        box,p=card(parent);box.pack(fill='x',pady=(0,15))
        label(p,'MOTOR Y DIAGNÓSTICO',size=10,weight='bold',color=self.accent).pack(anchor='w')
        label(p,'yt-dlp    '+engine_version(),size=12,weight='bold').pack(anchor='w',pady=(12,5))
        present=ffmpeg_path() is not None
        label(p,'● FFmpeg detectado' if present else '○ FFmpeg no detectado — requerido para MP3 y unir video',size=10,
              color=GREEN if present else AMBER).pack(anchor='w',pady=(2,12))
        label(p,'Al actualizar el código fuente, vuelve a ejecutar INICIAR_APEX.cmd.\nEl .exe usa la versión incluida durante su compilación.',
              size=10,color=MUTED,wrap=680).pack(anchor='w')

        box,p=card(parent);box.pack(fill='x',pady=(0,18))
        label(p,'PRIVACIDAD Y SOPORTE',size=10,weight='bold',color=self.accent).pack(anchor='w')
        label(p,'Los enlaces se procesan localmente. El proveedor de cada enlace recibe las\nsolicitudes de yt-dlp. Apex no requiere cuenta ni envía telemetría propia.',size=10,color=MUTED).pack(anchor='w',pady=(12,12))
        row=tk.Frame(p,bg=SURFACE);row.pack(fill='x')
        action(row,'Copiar correo de soporte',self._copy_support,width=200,accent=self.accent,side='left')
        action(row,'Ver GitHub',lambda:webbrowser.open('https://github.com/Sombra-789/apex-descarga'),width=128,accent=self.accent,side='left',padx=9)

    def _set_compact(self):
        self.store.settings['compact_mode']=bool(self.compact_value.get())
        self.store.save_settings();self._say('Preferencia de diseño guardada.');self._render()

    def _copy_support(self):
        self.clipboard_clear();self.clipboard_append('angelrlpz030207@gmail.com');self._say('Correo copiado al portapapeles.')

    def _write_support(self):
        """Intenta abrir cliente de correo; si falta, copia el correo y avisa."""
        mail='angelrlpz030207@gmail.com'
        params=urllib.parse.urlencode({
            'subject':'Apex Descarga Desktop — Reporte o sugerencia',
            'body':'Versión: 0.2.1 UI Pro\nWindows: 11\n\nDescripción del problema o sugerencia:\n',
        })
        link='mailto:'+mail+'?'+params
        try:
            if os.name=='nt':
                os.startfile(link)
                self._say('Abriendo aplicación de correo...')
                return
            if webbrowser.open(link):
                self._say('Abriendo correo...')
                return
        except (OSError,ValueError,RuntimeError):
            pass
        self.clipboard_clear()
        self.clipboard_append(mail)
        self.update()
        messagebox.showinfo('Sin aplicación de correo',
            'Windows no tiene una aplicación de correo asociada o no pudo abrirla.\n\n'
            'El correo se copió al portapapeles:\n'+mail+'\n\n'
            'Puedes pegarlo en Gmail, Outlook o tu servicio preferido.',parent=self)
        self._say('Correo de soporte copiado; abre Gmail o Outlook.')

    def _about(self,parent):
        box,p=card(parent,pad=26)
        box.pack(fill='x',pady=(8,18))
        label(p,'APEX  /  DESKTOP EDITION',size=10,weight='bold',color=self.accent).pack(anchor='w',pady=(0,11))
        label(p,'Una aplicación. Tus descargas.',size=22,weight='bold').pack(anchor='w',pady=(0,12))
        label(p,'Apex Descarga Desktop 0.2.1 UI Pro para Windows 11.',size=11,color=MUTED).pack(anchor='w',pady=(0,8))
        label(p,'Descarga y organiza medios propios o autorizados, sin necesidad de abrir el navegador.',size=10,color=MUTED,wrap=780).pack(anchor='w')
        tk.Frame(p,bg=OUTLINE,height=1).pack(fill='x',pady=(19,16))
        label(p,'yt-dlp   •   FFmpeg externo   •   Cola secuencial   •   Sin cuenta   •   Datos locales',size=10,color=MUTED).pack(anchor='w')

        box,p=card(parent,pad=25)
        box.pack(fill='x',pady=(0,18))
        label(p,'SOPORTE Y SUGERENCIAS',size=10,color=self.accent,weight='bold').pack(anchor='w')
        label(p,'¿Encontraste un problema?',size=18,weight='bold').pack(anchor='w',pady=(12,8))
        label(p,'angelrlpz030207@gmail.com',size=12,color=MUTED).pack(anchor='w',pady=(0,10))
        label(p,'Al reportar, incluye versión, pasos para reproducir y el mensaje de error. Nunca envíes contraseñas ni cookies.',size=10,color=SOFT,wrap=790).pack(anchor='w')
        row=tk.Frame(p,bg=SURFACE);row.pack(fill='x',pady=(16,1))
        action(row,'Escribir al soporte',self._write_support,width=200,accent=self.accent,filled=True,side='left')
        action(row,'Copiar correo',self._copy_support,width=156,accent=self.accent,side='left',padx=10)
        action(row,'Código fuente GitHub',lambda:webbrowser.open('https://github.com/Sombra-789/apex-descarga'),width=200,accent=self.accent,side='left')

        label(parent,'© 2026 Apex Visual Studio. Solo contenido autorizado; no evita DRM. Los programas externos pertenecen a sus respectivos titulares.',size=9,color=SOFT,wrap=900).pack(anchor='w',pady=(4,20))

    def _empty(self,parent,message):
        outer,p=card(parent,pad=22)
        outer.pack(fill='x',pady=(2,15))
        label(p,'☰  Nada por aquí todavía',size=13,weight='bold',color=self.accent).pack(anchor='w')
        label(p,message,size=10,color=MUTED).pack(anchor='w',pady=(6,0))

    def _say(self,message,error=False):
        super()._say(message,error=error)

    def _set_art(self,label,url,size):
        # Heredamos la descarga segura y los límites de miniaturas de 0.1.
        super()._set_art(label,url,size)
