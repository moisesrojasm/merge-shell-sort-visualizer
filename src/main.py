import tkinter as tk
import random
import time
import threading

# ─── Colores ─────────────────────────────────────────────────────────────────
COLOR_BASE    = "#378ADD"
COLOR_NIVEL   = ["#1D9E75", "#5DCAA5", "#9FE1CB", "#EF9F27", "#F0997B"]
COLOR_COMPARE = "#E24B4A"
COLOR_MERGE   = "#D4537E"
COLOR_DONE    = "#B5D4F4"

# ─── Ventana ──────────────────────────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Visualizador de Ordenamiento")
ventana.geometry("1080x660")
ventana.resizable(True, True)
ventana.configure(bg="#1e1e2e")

# ─── Canvas ───────────────────────────────────────────────────────────────────
canvas = tk.Canvas(ventana, width=1020, height=340, bg="#12121f", highlightthickness=0)
canvas.pack(padx=20, pady=(14, 4))

# ─── Estado ───────────────────────────────────────────────────────────────────
arreglo_actual = []
pasos          = []
paso_idx       = 0
reproduciendo  = False
algoritmo      = tk.StringVar(value="merge")

var_tamano        = tk.IntVar(value=30)
var_velocidad     = tk.IntVar(value=5)
var_comparaciones = tk.StringVar(value="0")
var_intercambios  = tk.StringVar(value="0")
var_info_extra    = tk.StringVar(value="")

# ─── Dibujar ──────────────────────────────────────────────────────────────────
def dibujar(arr, colores=None):
    canvas.delete("all")
    if not arr:
        return
    W   = canvas.winfo_width()  or 1020
    H   = canvas.winfo_height() or 340
    n   = len(arr)
    bw  = W / n
    mx  = max(arr) or 1
    if colores is None:
        colores = [COLOR_BASE] * n
    for i, v in enumerate(arr):
        bh = max(2, int((v / mx) * (H - 4)))
        x1, y1 = i * bw + 0.5, H - bh
        x2, y2 = (i + 1) * bw - 0.5, H
        canvas.create_rectangle(x1, y1, x2, y2, fill=colores[i], outline="")
    ventana.update_idletasks()

# ─── Merge Sort ───────────────────────────────────────────────────────────────
def construir_merge(arr_entrada):
    pasos_l = []
    a    = list(arr_entrada)
    cols = [COLOR_BASE] * len(a)
    cmps = [0]; swps = [0]

    def snap(gap=None):
        pasos_l.append((list(a), list(cols), cmps[0], swps[0], gap))

    def ms(l, r, depth):
        if r - l <= 1:
            return
        mid  = (l + r) // 2
        lc   = COLOR_NIVEL[min(depth, len(COLOR_NIVEL) - 1)]
        for i in range(l, r):
            cols[i] = lc
        snap()
        ms(l, mid, depth + 1)
        ms(mid, r,  depth + 1)
        for i in range(l, r):
            cols[i] = COLOR_MERGE
        snap()
        L, R = a[l:mid], a[mid:r]
        i = j = 0; k = l
        while i < len(L) and j < len(R):
            cmps[0] += 1
            if L[i] <= R[j]:
                a[k] = L[i]; i += 1
            else:
                a[k] = R[j]; j += 1; swps[0] += 1
            cols[k] = COLOR_COMPARE; snap(); cols[k] = COLOR_MERGE; k += 1
        while i < len(L):  a[k] = L[i]; i += 1; k += 1
        while j < len(R):  a[k] = R[j]; j += 1; k += 1
        for x in range(l, r):
            cols[x] = COLOR_DONE
        snap()

    snap()
    ms(0, len(a), 0)
    for x in range(len(a)):
        cols[x] = COLOR_DONE
    snap()
    return pasos_l

