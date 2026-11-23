#!/usr/bin/env python3
"""Calculos del informe: velocidad contra tension (tabla de la clase) y velocidad sincronica.

Datos medidos (tabla manuscrita, conexion delta, 220 V): V_L [V] -> N [rpm].
Tablero: conexion en estrella, 380 V -> 3580 rpm; barrido 380 -> 300 V.
Escribe calculos/salidas/clase.dat, clase_tabla.tex y clase.tex (macros).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "salidas"
OUT.mkdir(exist_ok=True)
V = [220, 215, 210, 205, 200, 195, 190, 185, 180, 175, 170]
N = [3591.7, 3600.8, 3596.8, 3596.0, 3593.9, 3606.3, 3590.6, 3596.5, 3606.3, 3591.2, 3593.1]
F, P = 60, 2
NS = 120 * F / P
mac = {}


def m(k, v, nd=2):
    mac[k] = f"\\num{{{v:.{nd}f}}}"
    return v


n = len(V)
vm, nm = sum(V) / n, sum(N) / n
sxx = sum((v - vm) ** 2 for v in V)
sxy = sum((v - vm) * (x - nm) for v, x in zip(V, N))
syy = sum((x - nm) ** 2 for x in N)
b = sxy / sxx
a = nm - b * vm
res = sum((x - (a + b * v)) ** 2 for v, x in zip(V, N))
se = math.sqrt(res / (n - 2) / sxx)
r = sxy / math.sqrt(sxx * syy)
sd = math.sqrt(syy / (n - 1))
m("Cn", n, 0)
m("ClMean", nm, 1)
m("ClSd", sd, 1)
m("ClMin", min(N), 1)
m("ClMax", max(N), 1)
m("ClRange", max(N) - min(N), 1)
m("ClRangePct", (max(N) - min(N)) / NS * 100, 2)
m("ClSlope", b, 3)
m("ClSlopeSE", se, 3)
m("ClSlopeAbsMax", abs(b) * (V[0] - V[-1]), 1)    # cambio total que implicaria la recta de 220 a 170 V
m("ClR", r, 2)
m("ClNs", NS, 0)
m("ClMeanSlip", (NS - nm) / NS * 100, 2)
sl = [(NS - x) / NS * 100 for x in N]
m("ClSlipMin", min(sl), 2)
m("ClSlipMax", max(sl), 2)
m("ClNabove", sum(1 for x in N if x > NS), 0)
m("ClVred", (V[0] - V[-1]) / V[0] * 100, 1)       # reduccion de tension 220 -> 170 V
m("ClVredPizarra", (380 - 300) / 380 * 100, 1)
m("ClSlipY", (NS - 3580) / NS * 100, 2)
m("ClFrY", (NS - 3580) / NS * F, 2)
m("ClDN", N[-1] - N[0], 1)
# estimacion: s ~ 1/V^2 con el deslizamiento medio como referencia a 220 V
s0 = (NS - nm) / NS
m("ClEstFactor", (V[0] / V[-1]) ** 2, 2)
m("ClEstDN", NS * s0 * ((V[0] / V[-1]) ** 2 - 1), 1)
with open(OUT / "clase.dat", "w") as fh:
    fh.write("V N s fr Vpct\n")
    for v, x in zip(V, N):
        fh.write(f"{v} {x:.1f} {(NS-x)/NS*100:.3f} {(NS-x)/NS*F:.3f} {v/220*100:.1f}\n")
with open(OUT / "clase_tabla.tex", "w") as fh:
    for v, x in zip(V, N):
        s = (NS - x) / NS * 100
        fh.write(f"\\num{{{v}}} & \\num{{{v/220*100:.1f}}} & \\num{{{x:.1f}}} & \\num{{{s:.2f}}} & \\num{{{s*F/100:.2f}}} \\\\\n")
with open(OUT / "clase.tex", "w") as fh:
    for k, v in mac.items():
        fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
print(f"mean={nm:.2f} sd={sd:.2f} slope={b:.3f}+-{se:.3f} rpm/V r={r:.2f} slip_mean={(NS-nm)/NS*100:.3f}%")
print("slip range", min(sl), max(sl), "above ns:", sum(1 for x in N if x > NS))
print("est dN for 1/V^2:", NS * s0 * ((V[0]/V[-1])**2 - 1))
