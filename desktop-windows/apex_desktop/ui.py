"""Interfaz de escritorio Apex con Tkinter; sin dependencia de Brave."""
from __future__ import annotations

import io
import os
import queue
import sys
import threading
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageTk

from .coordinator import DownloadCoordinator
from .engine import MediaEngine, ffmpeg_path, version as engine_version
from .models import DownloadJob, QUALITIES, THEMES, display_bytes, display_duration, is_hex_color, validate_url
from .storage import AppStore

BG = "#090E1A"
NAV = "#0D1525"
CARD = "#141F33"
CARD_2 = "#1B2942"
FIELD = "#101829"
BORDER = "#293A55"
TEXT = "#F3F6FF"
MUTED = "#96A8C2"
SOFT = "#647895"
GREEN = "#52DDB4"
RED = "#FF8C9A"
FONT = "Segoe UI"


class ScrollBody(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Apex.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window((0, 0), anchor="nw", window=self.inner)
        self.inner.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        self.bind("<Enter>", self._scroll_on)
        self.bind("<Leave>", self._scroll_off)

    def _scroll_on(self, _):
        self.canvas.bind_all("<MouseWheel>", self._wheel)

    def _scroll_off(self, _):
        self.canvas.unbind_all("<MouseWheel>")

    def _wheel(self, e):
        self.canvas.yview_scroll(int(-e.delta / 120) if e.delta else 0, "units")

    def clear(self):
        for item in self.inner.winfo_children():
            item.destroy()
        self.canvas.yview_moveto(0)


class GradientButton(tk.Canvas):
    def __init__(self, parent, text, command, color, width=220, height=46):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         bd=0, highlightthickness=0, cursor="hand2")
        self.color = color
        self.label_text = text
        self.command = command
        self._image = None
        self.bind("<Button-1>", lambda _: self.command())
        self.bind("<Enter>", lambda _: self._paint(True))
        self.bind("<Leave>", lambda _: self._paint(False))
        self._paint(False)

    def _paint(self, hovered: bool):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        from PIL import ImageColor
        c = ImageColor.getrgb(self.color)
        e = (min(255, c[0] + 65), min(255, c[1] + 18), min(255, c[2] + 45))
        scale = 2
        im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
        pix = ImageDraw.Draw(im)
        for x in range(w * scale):
            t = x / max(w * scale - 1, 1)
            rgb = tuple(round((a * (1-t) + b*t) * (1.09 if hovered else 1)) for a,b in zip(c,e))
            rgb = tuple(min(255, z) for z in rgb)
            pix.line([(x, 0), (x, h*scale)], fill=(*rgb, 255))
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w*scale-1, h*scale-1), radius=15*scale, fill=255)
        im.putalpha(mask)
        im = im.resize((w,h), Image.Resampling.LANCZOS)
        self._image = ImageTk.PhotoImage(im)
        self.delete("all")
        self.create_image(0,0,anchor="nw",image=self._image)
        self.create_text(w/2,h/2,text=self.label_text,fill="white",font=(FONT,11,"bold"))


def tlabel(parent, text, size=11, color=TEXT, weight="normal", **kw):
    return tk.Label(parent, text=text, font=(FONT, size, weight), fg=color,
                    bg=parent.cget("bg"), anchor="w", justify="left", **kw)


def simple_button(parent, text, command, accent=False, color=None):
    bg = color if color else (CARD_2 if accent else FIELD)
    return tk.Button(parent, text=text, command=command, bg=bg, fg=TEXT,
                     activebackground=bg, activeforeground="white", relief="flat",
                     bd=0, padx=15, pady=10, font=(FONT, 10, "bold"),
                     cursor="hand2", highlightthickness=0, overrelief="flat")


def panel(parent, border=True, padding=22):
    outline = tk.Frame(parent, bg=BORDER if border else CARD)
    inside = tk.Frame(outline, bg=CARD, padx=padding, pady=padding)
    inside.pack(fill="both", expand=True, padx=1 if border else 0, pady=1 if border else 0)
    return outline, inside


def field(parent, textvariable, width=54):
    f = tk.Entry(parent, textvariable=textvariable, width=width,
                 bg=FIELD, fg=TEXT, insertbackground="white", relief="flat",
                 highlightcolor=BORDER, highlightbackground=BORDER,
                 highlightthickness=1, font=(FONT, 12), bd=0)
    return f