# ─── Shell Sort ───────────────────────────────────────────────────────────────
def construir_shell(arr_entrada):
    pasos_l = []
    a    = list(arr_entrada)
    n    = len(a)
    cols = [COLOR_BASE] * n
    cmps = [0]; swps = [0]

    def snap(gap=0):
        pasos_l.append((list(a), list(cols), cmps[0], swps[0], gap))

    # Secuencia de Knuth: 1, 4, 13, 40, 121...
    gaps = []
    g = 1
    while g < n:
        gaps.append(g); g = g * 3 + 1
    total_gaps = len(gaps)

    snap(gaps[-1] if gaps else 1)

    for gi in range(len(gaps) - 1, -1, -1):
        gap      = gaps[gi]
        lv_color = COLOR_NIVEL[min(total_gaps - 1 - gi, len(COLOR_NIVEL) - 1)]
        for i in range(gap, n):
            tmp = a[i]; j = i
            cols[i] = COLOR_COMPARE; snap(gap)
            while j >= gap:
                cmps[0] += 1
                cols[j - gap] = COLOR_COMPARE; snap(gap)
                if a[j - gap] > tmp:
                    a[j] = a[j - gap]; swps[0] += 1
                    cols[j] = COLOR_MERGE; cols[j - gap] = lv_color
                    snap(gap); j -= gap
                else:
                    cols[j - gap] = lv_color; snap(gap); break
            a[j] = tmp
            cols[j] = lv_color; snap(gap)
        # limpiar colores residuales
        for x in range(n):
            if cols[x] in (COLOR_COMPARE, COLOR_MERGE):
                cols[x] = lv_color
        snap(gap)

    for x in range(n):
        cols[x] = COLOR_DONE
    snap(0)
    return pasos_l

# ─── Aplicar paso ─────────────────────────────────────────────────────────────
def aplicar_paso(idx):
    if not pasos:
        return
    idx = min(idx, len(pasos) - 1)
    arr, cols, cmp, swp, extra = pasos[idx]
    dibujar(arr, cols)
    var_comparaciones.set(str(cmp))
    var_intercambios.set(str(swp))
    if algoritmo.get() == "shell" and extra is not None and extra > 0:
        var_info_extra.set(f"Gap: {extra}")
    else:
        var_info_extra.set("")

# ─── Inicializar ──────────────────────────────────────────────────────────────
def iniciar(tipo="aleatorio"):
    global arreglo_actual, pasos, paso_idx, reproduciendo
    detener()
    n = var_tamano.get()
    if tipo == "ordenado":
        arreglo_actual = [int(10 + (i / max(n - 1, 1)) * 90) for i in range(n)]
    elif tipo == "invertido":
        arreglo_actual = [int(10 + (i / max(n - 1, 1)) * 90) for i in range(n - 1, -1, -1)]
    else:
        arreglo_actual = [random.randint(10, 100) for _ in range(n)]

    if algoritmo.get() == "shell":
        pasos = construir_shell(arreglo_actual)
    else:
        pasos = construir_merge(arreglo_actual)

    paso_idx = 0
    aplicar_paso(0)
    actualizar_botones()

# ─── Controles de reproducción ────────────────────────────────────────────────
def obtener_delay():
    v = var_velocidad.get()
    return max(10, int(600 / (v * v * 0.4 + 0.6)))

def detener():
    global reproduciendo
    reproduciendo = False
    btn_play.config(text="▶  Reproducir")
    actualizar_botones()

def paso_adelante():
    global paso_idx
    if paso_idx < len(pasos) - 1:
        paso_idx += 1
        aplicar_paso(paso_idx)
        actualizar_botones()

def toggle_play():
    global reproduciendo, paso_idx
    if reproduciendo:
        detener(); return
    if paso_idx >= len(pasos) - 1:
        paso_idx = 0
    reproduciendo = True
    btn_play.config(text="⏸  Pausar")
    btn_step.config(state="disabled")
    threading.Thread(target=loop_reproduccion, daemon=True).start()

def loop_reproduccion():
    global paso_idx, reproduciendo
    while reproduciendo and paso_idx < len(pasos) - 1:
        paso_idx += 1
        aplicar_paso(paso_idx)
        time.sleep(obtener_delay() / 1000)
    detener()

def actualizar_botones():
    fin = paso_idx >= len(pasos) - 1 if pasos else True
    btn_step.config(state="disabled" if (fin or reproduciendo) else "normal")
    btn_play.config(state="disabled" if fin else "normal")

def cambiar_algoritmo():
    iniciar("aleatorio")

# ─── UI ───────────────────────────────────────────────────────────────────────
BG    = "#1e1e2e"
LBL   = {"bg": BG, "fg": "#aaaacc", "font": ("Courier", 10)}
BTN   = {"bg": "#2a2a3e", "fg": "#e0e0f0", "font": ("Courier", 10),
         "relief": "flat", "padx": 9, "pady": 3, "cursor": "hand2",
         "activebackground": "#3a3a5e", "activeforeground": "#ffffff"}

# Selector de algoritmo
sel_frame = tk.Frame(ventana, bg=BG)
sel_frame.pack(padx=20, pady=(0, 4), fill="x")

