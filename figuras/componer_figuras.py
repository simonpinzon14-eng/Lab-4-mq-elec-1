#!/usr/bin/env python3
"""Compone las capturas reales de LVSIM (figuras/lvsim_capturas) en figuras
legibles por actividad (figuras/lvsim/*.png): banco recortado + ventana de medicion."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent
SRC = B / "lvsim_capturas"
DST = B / "lvsim"
DST.mkdir(exist_ok=True)

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
except OSError:
    FONT = ImageFont.load_default()


def img(name, box=None):
    im = Image.open(SRC / name).convert("RGB")
    return im.crop(box) if box else im


def label(im, text, band=None):
    """Agrega una franja blanca superior con el rotulo (no tapa la captura)."""
    band = band or max(48, im.width // 22)
    out = Image.new("RGB", (im.width, im.height + band), "white")
    out.paste(im, (0, band))
    d = ImageDraw.Draw(out)
    size = int(band * 0.7)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        f = FONT
    d.text((8, (band - size) // 2 - 2), text, fill="black", font=f)
    return out


def row(ims, h, gap=16):
    rs = [im.resize((int(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
    W = sum(r.width for r in rs) + gap * (len(rs) - 1)
    out = Image.new("RGB", (W, h), "white")
    x = 0
    for r in rs:
        out.paste(r, (x, 0))
        x += r.width + gap
    return out


def col(ims, w, gap=16):
    rs = [im.resize((w, int(im.height * w / im.width)), Image.LANCZOS) for im in ims]
    H = sum(r.height for r in rs) + gap * (len(rs) - 1)
    out = Image.new("RGB", (w, H), "white")
    y = 0
    for r in rs:
        out.paste(r, (0, y))
        y += r.height + gap
    return out


def save(im, name):
    im.save(DST / name, optimize=True)
    print(name, im.size)


# medidores: recorte de la ventana (sin barra inferior)
MET = (0, 150, 1600, 900)
MET_DC = (0, 150, 540, 650)          # solo E1 e I1 en CC (actividad 1.1)

# ---- Actividad 1.1: resistencia
ohm_box = (0, 0, 520, 1300)
a = label(img("a11_ohm_14_25.png", ohm_box), "a) 1-4 y 2-5")
b = label(img("a11_ohm_36.png", ohm_box), "b) 1-4 y 3-6")
c = label(img("a11_ohm_Y.png", ohm_box), "c) Y: 1-2")
d = label(img("a11_ohm_D.png", ohm_box), "d) Delta: 1-2")
save(row([a, b, c, d], 1100), "a11_ohmetro.png")
vi_b = label(img("a11_vi_bench.png", (40, 540, 1480, 1300)), "a) Banco")
vi_m = label(img("a11_vi_meter.png", MET_DC), "b) Medicion")
save(row([vi_b, vi_m], 760), "a11_voltamperimetrico.png")

# ---- Actividad 1.2: puesta en operacion
BENCH = (0, 60, 1500, 1320)
y_b = label(img("a1_Y_bench.png", BENCH), "Banco, estrella")
y_m = label(img("a1_Y_meter.png", MET), "208 V, secuencia ABC")
save(row([y_b, y_m], 900), "a12_estrella.png")
r1 = label(img("a1_Y_bac_meter.png", MET), "L1<->L2 (BAC)")
r2 = label(img("a1_Y_bca_meter.png", MET), "Ademas L2<->L3 (BCA)")
save(row([r1, r2], 700), "a12_sentido.png")
d_b = label(img("a1_D_bench.png", BENCH), "Banco, delta")
d_m = label(img("a1_D_meter.png", MET), "120 V, secuencia ABC")
save(row([d_b, d_m], 900), "a12_delta.png")

# ---- Actividad 2: vacio y carga
v_b = label(img("a2_bench.png", BENCH), "a) Banco, delta + dinamometro")
v_m = label(img("a2_vacio_meter.png", MET), "b) Vacio a 120 V")
save(row([v_b, v_m], 900), "a2_vacio.png")
c_b = label(img("a2_carga_bench.png", BENCH), "a) Banco con freno")
c_m = label(img("a2_carga_meter.png", MET), "b) Carga, I ~ I nominal")
save(row([c_b, c_m], 900), "a2_carga.png")

# ---- Modulos de LVSIM usados (capturas limpias, sin cables)
dyn = label(img("modulo_DYN.png"), "a) 8960 Dinamometro")
mot = label(img("modulo_MOT.png"), "b) 8221 Motor jaula")
psu = label(img("modulo_PS.png"), "c) 8821 Fuente")
dai = label(img("modulo_DAI.png"), "d) 9063 Interfaz DAI")
save(col([row([dyn, mot], 700), row([psu, dai], 700)], 1600), "equipos_lvsim.png")