class DesktopApp(tk.Tk):
    def __init__(self, engine=None, store=None):
        super().__init__()
        self.store = store or AppStore()
        self.engine = engine or MediaEngine()
        self.accent = self.store.settings["accent"]
        self.title("Apex Descarga Desktop 0.1 — Apex Visual Studio")
        self.geometry("1170x790")
        self.minsize(920, 660)
        self.configure(bg=BG)
        self._icon = None
        self._set_icon()
        style=ttk.Style(self)
        style.theme_use("clam")
        style.configure("Apex.TCombobox", fieldbackground=FIELD, background=CARD_2, foreground=TEXT,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, arrowcolor=TEXT,
                        padding=8)
        style.map("Apex.TCombobox",fieldbackground=[("readonly",FIELD),("disabled",FIELD)],
                  foreground=[("readonly",TEXT),("disabled",MUTED)])
        style.configure("Apex.Vertical.TScrollbar", background=CARD_2, troughcolor=BG,
                        bordercolor=BG, arrowcolor=MUTED, lightcolor=CARD_2, darkcolor=CARD_2)
        self.events: queue.Queue[tuple] = queue.Queue()
        self.coordinator = DownloadCoordinator(self.engine, self._notify, self.store.folder)
        self.page = "inicio"
        self.filter_status = "Todas"
        self.search_query = ""
        self.media_type = tk.StringVar(value="video")
        self.url = tk.StringVar()
        self.quality = tk.StringVar(value="1080p")
        self.preview: dict | None = None
        self.preview_url = ""
        self._images = {}
        self._pending_images = set()
        self._toast = "Listo para descargar contenido propio o autorizado."
        self._needs_redraw = True
        self._last_snapshot = 0
        self._pending_save = False
        self._last_ui = 0
        self._build_shell()
        self.after(160, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_icon(self):
        icon = Path(__file__).resolve().parent.parent / "assets" / "apex_icon.png"
        if getattr(sys, "frozen", False):
            icon = Path(getattr(sys, "_MEIPASS", "")) / "assets" / "apex_icon.png"
        if icon.exists():
            try:
                self._icon = tk.PhotoImage(file=str(icon))
                self.iconphoto(True, self._icon)
            except tk.TclError:
                pass

    def _notify(self, jobid, typ, payload):
        self.events.put((jobid, typ, payload))

    def _build_shell(self):
        for child in self.winfo_children():
            child.destroy()
        self.configure(bg=BG)
        self.shell = tk.Frame(self, bg=BG)
        self.shell.pack(fill="both", expand=True)
        self.sidebar = tk.Frame(self.shell, width=235, bg=NAV, padx=20, pady=25)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = tk.Frame(self.sidebar, bg=NAV)
        brand.pack(fill="x", pady=(0, 45))
        if self.store.settings["show_logo"] and self._icon:
            icon_path = Path(__file__).resolve().parent.parent / "assets" / "apex_icon.png"
            if getattr(sys, "frozen", False):
                icon_path = Path(getattr(sys, "_MEIPASS", "")) / "assets" / "apex_icon.png"
            try:
                icon_image = Image.open(icon_path).convert("RGBA").resize((42,42), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(icon_image)
                logo = tk.Label(brand, image=photo, bg=NAV)
                logo.image=photo
                logo.pack(side="left",padx=(0,10))
            except (OSError, tk.TclError):
                tlabel(brand, "⬇", size=28, color=self.accent, weight="bold").pack(side="left", padx=(0, 11))
        labels = tk.Frame(brand, bg=NAV)
        labels.pack(side="left")
        tlabel(labels, "APEX", size=19, weight="bold").pack(anchor="w")
        tlabel(labels, "DESCARGA", size=10, color=self.accent, weight="bold").pack(anchor="w")
        tlabel(self.sidebar, "MENÚ PRINCIPAL", size=9, color=SOFT, weight="bold").pack(anchor="w", pady=(0,13))
        self.nav_buttons = {}
        for key, icon, title in [("inicio","⌂", "Inicio"),("cola","≡", "Cola de descargas"),("biblioteca","▣", "Biblioteca"),("ajustes","⚙", "Ajustes")]:
            selected = key == self.page
            btn = tk.Button(self.sidebar,text=f"{icon}    {title}",anchor="w",
                bg=CARD_2 if selected else NAV,fg=self.accent if selected else MUTED,
                activebackground=CARD_2,activeforeground=TEXT,bd=0,relief="flat",
                padx=13,pady=14,font=(FONT,11,"bold" if selected else "normal"),
                highlightthickness=0,cursor="hand2",command=lambda p=key:self.navigate(p))
            btn.pack(fill="x",pady=4)
            self.nav_buttons[key] = btn
        tk.Frame(self.sidebar,bg=NAV).pack(fill="both",expand=True)
        tlabel(self.sidebar,"APEX VISUAL STUDIO",size=9,color=SOFT,weight="bold").pack(anchor="w")
        tlabel(self.sidebar,"Desktop v0.1 • Windows 11",size=9,color=MUTED).pack(anchor="w",pady=(5,0))
        self.content = tk.Frame(self.shell,bg=BG)
        self.content.pack(side="left",fill="both",expand=True)
        self.topbar = tk.Frame(self.content,bg=BG,height=83,padx=28,pady=17)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        self.page_title = tlabel(self.topbar,"",size=21,weight="bold")
        self.page_title.pack(side="left",anchor="w")
        self.badge = tlabel(self.topbar,"● yt-dlp " + engine_version(),size=10,
                            color=GREEN if engine_version()!="No instalado" else RED)
        self.badge.pack(side="right")
        self.scroll = ScrollBody(self.content)
        self.scroll.pack(fill="both",expand=True,padx=27)
        self.statusbar = tk.Frame(self.content,bg=NAV,padx=22,pady=12)
        self.statusbar.pack(fill="x",side="bottom")
        self.status_text = tlabel(self.statusbar,self._toast,size=9,color=MUTED)
        self.status_text.pack(side="left",fill="x",expand=True)
        tlabel(self.statusbar,"Sin cuenta · Datos locales · Sin telemetría Apex",size=9,color=SOFT).pack(side="right")
        self._render()

    def navigate(self, page):
        self.page = page
        for key, btn in self.nav_buttons.items():
            selected = key == page
            btn.configure(bg=CARD_2 if selected else NAV,fg=self.accent if selected else MUTED,
                          font=(FONT,11,"bold" if selected else "normal"))
        self._render()

    def _render(self):
        self.scroll.clear()
        self.page_title.configure(text={"inicio":"Tu centro de descargas","cola":"Cola de descargas", "biblioteca":"Biblioteca multimedia", "ajustes":"Ajustes y personalización"}[self.page])
        page = self.scroll.inner
        if self.page == "inicio": self._home(page)
        elif self.page == "cola": self._queue_page(page)
        elif self.page == "biblioteca": self._library_page(page)
        else: self._settings(page)
        self._needs_redraw = False

    def _section_title(self, parent, overline, title, subtitle=""):
        tlabel(parent,overline.upper(),size=9,color=self.accent,weight="bold").pack(anchor="w",pady=(15,5))
        tlabel(parent,title,size=18,weight="bold").pack(anchor="w")
        if subtitle: tlabel(parent,subtitle,size=10,color=MUTED,wraplength=710).pack(anchor="w",pady=(4,16))

    def _home(self, parent):
        self._section_title(parent,"Apex Descarga Desktop","Descarga lo que importa", "Pega un enlace y selecciona el formato. Todo se procesa localmente en tu equipo.")
        wrap, box = panel(parent)
        wrap.pack(fill="x", pady=(0,18))
        tlabel(box,"ENLACE DEL CONTENIDO",size=9,color=MUTED,weight="bold").pack(anchor="w",pady=(0,9))
        linkrow = tk.Frame(box,bg=CARD)
        linkrow.pack(fill="x")
        entry = field(linkrow,self.url)
        entry.pack(side="left",fill="x",expand=True,ipady=13)
        self.link_entry = entry
        simple_button(linkrow,"Pegar",self._paste).pack(side="left",padx=(10,0))
        simple_button(linkrow,"Analizar enlace",self._probe,accent=True).pack(side="left",padx=(9,0))
        tlabel(box,"VISTA PREVIA",size=9,color=self.accent,weight="bold").pack(anchor="w",pady=(24,12))
        meta = tk.Frame(box,bg=CARD_2,padx=15,pady=14)
        meta.pack(fill="x")
        self.preview_art = tk.Label(meta,text="▶",fg=self.accent,bg=FIELD,font=(FONT,28),width=11,height=4)
        self.preview_art.pack(side="left",padx=(0,18))
        info = tk.Frame(meta,bg=CARD_2)
        info.pack(side="left",fill="both",expand=True)
        meta_preview = self.preview if self.preview and self.preview_url == self.url.get().strip() else None
        title = meta_preview.get("title") if meta_preview else "Tu próximo video o canción"
        tlabel(info,title,size=15,weight="bold",wraplength=440).pack(anchor="w",pady=(9,9))
        self.meta_label = tlabel(info,(meta_preview.get("uploader") or "Fuente original")+"   ·   "+display_duration(meta_preview.get("duration")) if meta_preview else "Analiza el enlace para mostrar portada, autor y duración",size=10,color=MUTED,wraplength=450)
        self.meta_label.pack(anchor="w")
        if meta_preview and meta_preview.get("thumbnail"):
            self._set_art(self.preview_art,meta_preview["thumbnail"],(160,104))
        tlabel(box,"FORMATO",size=9,color=MUTED,weight="bold").pack(anchor="w",pady=(23,9))
        fmtrow = tk.Frame(box,bg=CARD)
        fmtrow.pack(fill="x")
        for val,text in [("video","▣  Video MP4"),("audio","♫  Audio MP3")]:
            radio = tk.Radiobutton(fmtrow,text=text,value=val,variable=self.media_type,
                bg=CARD,fg=TEXT,activebackground=CARD,activeforeground=TEXT,
                selectcolor=FIELD,indicatoron=0,relief="flat",bd=1,
                padx=15,pady=11,font=(FONT,10,"bold"),command=self._switch_format)
            radio.pack(side="left",padx=(0,10))
        tlabel(box,"CALIDAD MÁXIMA",size=9,color=MUTED,weight="bold").pack(anchor="w",pady=(20,8))
        self.quality_selector = ttk.Combobox(box,values=QUALITIES,state="readonly",textvariable=self.quality,width=29,font=(FONT,11),style="Apex.TCombobox")
        self.quality_selector.pack(anchor="w",ipady=7)
        self._switch_format()
        actions = tk.Frame(box,bg=CARD)
        actions.pack(fill="x",pady=(23,3))
        GradientButton(actions,"↓  AGREGAR A LA COLA",self._add_download,self.accent,width=265,height=48).pack(side="left")
        tlabel(actions,"Solo contenido propio o autorizado · Sin evasión de DRM",size=9,color=MUTED).pack(side="left",padx=17)
        self._section_title(parent,"Actividad","Últimas descargas")
        latest=list(reversed(self.store.jobs[-3:]))
        if not latest: self._empty(parent,"Todavía no tienes descargas. Agrega tu primer enlace.")
        for job in latest:
            self._job_card(parent,job)
        if len(self.store.jobs)>3:
            simple_button(parent,"Ver toda la cola  →",lambda:self.navigate("cola")).pack(anchor="w",pady=(3,22))

    def _switch_format(self):
        if hasattr(self,"quality_selector"):
            self.quality_selector.configure(state="disabled" if self.media_type.get()=="audio" else "readonly")

    def _paste(self):
        try:
            text=self.clipboard_get().strip()
            self.url.set(text)
            self._say("Enlace pegado; puedes analizarlo.")
        except tk.TclError:
            self._say("El portapapeles está vacío o no contiene texto.",error=True)

    def _probe(self):
        try:
            url=validate_url(self.url.get())
        except ValueError as exc:
            messagebox.showwarning("Enlace no válido",str(exc),parent=self)
            return
        self._say("Analizando enlace…")
        def work():
            try:
                meta=self.engine.probe(url)
                self.events.put(("", "preview", {"url":url,"meta":meta}))
            except Exception as exc:
                self.events.put(("", "probe_error", {"error":str(exc)[:300]}))
        threading.Thread(target=work,daemon=True,name="ApexPreview").start()

    def _add_download(self):
        try:
            job=DownloadJob(self.url.get(),kind=self.media_type.get(),quality=self.quality.get())
        except ValueError as exc:
            messagebox.showwarning("Revisa tu enlace",str(exc),parent=self)
            return
        if self.preview and self.preview_url == job.url:
            for key in ("title","uploader","duration","thumbnail"):
                setattr(job,key,self.preview.get(key) or getattr(job,key))
        self.store.add_job(job)
        self.coordinator.enqueue(job)
        self._say("Agregado a la cola. La descarga comenzará automáticamente.")
        self._render()

    def _queue_page(self,parent):
        self._section_title(parent,"Administrador","Todas tus descargas","Las tareas se procesan una a una para ahorrar recursos del equipo.")
        tabs=tk.Frame(parent,bg=BG)
        tabs.pack(fill="x",pady=(0,15))
        for name in ("Todas","Pendientes","Descargando","Completadas","Errores"):
            selected=name==self.filter_status
            btn=simple_button(tabs,name,lambda n=name:self._set_filter(n),accent=selected,color=CARD_2 if selected else NAV)
            btn.configure(fg=self.accent if selected else MUTED)
            btn.pack(side="left",padx=(0,8))
        jobs=list(reversed(self.store.jobs))
        if self.filter_status=="Pendientes":jobs=[x for x in jobs if x.state in ("pendiente","interrumpido")]
        if self.filter_status=="Descargando":jobs=[x for x in jobs if x.state in ("descargando","procesando","analizando")]
        if self.filter_status=="Completadas":jobs=[x for x in jobs if x.state=="completado"]
        if self.filter_status=="Errores":jobs=[x for x in jobs if x.state in ("error","cancelado")]
        if not jobs: self._empty(parent,"No hay tareas en esta categoría.")
        for job in jobs:
            self._job_card(parent,job)

    def _set_filter(self,name):
        self.filter_status=name
        self._render()

    def _job_card(self,parent,job):
        wrap,content=panel(parent,padding=16)
        wrap.pack(fill="x",pady=(0,12))
        row=tk.Frame(content,bg=CARD)
        row.pack(fill="x")
        art=tk.Label(row,text="♫" if job.kind=="audio" else "▶",bg=FIELD,fg=self.accent,font=(FONT,22),width=7,height=3)
        art.pack(side="left",padx=(0,17))
        if job.thumbnail:
            self._set_art(art,job.thumbnail,(112,72))
        middle=tk.Frame(row,bg=CARD)
        middle.pack(side="left",fill="both",expand=True)
        tlabel(middle,job.title[:70],size=12,weight="bold",wraplength=475).pack(anchor="w",pady=(0,5))
        tlabel(middle,(job.uploader or "Enlace multimedia")+"   ·   "+(display_duration(job.duration) if job.duration else "")+"   ·   "+("MP3" if job.kind=="audio" else job.quality),size=9,color=MUTED).pack(anchor="w")
        status_colors={"completado":GREEN,"error":RED,"cancelado":RED,"descargando":self.accent,"procesando":self.accent}
        tlabel(middle,job.state.upper(),size=9,color=status_colors.get(job.state,MUTED),weight="bold").pack(anchor="w",pady=(11,0))
        btns=tk.Frame(row,bg=CARD)
        btns.pack(side="right",padx=(14,0))
        if job.state in ("pendiente","descargando","procesando"):
            simple_button(btns,"Cancelar",lambda j=job:self._cancel(j)).pack(anchor="e",pady=3)
        if job.state in ("error","cancelado","interrumpido"):
            simple_button(btns,"Reintentar",lambda j=job:self._retry(j),accent=True).pack(anchor="e",pady=3)
        if job.can_open:
            simple_button(btns,"Abrir archivo",lambda j=job:self._open_file(j)).pack(anchor="e",pady=3)
        if job.state=="completado":
            simple_button(btns,"Ver carpeta",lambda:self._open_folder()).pack(anchor="e",pady=3)
        if job.state in ("descargando","procesando","completado"):
            bar=tk.Frame(content,bg=FIELD,height=6)
            bar.pack(fill="x",pady=(14,4))
            bar.pack_propagate(False)
            fill=tk.Frame(bar,bg=self.accent)
            fill.place(relx=0,rely=0,relwidth=max(0.0,min(1.0,job.progress/100)),relheight=1)
            detail=f"{job.progress:.1f}%   ·   {display_bytes(job.downloaded)}"
            if job.speed: detail+=f"   ·   {display_bytes(job.speed)}/s"
            if job.eta is not None: detail+=f"   ·   Restante: {display_duration(job.eta)}"
            tlabel(content,detail,size=9,color=MUTED).pack(anchor="w",pady=(5,0))
        if job.error and job.state in ("error","interrumpido"):
            tlabel(content,job.error[:200],size=9,color=RED,wraplength=650).pack(anchor="w",pady=(8,0))

    def _library_page(self,parent):
        self._section_title(parent,"Tus archivos","Biblioteca multimedia","Abre los archivos guardados en el equipo, sin cargar tus datos a Apex.")
        search=tk.StringVar(value=self.search_query)
        inp=field(parent,search,width=70)
        inp.pack(fill="x",ipady=12,pady=(0,15))
        def do_search(*_):
            self.search_query=search.get()
            if self.page=="biblioteca":
                # No reconstruir el campo mientras se escribe: filtrar al presionar Enter.
                pass
        search.trace_add("write",do_search)
        inp.bind("<Return>",lambda _:self._render())
        tlabel(parent,"Pulsa Enter para filtrar por título o autor.",size=9,color=MUTED).pack(anchor="w",pady=(0,15))
        jobs=[j for j in reversed(self.store.jobs) if j.state=="completado"]
        q=self.search_query.strip().casefold()
        if q: jobs=[j for j in jobs if q in (j.title+" "+j.uploader).casefold()]
        if not jobs: self._empty(parent,"No hay archivos completados que coincidan con la búsqueda.")
        for job in jobs: self._job_card(parent,job)
        simple_button(parent,"Abrir carpeta de descargas  ↗",self._open_folder).pack(anchor="w",pady=(4,20))

    def _settings(self,parent):
        self._section_title(parent,"Personalización","Hazla tuya","Tus cambios se guardan solo en este dispositivo.")
        wrap,box=panel(parent)
        wrap.pack(fill="x",pady=(0,16))
        tlabel(box,"COLORES DE APEX",size=9,color=self.accent,weight="bold").pack(anchor="w")
        choices=tk.Frame(box,bg=CARD)
        choices.pack(fill="x",pady=(12,12))
        for name,color in THEMES.items():
            tk.Button(choices,text="●  "+name,bg=FIELD,fg=color,
                      activebackground=CARD_2,activeforeground=color,
                      relief="flat",bd=0,padx=9,pady=9,font=(FONT,10,"bold"),
                      command=lambda c=color,n=name:self._change_theme(n,c),cursor="hand2").pack(side="left",padx=(0,7))
        picker=tk.Frame(box,bg=CARD)
        picker.pack(fill="x")
        tlabel(picker,"Color HEX  ",size=11,color=MUTED).pack(side="left")
        self.hex_value=tk.StringVar(value=self.accent)
        field(picker,self.hex_value,width=12).pack(side="left",ipady=8)
        simple_button(picker,"Aplicar",self._custom_hex).pack(side="left",padx=12)
        self.logo_value=tk.BooleanVar(value=self.store.settings["show_logo"])
        tk.Checkbutton(box,text="Mostrar marca en la barra lateral",variable=self.logo_value,
                       bg=CARD,fg=TEXT,activebackground=CARD,activeforeground=TEXT,
                       selectcolor=FIELD,font=(FONT,10),command=self._set_logo).pack(anchor="w",pady=(15,0))
        wrap,box=panel(parent)
        wrap.pack(fill="x",pady=(0,16))
        tlabel(box,"ALMACENAMIENTO",size=9,color=self.accent,weight="bold").pack(anchor="w")
        tlabel(box,str(self.store.folder()),size=10,color=MUTED,wraplength=650).pack(anchor="w",pady=(9,12))
        options=tk.Frame(box,bg=CARD)
        options.pack(fill="x")
        simple_button(options,"Elegir carpeta…",self._choose_folder).pack(side="left",padx=(0,10))
        simple_button(options,"Abrir carpeta",self._open_folder).pack(side="left")
        wrap,box=panel(parent)
        wrap.pack(fill="x",pady=(0,16))
        tlabel(box,"MOTOR MULTIMEDIA",size=9,color=self.accent,weight="bold").pack(anchor="w")
        tlabel(box,"yt-dlp: "+engine_version(),size=12,weight="bold").pack(anchor="w",pady=(10,5))
        tlabel(box,"FFmpeg: "+("Detectado" if ffmpeg_path() else "No detectado (necesario para MP3 y combinar video)"),size=10,color=GREEN if ffmpeg_path() else RED).pack(anchor="w",pady=(3,8))
        tlabel(box,"Para actualizar yt-dlp, vuelve a ejecutar INSTALAR_Y_EJECUTAR.cmd; para reconstruir el EXE usa BUILD_EXE_WINDOWS.cmd.",size=10,color=MUTED,wraplength=670).pack(anchor="w",pady=(4,0))
        wrap,box=panel(parent)
        wrap.pack(fill="x",pady=(0,22))
        tlabel(box,"PRIVACIDAD Y SOPORTE",size=9,color=self.accent,weight="bold").pack(anchor="w")
        tlabel(box,"Apex no pide cuenta y no integra telemetría propia. yt-dlp contacta al sitio del enlace. Descarga solo contenido autorizado.",size=10,color=MUTED,wraplength=680).pack(anchor="w",pady=(10,10))
        tlabel(box,"Fallos y sugerencias: angelrlpz030207@gmail.com",size=10,color=TEXT).pack(anchor="w")
        simple_button(box,"Ver código y documentación en GitHub ↗",lambda:webbrowser.open("https://github.com/Sombra-789/apex-descarga")).pack(anchor="w",pady=(12,0))

    def _change_theme(self,name,color):
        self.store.settings.update({"theme":name,"accent":color})
        self.store.save_settings()
        self.accent=color
        self._build_shell()

    def _custom_hex(self):
        h=self.hex_value.get().strip()
        if not is_hex_color(h):
            messagebox.showwarning("Color incorrecto","Utiliza un código de seis dígitos, por ejemplo #A16BFA.",parent=self)
            return
        self._change_theme(self.store.settings["theme"],h.upper())

    def _set_logo(self):
        self.store.settings["show_logo"]=self.logo_value.get()
        self.store.save_settings()
        self._build_shell()

    def _choose_folder(self):
        path=filedialog.askdirectory(parent=self,initialdir=str(self.store.folder()),title="Carpeta de descargas Apex")
        if path:
            if self.coordinator.busy():
                messagebox.showinfo("Descarga activa","Espera a que termine la cola para cambiar la carpeta.",parent=self)
                return
            self.store.settings["folder"]=path
            self.store.save_settings()
            self._say("Carpeta de destino actualizada.")
            self._render()

    def _open_folder(self):
        try:
            folder=self.store.folder()
            folder.mkdir(parents=True,exist_ok=True)
            if os.name=="nt": os.startfile(str(folder))
            else: webbrowser.open(folder.as_uri())
        except OSError as exc:
            messagebox.showerror("No se puede abrir carpeta",str(exc),parent=self)

    def _open_file(self,job):
        try:
            if os.name=="nt": os.startfile(job.file_path)
            else: webbrowser.open(Path(job.file_path).as_uri())
        except OSError as exc:
            messagebox.showerror("No se puede abrir archivo",str(exc),parent=self)

    def _cancel(self,job):
        if job.state=="pendiente":
            self.coordinator.cancel(job.id)
            job.state="cancelado"
            self.store.save_jobs()
            self._render()
        elif job.state in ("descargando","procesando"):
            self.coordinator.cancel(job.id)
            self._say("Cancelación solicitada. Puede tardar durante el posprocesado.")

    def _retry(self,job):
        if job.state not in ("error","cancelado","interrumpido"):
            return
        # Crear un nuevo intento con ID nuevo evita una carrera con la cancelación
        # anterior mientras el worker todavía libera sus recursos.
        replacement = DownloadJob(job.url,kind=job.kind,quality=job.quality,
                                  title=job.title,uploader=job.uploader,
                                  duration=job.duration,thumbnail=job.thumbnail)
        self.store.add_job(replacement)
        self.coordinator.enqueue(replacement)
        self._say("Se agregó un nuevo intento a la cola.")
        self._render()

    def _empty(self,parent,message):
        wrap,p=panel(parent)
        wrap.pack(fill="x",pady=(0,15))
        tlabel(p,"▤",size=28,color=self.accent).pack(anchor="w")
        tlabel(p,message,size=11,color=MUTED).pack(anchor="w",pady=(7,5))

    def _say(self,message,error=False):
        self._toast=message
        if hasattr(self,"status_text") and self.status_text.winfo_exists():
            self.status_text.configure(text=message,fg=RED if error else MUTED)

    def _set_art(self,label,url,size):
        if url in self._images:
            try:
                img=self._images[url].copy()
                img.thumbnail(size,Image.Resampling.LANCZOS)
                photo=ImageTk.PhotoImage(img)
                label.configure(image=photo,text="",width=size[0],height=size[1])
                label.image=photo
            except tk.TclError:
                pass
            return
        if url in self._pending_images: return
        self._pending_images.add(url)
        def fetch():
            try:
                validate_url(url)
                req=Request(url,headers={"User-Agent":"ApexDescargaDesktop/0.1"})
                with urlopen(req,timeout=10) as response:
                    if response.headers.get("content-type","").lower().split(";")[0] not in ("image/jpeg","image/png","image/webp"):
                        return
                    data=response.read(2_000_001)
                    if len(data)>2_000_000:
                        return
                img=Image.open(io.BytesIO(data))
                img.thumbnail((450,260),Image.Resampling.LANCZOS)
                self.events.put(("", "artwork", {"url":url,"image":img.copy()}))
            except Exception:
                pass
            finally:
                self.events.put(("", "artwork_done", {"url":url}))
        threading.Thread(target=fetch,daemon=True).start()

    def _poll(self):
        count=0
        needs_redraw=False
        need_save=False
        while count<250:
            try:
                jobid,typ,payload=self.events.get_nowait()
            except queue.Empty:
                break
            count+=1
            if typ=="preview":
                self.preview=payload["meta"]
                self.preview_url=payload["url"]
                self._say("Vista previa obtenida. Ya puedes agregarlo a la cola.")
                needs_redraw=True
            elif typ=="probe_error":
                self._say("No se pudo analizar: "+payload["error"][:170],error=True)
            elif typ=="artwork":
                if len(self._images)>=60:
                    self._images.pop(next(iter(self._images)))
                self._images[payload["url"]]=payload["image"]
                needs_redraw=True
            elif typ=="artwork_done":
                self._pending_images.discard(payload["url"])
            else:
                job=self.store.get_job(jobid)
                if not job: continue
                if typ=="state":
                    if job.state!="cancelado":
                        job.state=payload.get("state",job.state)
                        job.progress=max(job.progress,payload.get("progress",0))
                elif typ=="progress":
                    if job.state!="cancelado":
                        for k in ("downloaded","total","speed","eta","progress"):
                            if k in payload: setattr(job,k,payload[k])
                elif typ=="complete":
                    if job.state!="cancelado":
                        job.state="completado"
                        job.progress=100
                        for k in ("title","uploader","duration","thumbnail","file_path"):
                            if k in payload: setattr(job,k,payload[k])
                        self._say("¡Descarga completada! Encontrarás el archivo en tu carpeta elegida.")
                elif typ=="error":
                    if job.state!="cancelado":
                        job.state="error"
                        job.error=payload.get("error","")[:500]
                        self._say("Una descarga falló; revisa la cola para reintentar.",error=True)
                elif typ=="cancelled":
                    job.state="cancelado"
                    self._say("Descarga cancelada.")
                needs_redraw=True
                need_save=True
        import time
        now=time.monotonic()
        if need_save:
            self._pending_save = True
        if self._pending_save and now-self._last_snapshot>0.8:
            self.store.save_jobs()
            self._last_snapshot=now
            self._pending_save=False
        if needs_redraw:
            self._needs_redraw=True
        if self._needs_redraw and now-self._last_ui>0.7:
            self._last_ui=now
            # No reconstruir Ajustes mientras se está escribiendo el código HEX.
            if self.page in ("cola","biblioteca","inicio"):
                position=self.scroll.canvas.yview()[0]
                self._render()
                self.scroll.canvas.update_idletasks()
                self.scroll.canvas.yview_moveto(position)
        self.after(180,self._poll)

    def _on_close(self):
        if self.coordinator.busy():
            if not messagebox.askyesno("Descargas activas","Cerrar Apex interrumpirá las descargas activas. Los trabajos se podrán reintentar al volver a abrir. ¿Salir?",parent=self):
                return
        self.store.save_jobs()
        self.destroy()