tk.Label(sel_frame, text="Algoritmo:", **LBL).pack(side="left", padx=(0, 6))
rb_merge = tk.Radiobutton(sel_frame, text="Merge Sort", variable=algoritmo, value="merge",
    command=cambiar_algoritmo, bg=BG, fg="#e0e0f0", selectcolor="#3a3a5e",
    activebackground=BG, font=("Courier", 10))
rb_merge.pack(side="left", padx=(0, 12))
rb_shell = tk.Radiobutton(sel_frame, text="Shell Sort", variable=algoritmo, value="shell",
    command=cambiar_algoritmo, bg=BG, fg="#e0e0f0", selectcolor="#3a3a5e",
    activebackground=BG, font=("Courier", 10))
rb_shell.pack(side="left")

# Fila controles
ctrl = tk.Frame(ventana, bg=BG)
ctrl.pack(padx=20, pady=6, fill="x")

fila1 = tk.Frame(ctrl, bg=BG)
fila1.pack(fill="x", pady=2)

tk.Label(fila1, text="Tamaño:", **LBL).pack(side="left")
tk.Scale(fila1, from_=5, to=80, orient="horizontal", variable=var_tamano, length=110,
    bg=BG, fg="#e0e0f0", troughcolor="#3a3a5e", highlightthickness=0,
    command=lambda _: iniciar("aleatorio")).pack(side="left", padx=(2, 14))

tk.Label(fila1, text="Velocidad:", **LBL).pack(side="left")
tk.Scale(fila1, from_=1, to=10, orient="horizontal", variable=var_velocidad, length=110,
    bg=BG, fg="#e0e0f0", troughcolor="#3a3a5e", highlightthickness=0).pack(side="left", padx=(2, 16))

tk.Label(fila1, text="Comparaciones:", **LBL).pack(side="left")
tk.Label(fila1, textvariable=var_comparaciones, bg=BG, fg="#5DCAA5",
    font=("Courier", 10, "bold"), width=5).pack(side="left")
tk.Label(fila1, text=" Intercambios:", **LBL).pack(side="left")
tk.Label(fila1, textvariable=var_intercambios, bg=BG, fg="#EF9F27",
    font=("Courier", 10, "bold"), width=5).pack(side="left")
tk.Label(fila1, textvariable=var_info_extra, bg=BG, fg="#D4537E",
    font=("Courier", 10, "bold"), width=10).pack(side="left")

fila2 = tk.Frame(ctrl, bg=BG)
fila2.pack(fill="x", pady=3)

btn_play = tk.Button(fila2, text="▶  Reproducir", command=toggle_play,
    **{**BTN, "bg": "#185FA5", "fg": "#B5D4F4"})
btn_play.pack(side="left", padx=(0, 6))

btn_step = tk.Button(fila2, text="Paso →", command=paso_adelante, **BTN)
btn_step.pack(side="left", padx=(0, 6))

tk.Button(fila2, text="↺ Reiniciar",  command=lambda: iniciar("aleatorio"), **BTN).pack(side="left", padx=(0, 14))
tk.Button(fila2, text="Aleatorio",    command=lambda: iniciar("aleatorio"), **BTN).pack(side="left", padx=(0, 4))
tk.Button(fila2, text="Ordenado",     command=lambda: iniciar("ordenado"),  **BTN).pack(side="left", padx=(0, 4))
tk.Button(fila2, text="Invertido",    command=lambda: iniciar("invertido"), **BTN).pack(side="left")

# Leyenda
ley = tk.Frame(ventana, bg=BG)
ley.pack(padx=20, pady=(0, 8), fill="x")

items = [
    (COLOR_BASE,    "sin procesar"),
    (COLOR_NIVEL[0],"nivel 0 / gap grande"),
    (COLOR_NIVEL[1],"nivel 1 / gap medio"),
    (COLOR_NIVEL[2],"nivel 2"),
    (COLOR_NIVEL[3],"nivel 3+"),
    (COLOR_COMPARE, "comparando"),
    (COLOR_MERGE,   "fusionando/moviendo"),
    (COLOR_DONE,    "ordenado"),
]
for color, texto in items:
    tk.Label(ley, text="■", fg=color, bg=BG, font=("Courier", 11)).pack(side="left")
    tk.Label(ley, text=texto + "  ", bg=BG, fg="#888899", font=("Courier", 9)).pack(side="left")

# ─── Arranque ─────────────────────────────────────────────────────────────────
ventana.after(100, lambda: iniciar("aleatorio"))
ventana.mainloop()
