#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panorama Converter to Minecraft  ·  DuxLay
Requisitos: pip install pillow numpy
# Compilar:   pyinstaller --onefile --windowed --name DuxLayPanoConverter --icon=icono.ico panorama_generator.py
"""

import os, sys, math, random, threading, traceback, webbrowser
import ctypes  # <--- Agregamos este para el truco de la barra de tareas

# ──────────────────────────────────────────────────────────────
#  TRUCO MAESTRO PARA LA BARRA DE TAREAS (EVITA EL ICONO VACÍO)
# ──────────────────────────────────────────────────────────────
try:
    # Fuerza a Windows a identificar este script compilado como una app única con su propio icono
    id_aplicacion = 'duxlay.panoconverter.minecraft.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id_aplicacion)
except Exception:
    pass


# ──────────────────────────────────────────────────────────────
#  MANEJO DE LIBRERÍAS DE TERCEROS
# ──────────────────────────────────────────────────────────────
try:
    import numpy as np
except ImportError:
    print("Falta numpy. Instala con: pip install numpy"); sys.exit(1)

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Falta Pillow. Instala con: pip install pillow"); sys.exit(1)

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("Tkinter no disponible. En Linux: sudo apt install python3-tk"); sys.exit(1)


# ──────────────────────────────────────────────────────────────
#  FUNCIÓN EXTRA PARA EXTRAER EL ICONO EN RUTA TEMPORAL (.EXE)
# ──────────────────────────────────────────────────────────────
def obtener_ruta_recurso(ruta_relativa):
    """ Encuentra la ruta del archivo tanto en desarrollo como dentro del .exe compilado """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)


# ──────────────────────────────────────────────────────────────
#  NÚCLEO MATEMÁTICO Y LINKS
# ──────────────────────────────────────────────────────────────
FACE_ORDER  = ["panorama_0","panorama_1","panorama_2","panorama_3","panorama_4","panorama_5"]
FACE_LABELS = {
    "es": {"panorama_0":"Frente","panorama_1":"Derecha","panorama_2":"Atrás","panorama_3":"Izquierda","panorama_4":"Cielo","panorama_5":"Piso"},
    "en": {"panorama_0":"Front","panorama_1":"Right","panorama_2":"Back","panorama_3":"Left","panorama_4":"Sky","panorama_5":"Floor"}
}
FACE_VECTORS = {
    "panorama_0":((0,0,1),(1,0,0),(0,1,0)),  "panorama_1":((1,0,0),(0,0,-1),(0,1,0)),
    "panorama_2":((0,0,-1),(-1,0,0),(0,1,0)),"panorama_3":((-1,0,0),(0,0,1),(0,1,0)),
    "panorama_4":((0,1,0),(1,0,0),(0,0,-1)), "panorama_5":((0,-1,0),(1,0,0),(0,0,1)),
}
KOFI_URL    = "https://ko-fi.com/duxlay"
YOUTUBE_URL = "https://www.youtube.com/@DuxLay"

DONATE_MSGS = {
    "es": ["☕ Cómprame un Café", "💛 Apoyar", "🌮 Cómprame unos Tacos", "🍔 Cómprame una Hamburguesa"],
    "en": ["☕ Buy me a Coffee", "💛 Support", "🌮 Buy me a Taco bro", "🍔 Buy me a Burger"]
}

# ──────────────────────────────────────────────────────────────
#  DICCIONARIO DE TRADUCCIONES
# ──────────────────────────────────────────────────────────────
LOCALES = {
    "es": {
        "title_preview": "Vista previa 360°",
        "no_image": "Sin imagen",
        "hint_click": "Clic o arrastra en la imagen para fijar el centro (X e Y) del panorama_0",
        "sec_image": "1. Imagen",
        "btn_load": "📂 Cargar imagen",
        "no_file": "Ningún archivo cargado",
        "sec_center": "2. Centro",
        "btn_reset": "↺ Centro al medio",
        "sec_preview_p0": "↗ Vista previa panorama_0",
        "preview_placeholder": "Preview aquí",
        "sec_res": "3. Resolución",
        "lbl_width": "Ancho",
        "lbl_height": "Alto",
        "lbl_restip": "1080×1080 recomendado para Minecraft",
        "sec_out": "4. Carpeta de salida",
        "lbl_outinfo": "Vacío = junto al archivo, carpeta con el nombre de la imagen",
        "lbl_status_ready": "Listo · carga una imagen para comenzar",
        "lbl_status_loaded": "Imagen cargada · ajusta el centro y genera",
        "btn_generate": "✅ Generar panorama",
        "warn_no_img_title": "Sin imagen",
        "warn_no_img_msg": "Carga una imagen 360° primero.",
        "err_res_title": "Resolución inválida",
        "err_res_msg": "Valores entre 1 y 8192.",
        "status_generating": "Generando → ",
        "status_gen_step": "Generando {}/6 → {} ({})",
        "status_done": "✅ Listo — 6 caras generadas",
        "msg_done_title": "¡Listo!",
        "msg_done_msg": "panorama_0…panorama_5 guardados en:\n{}",
        "status_err": "❌ Error al generar",
        "err_title": "Error",
        "btn_youtube": "🔴 Ver canal de YouTube"
    },
    "en": {
        "title_preview": "360° Preview",
        "no_image": "No image",
        "hint_click": "Click or drag on the image to set the center (X and Y) of panorama_0",
        "sec_image": "1. Image",
        "btn_load": "📂 Load Image",
        "no_file": "No file loaded",
        "sec_center": "2. Center",
        "btn_reset": "↺ Center to middle",
        "sec_preview_p0": "↗ panorama_0 Preview",
        "preview_placeholder": "Preview here",
        "sec_res": "3. Resolution",
        "lbl_width": "Width",
        "lbl_height": "Height",
        "lbl_restip": "1080×1080 recommended for Minecraft",
        "sec_out": "4. Output Folder",
        "lbl_outinfo": "Empty = next to file, folder named after the image",
        "lbl_status_ready": "Ready · load an image to start",
        "lbl_status_loaded": "Image loaded · adjust center and generate",
        "btn_generate": "✅ Generate Panorama",
        "warn_no_img_title": "No image",
        "warn_no_img_msg": "Please load a 360° image first.",
        "err_res_title": "Invalid resolution",
        "err_res_msg": "Values must be between 1 and 8192.",
        "status_generating": "Generating → ",
        "status_gen_step": "Generating {}/6 → {} ({})",
        "status_done": "✅ Done — 6 faces generated",
        "msg_done_title": "Done!",
        "msg_done_msg": "panorama_0…panorama_5 saved in:\n{}",
        "status_err": "❌ Error during generation",
        "err_title": "Error",
        "btn_youtube": "🔴 View YouTube Channel"
    }
}

def generate_face(arr, face_key, ow, oh):
    fwd,rgt,up_ = [np.array(v,np.float64) for v in FACE_VECTORS[face_key]]
    h,w = arr.shape[:2]
    uu,vv = np.meshgrid(np.arange(ow),np.arange(oh))
    u=2*(uu+.5)/ow-1; v=1-2*(vv+.5)/oh
    dx=fwd[0]+u*rgt[0]+v*up_[0]; dy=fwd[1]+u*rgt[1]+v*up_[1]; dz=fwd[2]+u*rgt[2]+v*up_[2]
    n=np.sqrt(dx**2+dy**2+dz**2); dx/=n; dy/=n; dz/=n
    phi=np.arcsin(np.clip(dy,-1,1)); theta=np.arctan2(dx,dz)
    ex=(theta+math.pi)/(2*math.pi)*w; ey=((math.pi/2-phi)/math.pi)*h
    ex0=np.floor(ex).astype(np.int64); ey0=np.floor(ey).astype(np.int64)
    fx=(ex-ex0)[...,None]; fy=(ey-ey0)[...,None]
    ex0m=np.mod(ex0,w); ex1m=np.mod(ex0+1,w)
    ey0c=np.clip(ey0,0,h-1); ey1c=np.clip(ey0+1,0,h-1)
    c00=arr[ey0c,ex0m].astype(np.float64); c10=arr[ey0c,ex1m].astype(np.float64)
    c01=arr[ey1c,ex0m].astype(np.float64); c11=arr[ey1c,ex1m].astype(np.float64)
    return np.clip((c00*(1-fx)+c10*fx)*(1-fy)+(c01*(1-fx)+c11*fx)*fy,0,255).astype(np.uint8)

def recenter(arr,cx,cy=None):
    h,w=arr.shape[:2]
    out=np.roll(arr,(w//2)-int(round(cx)),axis=1)
    if cy is not None: out=np.roll(out,(h//2)-int(round(cy)),axis=0)
    return out

THEMES = {
    "dark": {
        "bg":"#0f1015","surface":"#161720","surface2":"#1f212d",
        "border":"#262936","fg":"#f1f3f9","fg2":"#868da4",
        "accent":"#22c55e","accent_dim":"#14532d","accent_fg":"#ffffff",
        "canvas_bg":"#08090c","sw_on":"#22c55e","sw_off":"#2a2d3d","sw_k":"#fff",
    },
    "light": {
        "bg":"#f4f6fa","surface":"#ffffff","surface2":"#f0f2f8",
        "border":"#e2e6f0","fg":"#0f172a","fg2":"#64748b",
        "accent":"#16a34a","accent_dim":"#dcfce7","accent_fg":"#ffffff",
        "canvas_bg":"#e2e8f0","sw_on":"#16a34a","sw_off":"#cbd5e1","sw_k":"#fff",
    },
}

class ToggleSwitch(tk.Canvas):
    W,H=36,18
    def __init__(self,parent,var,command=None,**kw):
        super().__init__(parent,width=self.W,height=self.H,highlightthickness=0,bd=0,**kw)
        self._v=var; self._cmd=command
        self.bind("<Button-1>",self._toggle)
        self._v.trace_add("write",lambda *_:self._draw())
        self._on = "#22c55e"
        self._off = "#2a2d3d"
        self._k = "#fff"
        self._draw()
    def _toggle(self,_=None):
        self._v.set(not self._v.get())
        if self._cmd: self._cmd()
    def _draw(self):
        self.delete("all")
        on=bool(self._v.get())
        tc=self._on if on else self._off
        kx=self.W-10 if on else 10
        r=self.H//2
        self.create_arc(0,0,self.H,self.H,start=90,extent=180,fill=tc,outline="")
        self.create_arc(self.W-self.H,0,self.W,self.H,start=270,extent=180,fill=tc,outline="")
        self.create_rectangle(r,0,self.W-r,self.H,fill=tc,outline="")
        self.create_oval(kx-r+2,2,kx+r-2,self.H-2,fill=self._k,outline="")
    def recolor(self,on,off,k,bg):
        self._on=on; self._off=off; self._k=k
        self.configure(bg=bg); self._draw()


# ──────────────────────────────────────────────────────────────
#  MOTOR DE ANIMACIÓN DE COLOR PARA EFECTOS FUTURISTAS (FADE INTERPOLATION)
# ──────────────────────────────────────────────────────────────
def animate_color(widget, start_hex, end_hex, steps=10, current_step=0, callback=None):
    if not widget.winfo_exists(): return
    
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]
    
    def rgb_to_hex(rgb_list):
        return f"#{int(rgb_list[0]):02x}{int(rgb_list[1]):02x}{int(rgb_list[2]):02x}"

    try:
        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)
    except:
        return # Si el formato falla

    curr_rgb = [
        start_rgb[i] + (end_rgb[i] - start_rgb[i]) * (current_step / steps)
        for i in range(3)
    ]
    
    next_hex = rgb_to_hex(curr_rgb)
    if callback:
        callback(next_hex)
    else:
        widget.configure(bg=next_hex)
        
    if current_step < steps:
        widget.after(15, lambda: animate_color(widget, start_hex, end_hex, steps, current_step + 1, callback))


class PanoramaApp:
    def __init__(self, root):
        self.root=root
        self.root.title("DuxLay Panorama Converter to Minecraft")
        self.root.minsize(1000,660)
        self.root.geometry("1180x720")

        self._tn="dark"
        self._lang="es"
        self.style=ttk.Style(self.root)
        try: self.style.theme_use("clam")
        except: pass

        # estado
        self.image_path=None; self.full_array=None
        self.preview_image=None; self.preview_tk=None
        self.center_x=None; self.center_y=None
        self.canvas_box=None; self.thumb_refs=[]
        self.p0_tk=None; self._ptimer=None; self._didx=0
        self._thumb_row=None
        
        # Animaciones de pulso
        self._pulse_direction = 1
        self._pulse_val = 0.0

        self.var_cx=tk.DoubleVar(value=0.5)
        self.var_cy=tk.DoubleVar(value=0.5)
        self.var_w=tk.StringVar(value="1080")
        self.var_h=tk.StringVar(value="1080")
        self.var_out=tk.StringVar(value="")
        self.var_theme=tk.BooleanVar(value=False)

        self._build(); self._theme(); self._cycle_donate(); self._pulse_animation()

    def t(self): return THEMES[self._tn]
    def loc(self, key): return LOCALES[self._lang].get(key, "")

    def _build(self):
        self.root.rowconfigure(0,weight=1)
        self.root.columnconfigure(0,weight=1)

        root_f=tk.Frame(self.root); root_f.grid(sticky="nsew")
        root_f.rowconfigure(1,weight=1); root_f.columnconfigure(0,weight=1)
        self._rf=root_f

        # 1. BARRA SUPERIOR
        top_utility = tk.Frame(root_f, height=45, padx=15)
        top_utility.grid(row=0, column=0, sticky="ew")
        top_utility.grid_propagate(False)
        self._top_util = top_utility

        # Botón Idioma
        self.btn_lang = tk.Button(top_utility, text="🇬🇧 EN", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=8, pady=2, command=self._toggle_language)
        self.btn_lang.pack(side="left", anchor="center", pady=8)

        # Botón Donar arriba
        self.btn_donate = tk.Button(top_utility, text=DONATE_MSGS[self._lang][0], font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=12, pady=4, command=lambda:webbrowser.open(KOFI_URL))
        self.btn_donate.pack(side="right", padx=(10,0), pady=6)
        self._bind_hover_fade(self.btn_donate, "#e8407a", "#c03060")

        # NUEVO BOTÓN DE YOUTUBE JUNTO A DONACIONES
        self.btn_youtube = tk.Button(top_utility, text="", font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", padx=12, pady=4, command=lambda:webbrowser.open(YOUTUBE_URL))
        self.btn_youtube.pack(side="right", padx=(10,0), pady=6)
        self._bind_hover_fade(self.btn_youtube, "#ff0000", "#b30000")

        # Switch Oscuro/Claro arriba
        sw_wrap = tk.Frame(top_utility)
        sw_wrap.pack(side="right", padx=10, pady=10)
        self._lbl_moon = tk.Label(sw_wrap, text="🌙", font=("Segoe UI", 9))
        self._lbl_moon.pack(side="left", padx=(0,4))
        self._sw = ToggleSwitch(sw_wrap, self.var_theme, command=self._toggle_theme)
        self._sw.pack(side="left")
        self._lbl_sun = tk.Label(sw_wrap, text="☀️", font=("Segoe UI", 9))
        self._lbl_sun.pack(side="left", padx=(4,0))
        self._sw_wrap = sw_wrap

        # Separador sutil
        self._top_sep = tk.Frame(root_f, height=1)
        self._top_sep.grid(row=1, column=0, sticky="ew")

        # CONTENIDO PRINCIPAL
        body=tk.Frame(root_f); body.grid(row=1,column=0,sticky="nsew",padx=15,pady=(15,5))
        body.rowconfigure(0,weight=1); body.columnconfigure(0,weight=3,minsize=400); body.columnconfigure(1,weight=0,minsize=320)
        self._body=body

        self._build_left(body)
        self._build_right(body)
        self._build_bottom(root_f)

    def _build_left(self,parent):
        lf=tk.Frame(parent); lf.grid(row=0,column=0,sticky="nsew",padx=(0,12))
        lf.rowconfigure(1,weight=1); lf.columnconfigure(0,weight=1)
        self._lf=lf

        topbar=tk.Frame(lf); topbar.grid(row=0,column=0,sticky="ew",pady=(0,6))
        topbar.columnconfigure(0,weight=1)
        self._lbl_title=tk.Label(topbar,text="",font=("Segoe UI",10,"bold"),anchor="w")
        self._lbl_title.grid(row=0,column=0,sticky="w")
        self._lbl_info=tk.Label(topbar,text="",font=("Segoe UI",9),anchor="e")
        self._lbl_info.grid(row=0,column=1,sticky="e")

        cvf=tk.Frame(lf,highlightthickness=1)
        cvf.grid(row=1,column=0,sticky="nsew"); cvf.rowconfigure(0,weight=1); cvf.columnconfigure(0,weight=1)
        self._cvf=cvf
        self.canvas=tk.Canvas(cvf,highlightthickness=0,bd=0,cursor="crosshair")
        self.canvas.grid(sticky="nsew")
        self.canvas.bind("<Configure>",lambda e:self._draw_main())
        self.canvas.bind("<Button-1>",self._click)
        self.canvas.bind("<B1-Motion>",self._click)

        self._lbl_hint=tk.Label(lf,text="",font=("Segoe UI",8),anchor="w")
        self._lbl_hint.grid(row=2,column=0,sticky="w",pady=(4,0))

    def _build_right(self,parent):
        rf=tk.Frame(parent); rf.grid(row=0,column=1,sticky="nsew")
        rf.columnconfigure(0,weight=1); rf.rowconfigure(2,weight=1)   
        self._rf2=rf

        PAD={"sticky":"ew","pady":(0,8),"padx":0}

        # 1. Cargar imagen
        r1=self._section(rf,""); r1.grid(row=0,column=0,**PAD)
        self.btn_load=self._abtn(r1.body,"",self.load_image)
        self.btn_load.grid(sticky="ew")
        self._lbl_fn=tk.Label(r1.body,text="",font=("Segoe UI",8),anchor="w")
        self._lbl_fn.grid(sticky="w",pady=(4,0))

        # 2. Centro X / Y
        r2=self._section(rf,""); r2.grid(row=1,column=0,**PAD)
        self._lbl_ctr=tk.Label(r2.body,text="—",font=("Segoe UI",8),anchor="w")
        self._lbl_ctr.grid(row=0,column=0,columnspan=3,sticky="w",pady=(0,4))
        r2.body.columnconfigure(2,weight=1)
        
        self._lbl_x_axis = tk.Label(r2.body,text="X",font=("Segoe UI",8,"bold"),width=1)
        self._lbl_x_axis.grid(row=1,column=0,sticky="w")
        self._slx=ttk.Scale(r2.body,from_=0,to=1,orient="h",variable=self.var_cx,command=self._sl_x)
        self._slx.grid(row=1,column=1,columnspan=2,sticky="ew",padx=(6,0))
        
        self._lbl_y_axis = tk.Label(r2.body,text="Y",font=("Segoe UI",8,"bold"),width=1)
        self._lbl_y_axis.grid(row=2,column=0,sticky="w",pady=(4,0))
        self._sly=ttk.Scale(r2.body,from_=0,to=1,orient="h",variable=self.var_cy,command=self._sl_y)
        self._sly.grid(row=2,column=1,columnspan=2,sticky="ew",padx=(6,0),pady=(4,0))
        
        self._btn_rst=self._fbtn(r2.body,"",self.reset_center)
        self._btn_rst.grid(row=3,column=0,columnspan=3,sticky="ew",pady=(6,0))

        # 3. Preview panorama_0
        r3=self._section(rf,""); r3.grid(row=2,column=0,sticky="nsew",pady=(0,8))
        r3.body.rowconfigure(0,weight=1); r3.body.columnconfigure(0,weight=1)
        self._cv_p0=tk.Canvas(r3.body,highlightthickness=1,bd=0)
        self._cv_p0.grid(row=0,column=0,sticky="nsew")
        self._cv_p0.bind("<Configure>",lambda e:self._p0_placeholder())

        # 4. Resolución
        r4=self._section(rf,""); r4.grid(row=3,column=0,**PAD)
        r4.body.columnconfigure(1,weight=1); r4.body.columnconfigure(3,weight=1)
        self._lbl_w_title = tk.Label(r4.body,text="",font=("Segoe UI",8))
        self._lbl_w_title.grid(row=0,column=0,sticky="w")
        ttk.Entry(r4.body,textvariable=self.var_w,width=6,font=("Segoe UI",8)).grid(row=0,column=1,sticky="ew",padx=(5,10))
        self._lbl_h_title = tk.Label(r4.body,text="",font=("Segoe UI",8))
        self._lbl_h_title.grid(row=0,column=2,sticky="w")
        ttk.Entry(r4.body,textvariable=self.var_h,width=6,font=("Segoe UI",8)).grid(row=0,column=3,sticky="ew",padx=(5,0))
        self._lbl_restip=tk.Label(r4.body,text="",font=("Segoe UI",8),anchor="w")
        self._lbl_restip.grid(row=1,column=0,columnspan=4,sticky="w",pady=(4,0))

        # 5. Carpeta de salida
        r5=self._section(rf,""); r5.grid(row=4,column=0,**PAD)
        r5.body.columnconfigure(0,weight=1)
        orow=tk.Frame(r5.body); orow.grid(sticky="ew"); orow.columnconfigure(0,weight=1)
        self._entry_out=ttk.Entry(orow,textvariable=self.var_out,font=("Segoe UI",8))
        self._entry_out.grid(row=0,column=0,sticky="ew")
        self._fbtn(orow,"📁",self.choose_folder,w=3).grid(row=0,column=1,padx=(4,0))
        self._fbtn(orow,"↺",self.clear_folder,w=3).grid(row=0,column=2,padx=(2,0))
        self._lbl_outinfo=tk.Label(r5.body,text="",font=("Segoe UI",8),anchor="w",wraplength=290,justify="left")
        self._lbl_outinfo.grid(sticky="w",pady=(4,0))

        self._sections=[r1,r2,r3,r4,r5]

    def _build_bottom(self,parent):
        bar=tk.Frame(parent)
        bar.grid(row=2,column=0,sticky="ew",padx=15,pady=(0,12))
        bar.columnconfigure(0,weight=1)
        self._bar=bar

        left=tk.Frame(bar); left.grid(row=0,column=0,sticky="ew"); left.columnconfigure(0,weight=1)
        self._prog=ttk.Progressbar(left,mode="determinate",maximum=6)
        self._prog.grid(row=0,column=0,sticky="ew")
        self._lbl_st=tk.Label(left,text="",font=("Segoe UI",9),anchor="w")
        self._lbl_st.grid(row=1,column=0,sticky="w",pady=(3,0))

        self.btn_gen=tk.Button(bar,text="",font=("Segoe UI",10,"bold"),relief="flat",bd=0,cursor="hand2",padx=20,pady=10,command=self.start_gen)
        self.btn_gen.grid(row=0,column=1,padx=(12,0))

    class _Sec(tk.Frame):
        def __init__(self,parent,title,**kw):
            super().__init__(parent,highlightthickness=1,**kw)
            self.columnconfigure(0,weight=1)
            hdr=tk.Frame(self); hdr.grid(row=0,column=0,sticky="ew")
            hdr.columnconfigure(0,weight=1)
            self._hdr=hdr
            self._lbl=tk.Label(hdr,text=title,font=("Segoe UI",9,"bold"),anchor="w",padx=8,pady=4)
            self._lbl.grid(row=0,column=0,sticky="w")
            self.body=tk.Frame(self,padx=10,pady=8)
            self.body.grid(row=1,column=0,sticky="nsew")
            self.rowconfigure(1,weight=1); self.body.columnconfigure(0,weight=1)

    def _section(self,parent,title):
        return self._Sec(parent,title)

    def _abtn(self,parent,text,cmd):
        btn = tk.Button(parent,text=text,font=("Segoe UI",9,"bold"),relief="flat",bd=0,cursor="hand2",pady=6,command=cmd)
        return btn

    def _fbtn(self,parent,text,cmd,w=None):
        kw={"width":w} if w else {}
        btn = tk.Button(parent,text=text,font=("Segoe UI",8),relief="flat",bd=0,cursor="hand2",pady=4,command=cmd,**kw)
        return btn

    # ──────────────────────────────────────────────────────────
    #  SISTEMA AUXILIAR DE ANIMACIONES HOVER FADE
    # ──────────────────────────────────────────────────────────
    def _bind_hover_fade(self, widget, normal_hex, hover_hex):
        widget.bind("<Enter>", lambda e: animate_color(widget, normal_hex, hover_hex, steps=8))
        widget.bind("<Leave>", lambda e: animate_color(widget, hover_hex, normal_hex, steps=8))

    # Animación de respiración sutil "PULSE" para el botón de Generar
    def _pulse_animation(self):
        if not hasattr(self, 'btn_gen') or not self.btn_gen.winfo_exists(): return
        t = self.t()
        
        # Solo aplicar pulso si el botón está activo/habilitado
        if str(self.btn_gen['state']) == 'normal':
            self._pulse_val += 0.04 * self._pulse_direction
            if self._pulse_val >= 1.0:
                self._pulse_val = 1.0
                self._pulse_direction = -1
            elif self._pulse_val <= 0.0:
                self._pulse_val = 0.0
                self._pulse_direction = 1

            # Interpolación entre Verde normal y un tono un poco más brillante/neon
            # O Azul si está en modo claro
            start_hex = t["accent"]
            glow_hex = "#4ade80" if self._tn == "dark" else "#22c55e"
            
            def apply_pulse(current_hex):
                if str(self.btn_gen['state']) == 'normal':
                    self.btn_gen.configure(bg=current_hex)

            animate_color(self.btn_gen, start_hex, glow_hex, steps=1, current_step=int(self._pulse_val*10), callback=apply_pulse)

        self.root.after(80, self._pulse_animation)

    # ──────────────────────────────────────────────────────────
    #  INTERNACIONALIZACIÓN DINÁMICA
    # ──────────────────────────────────────────────────────────
    def _update_ui_strings(self):
        self._lbl_title.configure(text=self.loc("title_preview"))
        if self.image_path:
            self._lbl_fn.configure(text=os.path.basename(self.image_path))
        else:
            self._lbl_fn.configure(text=self.loc("no_file"))
            self._lbl_info.configure(text=self.loc("no_image"))
            self._lbl_st.configure(text=self.loc("lbl_status_ready"))

        self._lbl_hint.configure(text=self.loc("hint_click"))
        
        self._sections[0]._lbl.configure(text=self.loc("sec_image"))
        self.btn_load.configure(text=self.loc("btn_load"))
        
        self._sections[1]._lbl.configure(text=self.loc("sec_center"))
        self._btn_rst.configure(text=self.loc("btn_reset"))
        
        self._sections[2]._lbl.configure(text=self.loc("sec_preview_p0"))
        
        self._sections[3]._lbl.configure(text=self.loc("sec_res"))
        self._lbl_w_title.configure(text=self.loc("lbl_width"))
        self._lbl_h_title.configure(text=self.loc("lbl_height"))
        self._lbl_restip.configure(text=self.loc("lbl_restip"))
        
        self._sections[4]._lbl.configure(text=self.loc("sec_out"))
        self._lbl_outinfo.configure(text=self.loc("lbl_outinfo"))
        
        self.btn_gen.configure(text=self.loc("btn_generate"))
        self.btn_youtube.configure(text=self.loc("btn_youtube"))
        self.btn_lang.configure(text="🇪🇸 ES" if self._lang == "en" else "🇬🇧 EN")
        
        self._upd_ctr()
        self._sched_p0(d=50)

    def _toggle_language(self):
        self._lang = "en" if self._lang == "es" else "es"
        self._update_ui_strings()

    # ──────────────────────────────────────────────────────────
    #  TEMA Y ESTILOS
    # ──────────────────────────────────────────────────────────
    def _theme(self):
        t=self.t()
        def bg(w,c): 
            try: w.configure(bg=c)
            except: pass

        for w in (self.root,self._rf,self._body,self._lf,self._rf2,self._bar,self._top_util):
            bg(w,t["bg"])

        self._top_sep.configure(bg=t["border"])
        self._cvf.configure(highlightbackground=t["border"])
        self.canvas.configure(bg=t["canvas_bg"])

        for lbl in (self._lbl_title, self._lbl_moon, self._lbl_sun): lbl.configure(bg=t["bg"],fg=t["fg"])
        for lbl in (self._lbl_info,self._lbl_hint,self._lbl_st): lbl.configure(bg=t["bg"],fg=t["fg2"])

        for sec in self._sections:
            sec.configure(bg=t["surface"],highlightbackground=t["border"])
            sec._hdr.configure(bg=t["surface"])
            sec._lbl.configure(bg=t["surface"],fg=t["fg"])
            sec.body.configure(bg=t["surface"])
            self._recurse(sec.body,t)

        for lbl in (self._lbl_fn,self._lbl_ctr,self._lbl_restip,self._lbl_outinfo, self._lbl_w_title, self._lbl_h_title, self._lbl_x_axis, self._lbl_y_axis):
            lbl.configure(bg=t["surface"],fg=t["fg2"])

        # Asignar colores base e inyectar animaciones dinámicas de transición
        self.btn_load.configure(bg=t["surface2"],fg=t["fg"],activebackground=t["border"],activeforeground=t["fg"])
        self._bind_hover_fade(self.btn_load, t["surface2"], t["border"])

        self._btn_rst.configure(bg=t["surface2"],fg=t["fg"],activebackground=t["border"],activeforeground=t["fg"])
        self._bind_hover_fade(self._btn_rst, t["surface2"], t["border"])

        self.btn_donate.configure(bg="#e8407a",fg="#fff",activebackground="#c03060")
        self.btn_youtube.configure(bg="#ff0000",fg="#fff",activebackground="#b30000")

        self.btn_lang.configure(bg=t["surface2"],fg=t["fg"],activebackground=t["border"],activeforeground=t["fg"])
        self._bind_hover_fade(self.btn_lang, t["surface2"], t["border"])

        self.btn_gen.configure(bg=t["accent"],fg=t["accent_fg"],activebackground=t["accent_dim"],activeforeground=t["accent"])

        self._cv_p0.configure(bg=t["canvas_bg"],highlightbackground=t["border"])
        self._sw.recolor(t["sw_on"],t["sw_off"],t["sw_k"],t["bg"])
        self._sw_wrap.configure(bg=t["bg"])

        s=self.style
        s.configure("TScale",background=t["surface"],troughcolor=t["surface2"],sliderlength=10)
        s.configure("TEntry",fieldbackground=t["surface2"],foreground=t["fg"],insertcolor=t["fg"],borderwidth=0,padding=3)
        s.configure("Horizontal.TProgressbar",background=t["accent"],troughcolor=t["surface2"],borderwidth=0)

        self._update_ui_strings()
        self._draw_main()

    def _recurse(self,w,t):
        for c in w.winfo_children():
            try:
                if c.winfo_class() in ("Frame","Label"):
                    c.configure(bg=t["surface"])
                    if c.winfo_class()=="Label": c.configure(fg=t["fg"])
            except: pass
            self._recurse(c,t)

    def _toggle_theme(self):
        self._tn="light" if self.var_theme.get() else "dark"
        self._theme()

    def _cycle_donate(self):
        self._didx=(self._didx+1)%len(DONATE_MSGS[self._lang])
        try: self.btn_donate.configure(text=DONATE_MSGS[self._lang][self._didx])
        except: pass
        self.root.after(5000,self._cycle_donate)

    # ──────────────────────────────────────────────────────────
    #  LÓGICA OPERACIONAL
    # ──────────────────────────────────────────────────────────
    def load_image(self):
        path=filedialog.askopenfilename(title=self.loc("title_preview"),
            filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),("All","*.*")])
        if not path: return
        try: img=Image.open(path).convert("RGB")
        except Exception as e: messagebox.showerror(self.loc("err_title"),str(e)); return
        self.image_path=path; self.full_array=np.array(img)
        self.center_x=self.full_array.shape[1]/2; self.center_y=self.full_array.shape[0]/2
        self.var_cx.set(0.5); self.var_cy.set(0.5)
        mx=1600
        self.preview_image=img.resize((mx,int(img.height*mx/img.width)),Image.LANCZOS) if img.width>mx else img
        self._lbl_fn.configure(text=os.path.basename(path))
        self._lbl_info.configure(text=f"{img.width}×{img.height} px")
        self._upd_ctr(); self._draw_main(); self._sched_p0()
        self._lbl_st.configure(text=self.loc("lbl_status_loaded"))

    def reset_center(self):
        if self.full_array is None: return
        self.center_x=self.full_array.shape[1]/2; self.center_y=self.full_array.shape[0]/2
        self.var_cx.set(0.5); self.var_cy.set(0.5)
        self._upd_ctr(); self._draw_main(); self._sched_p0()

    def _upd_ctr(self):
        if self.full_array is None: self._lbl_ctr.configure(text="—"); return
        w,h=self.full_array.shape[1],self.full_array.shape[0]
        self._lbl_ctr.configure(
            text=f"X = {int(self.center_x)} px ({self.center_x/w*360:.0f}°)  "
                 f"Y = {int(self.center_y)} px ({self.center_y/h*100:.0f}%)")

    def _sl_x(self,_=None):
        if self.full_array is None: return
        self.center_x=self.var_cx.get()*self.full_array.shape[1]
        self._upd_ctr(); self._draw_main(); self._sched_p0()
        
    def _sl_y(self,_=None):
        if self.full_array is None: return
        self.center_y=self.var_cy.get()*self.full_array.shape[0]
        self._upd_ctr(); self._draw_main(); self._sched_p0()

    def _draw_main(self):
        c=self.canvas; c.delete("all")
        cw,ch=c.winfo_width(),c.winfo_height()
        if cw<2 or ch<2: return
        t=self.t()
        if self.preview_image is None:
            c.create_text(cw//2,ch//2,text=self.loc("lbl_status_ready"),fill=t["fg2"],font=("Segoe UI",10)); return
        iw,ih=self.preview_image.size
        sc=min(cw/iw,ch/ih); dw,dh=max(1,int(iw*sc)),max(1,int(ih*sc))
        x0,y0=(cw-dw)//2,(ch-dh)//2
        res=self.preview_image.resize((dw,dh),Image.LANCZOS)
        self.preview_tk=ImageTk.PhotoImage(res)
        c.create_image(x0,y0,image=self.preview_tk,anchor="nw")
        self.canvas_box=(x0,y0,x0+dw,y0+dh)
        if self.center_x is not None:
            fx=self.center_x/self.full_array.shape[1]
            fy=self.center_y/self.full_array.shape[0]
            lx=x0+fx*dw; ly=y0+fy*dh
            c.create_line(lx,y0,lx,y0+dh,fill="#ff453a",width=1,dash=(4,4))
            c.create_line(x0,ly,x0+dw,ly,fill="#ff453a",width=1,dash=(4,4))
            c.create_oval(lx-6,ly-6,lx+6,ly+6,outline="#ff453a",width=1.5)
            c.create_text(lx+10,ly-10,text="CENTER",fill="#ff453a",font=("Segoe UI",8,"bold"),anchor="w")

    def _click(self,e):
        if self.full_array is None or self.canvas_box is None: return
        x0,y0,x1,y1=self.canvas_box
        if not(x0<=e.x<=x1 and y0<=e.y<=y1): return
        fx=(e.x-x0)/(x1-x0); fy=(e.y-y0)/(y1-y0)
        fx,fy=max(0,min(1,fx)),max(0,min(1,fy))
        self.center_x=fx*self.full_array.shape[1]; self.center_y=fy*self.full_array.shape[0]
        self.var_cx.set(fx); self.var_cy.set(fy)
        self._upd_ctr(); self._draw_main(); self._sched_p0()

    def _p0_placeholder(self):
        c=self._cv_p0; c.delete("all")
        cw,ch=c.winfo_width(),c.winfo_height()
        if cw<4 or ch<4: return
        c.create_text(cw//2,ch//2,text=self.loc("preview_placeholder"),fill=self.t()["fg2"],font=("Segoe UI",9))

    def _sched_p0(self,d=280):
        if self._ptimer: self.root.after_cancel(self._ptimer)
        self._ptimer=self.root.after(d,self._upd_p0)

    def _upd_p0(self):
        self._ptimer=None
        if self.full_array is None: self._p0_placeholder(); return
        c=self._cv_p0; cw,ch=c.winfo_width(),c.winfo_height()
        if cw<4 or ch<4: self.root.after(200,self._upd_p0); return
        try:
            sf=max(1,self.full_array.shape[1]//600)
            sm=self.full_array[::sf,::sf]
            rolled=recenter(sm,self.center_x/sf,self.center_y/sf)
            res=min(cw,ch)-4
            fa=generate_face(rolled,"panorama_0",res,res)
            img=Image.fromarray(fa).resize((cw-2,ch-2),Image.LANCZOS)
            self.p0_tk=ImageTk.PhotoImage(img)
            c.delete("all")
            c.create_image(cw//2,ch//2,image=self.p0_tk,anchor="center")
            c.create_text(cw//2,ch-8,text=f"panorama_0 ({FACE_LABELS[self._lang]['panorama_0']})",fill=self.t()["accent"],font=("Segoe UI",8,"bold"))
        except: self._p0_placeholder()

    def choose_folder(self):
        d=filedialog.askdirectory(title=self.loc("sec_out"))
        if d: self.var_out.set(d)
        
    def clear_folder(self): self.var_out.set("")

    def _get_folder(self):
        m=self.var_out.get().strip()
        if m: return m
        name=os.path.splitext(os.path.basename(self.image_path))[0] if self.image_path else "output"
        base=os.path.dirname(sys.executable) if getattr(sys,'frozen',False) else os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base,name)

    def start_gen(self):
        if self.full_array is None:
            messagebox.showwarning(self.loc("warn_no_img_title"),self.loc("warn_no_img_msg")); return
        try:
            ow,oh=int(self.var_w.get()),int(self.var_h.get())
            assert 0<ow<=8192 and 0<oh<=8192
        except:
            messagebox.showerror(self.loc("err_res_title"),self.loc("err_res_msg")); return
        folder=self._get_folder()
        try: os.makedirs(folder,exist_ok=True)
        except Exception as e: messagebox.showerror(self.loc("err_title"),str(e)); return
        self.btn_gen.configure(state="disabled"); self.btn_load.configure(state="disabled")
        self._prog.configure(value=0)
        self._lbl_st.configure(text=f"{self.loc('status_generating')}{folder}")
        threading.Thread(target=self._worker,args=(ow,oh,folder),daemon=True).start()

    def _worker(self,ow,oh,folder):
        try:
            rolled=recenter(self.full_array,self.center_x,self.center_y)
            paths=[]
            for i,k in enumerate(FACE_ORDER):
                arr=generate_face(rolled,k,ow,oh)
                p=os.path.join(folder,f"{k}.png")
                Image.fromarray(arr).save(p); paths.append((k,p))
                self.root.after(0,self._prog_upd,i+1,k)
            self.root.after(0,self._done,paths,folder)
        except Exception as e:
            self.root.after(0,self._err,str(e),traceback.format_exc())

    def _prog_upd(self,n,k):
        self._prog.configure(value=n)
        label_face = FACE_LABELS[self._lang].get(k,'')
        self._lbl_st.configure(text=self.loc("status_gen_step").format(n, k, label_face))

    def _done(self,paths,folder):
        self.btn_gen.configure(state="normal"); self.btn_load.configure(state="normal")
        self._lbl_st.configure(text=self.loc("status_done"))
        self._show_results(paths)
        messagebox.showinfo(self.loc("msg_done_title"),self.loc("msg_done_msg").format(folder))

    def _err(self,msg,tb):
        self.btn_gen.configure(state="normal"); self.btn_load.configure(state="normal")
        self._lbl_st.configure(text=self.loc("status_err"))
        print(tb); messagebox.showerror(self.loc("err_title"),msg)

    def _show_results(self,paths):
        t=self.t()
        if hasattr(self,'_thumb_row') and self._thumb_row is not None:
            try: self._thumb_row.destroy()
            except: pass
        self.thumb_refs=[]
        self._thumb_row=tk.Frame(self._bar,bg=t["bg"])
        self._thumb_row.grid(row=0,column=2,padx=(8,0))
        for k,p in paths:
            try:
                im=Image.open(p); im.thumbnail((32,32),Image.LANCZOS)
                tki=ImageTk.PhotoImage(im); self.thumb_refs.append(tki)
                lf=tk.Frame(self._thumb_row,bg=t["bg"])
                lf.pack(side="left",padx=2)
                tk.Label(lf,image=tki,bg=t["bg"]).pack()
                tk.Label(lf,text=FACE_LABELS[self._lang].get(k,k)[:3],font=("Segoe UI",7),bg=t["bg"],fg=t["fg2"]).pack()
            except: pass

def main():
    root=tk.Tk()
    
    # ──────────────────────────────────────────────────────────────
    #  INYECCIÓN DEL ICONO MULTIRESOLUCIÓN EN LA VENTANA PRINCIPAL
    # ──────────────────────────────────────────────────────────────
    try:
        ruta_icono = obtener_ruta_recurso("icono.ico")
        root.iconbitmap(ruta_icono)
    except Exception:
        pass
        
    PanoramaApp(root)
    root.mainloop()

if __name__=="__main__":
    main()
