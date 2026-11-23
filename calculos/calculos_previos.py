#!/usr/bin/env python3
"""Calculos previos del preinforme del Laboratorio 4 (maquinas de induccion).

Reproduce los valores de la seccion VII del informe y escribe
calculos/salidas/previos.tex con macros LaTeX (coma decimal via \\num).

Datos de entrada:
  * DL 1021 (jaula de ardilla, banco fisico): placa real del equipo
      1,1 kW; 230/400 V D/Y; 4,8/2,8 A, cos 0,72, 2870 r/min a 50 Hz;
      4,2/2,4 A, cos 0,84, 3450 r/min a 60 Hz.
  * DL 1022 (rotor devanado, banco fisico): placa real del equipo
      1,1 kW; 230/400 V D/Y; 5/2,9 A, cos 0,73 a 50 Hz; 4,5/2,6 A, cos 0,82 a 60 Hz;
      3450 r/min a 60 Hz; rotor 390 V, 2 A.
  * LabVolt 8221-02 (jaula de ardilla de LVSIM): placa del modulo
      208 V 3F 60 Hz; motor 200 W, FP 0,73, 1685 r/min, 1,14 A; bobinas 120 V.
La guia y la simulacion LVSIM estan referidas a 220 V (VnD_guia).
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
# Placa real del equipo del laboratorio (foto): 230/400 V D/Y, 1,1 kW, IEC 34-1,
#   50 Hz: 4,8/2,8 A, cos 0,72, 2870 r/min;  60 Hz: 4,2/2,4 A, cos 0,84, 3450 r/min
f50, f60 = 50, 60
n50, n60 = 2870, 3450
PDL = 1100
VD, VY = 230, 400
ID50, IY50, fp50 = 4.8, 2.8, 0.72
ID, IY, fp60 = 4.2, 2.4, 0.84            # 60 Hz: datos de operacion en el laboratorio
p_dl = 2                                 # ns = 3000 a 50 Hz -> 2 polos
ns50 = m("DLnsCinc", ns(f50, p_dl), 0)
ns60 = m("DLnsSes", ns(f60, p_dl), 0)
s50 = m("DLs", (ns50 - n50) / ns50 * 100, 2)
s60 = m("DLsSes", (ns60 - n60) / ns60 * 100, 2)
m("DLfr", s50 / 100 * f50, 2)
m("DLfrSes", s60 / 100 * f60, 2)
m("DLnSes", n60, 0)
w50 = n50 * 2 * math.pi / 60
w60 = n60 * 2 * math.pi / 60
m("DLT", PDL / w50, 2)
m("DLTsesenta", PDL / w60, 2)
m("DLSD", SQ3 * VD * ID, 0)
m("DLSY", SQ3 * VY * IY, 0)
m("DLSDcinc", SQ3 * VD * ID50, 0)
m("DLSYcinc", SQ3 * VY * IY50, 0)
m("DLIfD", ID / SQ3, 2)
m("DLVfY", VY / SQ3, 1)
m("DLtolA", 3, 0)
m("DLtolB", 5, 0)
# potencia de entrada y eficiencia a plena carga con el cos(fi) de placa
for tag, S_, fp_ in (("Ses", SQ3 * VD * ID, fp60), ("Cinc", SQ3 * VD * ID50, fp50)):
    m(f"DLPin{tag}", S_ * fp_, 0)
    m(f"DLeta{tag}", PDL / (S_ * fp_) * 100, 1)
    m(f"DLQin{tag}", S_ * math.sin(math.acos(fp_)), 0)
m("DLfpeta", PDL / (SQ3 * VD * ID), 3)
# estimacion de la resistencia por fase: P_Cu1 entre 3 % y 6 % de S (60 Hz)
IfD = ID / SQ3
for pct, nombre in ((3, "Lo"), (6, "Hi")):
    pcu = pct / 100 * SQ3 * VD * ID
    r = pcu / (3 * IfD ** 2)
    m(f"DLPcu{nombre}", pcu, 0)
    m(f"DLR{nombre}", r, 2)
    m(f"DLRD{nombre}", 2 * r / 3, 2)
    m(f"DLRY{nombre}", 2 * r, 2)
    m(f"DLVprueba{nombre}", r * 1.0, 2)      # caida con 1 A de prueba
# operacion en vacio a 60 Hz
n0 = 3590.0                                   # vacio estimado (s0 ~ 0,3 %)
m("DLnVac", n0, 0)
m("DLsVac", (ns60 - n0) / ns60 * 100, 2)
m("DLRVest", (n0 - n60) / n60 * 100, 1)
m("DLflujo", 50 / 60 * 100, 1)
# freno: par por kilogramo de pesa, tau = m g X
g = 9.81
for k, x in enumerate([2, 4, 6, 8, 10, 12, 14, 16, 18, 20]):
    m(f"FrX{chr(65+k)}", x, 0)
    m(f"FrT{chr(65+k)}", g * x / 100, 3)
m("FrMasaNom", PDL / w60 / (g * 0.20), 2)    # masa que daria tau nominal con X = 20 cm
# factores de la tabla 20 respecto a 220 V
for i, vg in enumerate(tabla20):
    m(f"TvVV{chr(65+i)}", vg / VD, 3)
    m(f"TvVVsq{chr(65+i)}", (vg / VD) ** 2, 3)
    m(f"TvVF{chr(65+i)}", vg, 0)

# ------------------------------------------------------------ DL 1022 (placa real)
#   230/400 V D/Y, 1,1 kW; 50 Hz: 5/2,9 A, cos 0,73, 2870; 60 Hz: 4,5/2,6 A, cos 0,82, 3450
#   rotor: 390 V; 1,75 A (50 Hz) y 2 A (60 Hz)
m("DLdSD", SQ3 * 230 * 4.5, 0)
m("DLdSY", SQ3 * 400 * 2.6, 0)
m("DLdPin", SQ3 * 230 * 4.5 * 0.82, 0)
m("DLdeta", 1100 / (SQ3 * 230 * 4.5 * 0.82) * 100, 1)
m("DLdSrot", SQ3 * 390 * 2.0, 0)

with open(OUT / "previos.tex", "w") as fh:
    for k, v in macros.items():
        fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

print("LabVolt 8221: ns=%.0f s=%.2f%% fr=%.2f Hz S=%.1f VA Pin=%.1f W eta=%.1f%% T=%.3f N m"
      % (nsinc, s, s/100*f, S_in, P_in, Pn/P_in*100, Pn/w))
print("Tabla 20 adaptada:", ", ".join(f"{v:.1f}" for v in adapt))
print("DL 1021: ns60=%.0f s60=%.2f%% T60=%.2f N m S_D=%.0f VA eta60=%.1f%%"
      % (ns60, s60, PDL/w60, SQ3*VD*ID, PDL/(SQ3*VD*ID*fp60)*100))
