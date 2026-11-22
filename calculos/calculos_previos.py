#!/usr/bin/env python3
"""Calculos previos del preinforme del Laboratorio 4 (maquinas de induccion).

Reproduce los valores de la seccion VII del informe y escribe
calculos/salidas/previos.tex con macros LaTeX (coma decimal via \\num).

Datos de entrada:
  * DL 1021 (jaula de ardilla, banco fisico): catalogo De Lorenzo
      1,1 kW; 220/380 V D/Y; 4,3/2,5 A; 2870 r/min a 50 Hz.
  * DL 1022 (rotor devanado, supuesto para el banco fisico): catalogo De Lorenzo
      1,1 kW; 230/400 V D/Y; 4,3/2,5 A; 2870 r/min a 50 Hz.
  * LabVolt 8221-02 (jaula de ardilla de LVSIM): placa del modulo
      208 V 3F 60 Hz; motor 200 W, FP 0,73, 1685 r/min, 1,14 A; bobinas 120 V.
Los datos de catalogo deben confirmarse contra la placa real del banco.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "salidas"
OUT.mkdir(exist_ok=True)
SQ3 = math.sqrt(3)
macros = {}


def m(nombre, valor, nd=2):
    macros[nombre] = f"\\num{{{valor:.{nd}f}}}"
    return valor


def ns(f, p):
    return 120 * f / p


# ------------------------------------------------------------ LabVolt 8221
f = 60
P = 4
Vn, Pn, fp, nn, In = 208, 200, 0.73, 1685, 1.14
nsinc = m("LVns", ns(f, P), 0)
s = m("LVs", (nsinc - nn) / nsinc * 100, 2)
m("LVfr", s / 100 * f, 2)
S_in = m("LVS", SQ3 * Vn * In, 1)
P_in = m("LVPin", S_in * fp, 1)
m("LVQin", S_in * math.sin(math.acos(fp)), 1)
m("LVeta", Pn / P_in * 100, 1)
w = nn * 2 * math.pi / 60
m("LVw", w, 1)
m("LVT", Pn / w, 3)
m("LVVfY", Vn / SQ3, 1)                 # tension de bobina en Y
m("LVIfD", In * SQ3, 2)                 # corriente de linea nominal en delta
m("LVVlD", Vn / SQ3, 1)                 # tension de linea nominal en delta = 120 V
m("LVperdidas", P_in - Pn, 1)
# tensiones de la Tabla 20 adaptadas: misma fraccion de la nominal en delta
VnD_guia = 220.0
VnD_lv = Vn / SQ3
tabla20 = [240, 220, 200, 180, 160, 140, 120, 100]
adapt = [v * VnD_lv / VnD_guia for v in tabla20]
for i, (vg, va) in enumerate(zip(tabla20, adapt)):
    m(f"TvGuia{chr(65+i)}", vg, 0)
    m(f"TvLV{chr(65+i)}", va, 1)
    m(f"TvPct{chr(65+i)}", vg / VnD_guia * 100, 1)
# velocidad 80 % y 60 % (estimacion: a par de carga constante s ~ 1/V^2)
for pct, nombre in ((80, "Eighty"), (60, "Sixty")):
    s_est = (s / 100) / (pct / 100) ** 2
    m(f"LVsEst{nombre}", s_est * 100, 2)
    m(f"LVnEst{nombre}", nsinc * (1 - s_est), 0)
# perdidas en el cobre del estator en vacio esperadas con R = 14 ohm
R = 14.0
m("LVR", R, 1)
m("LVRY", 2 * R, 1)
m("LVRD", 2 * R / 3, 2)

# ------------------------------------------------------------ De Lorenzo DL 1021
f50 = 50
n50 = 2870
PDL = 1100
VD, VY, ID, IY = 220, 380, 4.3, 2.5
p_dl = 2   # 2870 r/min a 50 Hz -> 2 polos (ns = 3000)
ns50 = m("DLnsCinc", ns(f50, p_dl), 0)
s50 = m("DLs", (ns50 - n50) / ns50 * 100, 2)
m("DLfr", s50 / 100 * f50, 2)
ns60 = m("DLnsSes", ns(60, p_dl), 0)
n60 = m("DLnSes", ns60 * (1 - s50 / 100), 0)   # mismo deslizamiento aproximado
w50 = n50 * 2 * math.pi / 60
m("DLT", PDL / w50, 2)
m("DLSD", SQ3 * VD * ID, 0)
m("DLSY", SQ3 * VY * IY, 0)
m("DLIfD", ID / SQ3, 2)
m("DLVfY", VY / SQ3, 1)
# limite del 3 %-5 % de desbalance de resistencias
m("DLtolA", 3, 0)
m("DLtolB", 5, 0)
# FP y eficiencia minimos compatibles: P_in >= P_out -> FP*eta = P/S
m("DLfpeta", PDL / (SQ3 * VD * ID), 3)

# ------------------------------------------------------------ DL 1022
m("DLdVD", 230, 0)
m("DLdVY", 400, 0)
m("DLdS", SQ3 * 400 * 2.5, 0)

with open(OUT / "previos.tex", "w") as fh:
    for k, v in macros.items():
        fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

print("LabVolt 8221: ns=%.0f s=%.2f%% fr=%.2f Hz S=%.1f VA Pin=%.1f W eta=%.1f%% T=%.3f N m"
      % (nsinc, s, s/100*f, S_in, P_in, Pn/P_in*100, Pn/w))
print("Tabla 20 adaptada:", ", ".join(f"{v:.1f}" for v in adapt))
print("DL 1021: ns50=%.0f s=%.2f%% fr=%.2f Hz T=%.2f N m S_D=%.0f VA n60~%.0f"
      % (ns50, s50, s50/100*f50, PDL/w50, SQ3*VD*ID, n60))
