#!/usr/bin/env python3
"""Procesa las corridas reales de LVSIM-EMS del Laboratorio 4 (preinforme).

Lee los JSON crudos de calculos/lvsim/ (lecturas promediadas de la ventana de
medicion de LVSIM) y genera:
  - tablas LaTeX en calculos/salidas/*.tex
  - archivos de datos para pgfplots en calculos/salidas/*.dat
  - un resumen en consola.

Asignacion de los medidores de LVSIM (montajes de las actividades 1.2 y 2):
  M1 = E1 = V_AC (W1),  M2 = E2 = V_BC (W2),  M3 = E3 = V_AB
  M7..M9 = I1..I3 (corrientes de linea)
  M13 = PQS1(E1,I1) = P_W1,  M14 = PQS2(E2,I2) = P_W2  (metodo de dos vatimetros)
  M6 = par T [N m],  M12 = velocidad n [r/min],  M18 = Pm(T,n) [W]
"""
import json
import math
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
RAW = BASE / "lvsim"
OUT = BASE / "salidas"
OUT.mkdir(exist_ok=True)

R_FASE = 14.0          # ohm, resistencia por fase medida en LVSIM (act. 1.1)
NS = 1800.0            # r/min, motor 8221 de 4 polos a 60 Hz
SQ3 = math.sqrt(3)


def c(x, nd=2):
    """Numero con coma decimal para LaTeX (siunitx usa \\num)."""
    return f"\\num{{{x:.{nd}f}}}"


def load(name):
    return json.load(open(RAW / name))


def g(row, k):
    return row[str(k)]


def promedio_lineas(row):
    vl = (g(row, 1) + g(row, 2) + g(row, 3)) / 3
    il = (g(row, 7) + g(row, 8) + g(row, 9)) / 3
    return vl, il


# ---------------------------------------------------------------- 1.1 resistencia
ohm = load("resistencia_ohm_raw.json")
cc = load("resistencia_cc_raw.json")
V = np.array([r["1"] for r in cc])
Icc = np.array([r["7"] for r in cc])
pend, inter = np.polyfit(Icc, V, 1)
r_vi = V / Icc
fases = [ohm["fase_1_4_ohm"], ohm["fase_2_5_ohm"], ohm["fase_3_6_ohm"]]
desv = (max(fases) - min(fases)) / np.mean(fases) * 100

with open(OUT / "tab_resistencia_cc.tex", "w") as f:
    for v, i, r in zip(V, Icc, r_vi):
        f.write(f"{c(v,2)} & {c(i,3)} & {c(r,2)} \\\\\n")
with open(OUT / "res_valores.tex", "w") as f:
    f.write(f"\\newcommand{{\\Rvi}}{{{c(pend,2)}}}\n")
    f.write(f"\\newcommand{{\\Rvimin}}{{{c(r_vi.min(),2)}}}\n")
    f.write(f"\\newcommand{{\\Rvimax}}{{{c(r_vi.max(),2)}}}\n")
    f.write(f"\\newcommand{{\\Rinter}}{{{c(inter,3)}}}\n")
    f.write(f"\\newcommand{{\\Rdesv}}{{{c(desv,2)}}}\n")
with open(OUT / "vi_cc.dat", "w") as f:
    f.write("I V\n")
    for v, i in zip(V, Icc):
        f.write(f"{i:.4f} {v:.4f}\n")

# ------------------------------------------------------- 1.2 puesta en operacion
filas = []
for fn, con, sec in [("op_Y_ABC.json", "Y", "ABC"), ("op_D_ABC.json", "$\\Delta$", "ABC")]:
    for r in load(fn):
        filas.append((con, sec, r["pct"], r))
for fn, con, sec in [("op_Y_BAC.json", "Y", "BAC"), ("op_Y_BCA.json", "Y", "BCA"),
                     ("op_D_BAC.json", "$\\Delta$", "BAC")]:
    filas.append((con, sec, 100, load(fn)))

with open(OUT / "tab_operacion.tex", "w") as f:
    for con, sec, pct, r in filas:
        vl, il = promedio_lineas(r)
        p = g(r, 13) + g(r, 14)
        n = g(r, 12)
        s = (NS - abs(n)) / NS * 100
        sentido = "directo" if n > 0 else "inverso"
        f.write(f"{con} & {sec} & {pct} & {c(vl,1)} & {c(il,3)} & {c(p,1)} & "
                f"{c(n,0)} & {c(s,2)} & {sentido} \\\\\n")

d208 = load("op_D_208.json")
vl, il = promedio_lineas(d208)
with open(OUT / "res_valores.tex", "a") as f:
    f.write(f"\\newcommand{{\\DdosVL}}{{{c(vl,1)}}}\n")
    f.write(f"\\newcommand{{\\DdosIL}}{{{c(il,2)}}}\n")
    f.write(f"\\newcommand{{\\DdosIF}}{{{c(il/SQ3,2)}}}\n")
    f.write(f"\\newcommand{{\\DdosP}}{{{c(g(d208,13)+g(d208,14),0)}}}\n")

# ------------------------------------------------------------------ 2.1 vacio
vac = load("vacio_raw.json")
rows_v = []
for r in vac:
    vl, il = promedio_lineas(r)
    w1, w2 = g(r, 13), g(r, 14)
    p0 = w1 + w2
    ifase = il / SQ3                      # conexion delta
    pcu = 3 * R_FASE * ifase ** 2
    prot = p0 - pcu
    fp = p0 / (SQ3 * vl * il)
    rows_v.append(dict(V=vl, I=il, W1=w1, W2=w2, P0=p0, Pcu=pcu, Prot=prot, fp=fp, n=g(r, 12)))

with open(OUT / "tab_vacio.tex", "w") as f:
    for x in rows_v:
        f.write(f"{c(x['V'],1)} & {c(x['I'],3)} & {c(x['W1'],1)} & {c(x['W2'],1)} & "
                f"{c(x['P0'],1)} & {c(x['Pcu'],1)} & {c(x['Prot'],1)} & {c(x['fp'],3)} & "
                f"{c(x['n'],0)} \\\\\n")
with open(OUT / "vacio.dat", "w") as f:
    f.write("V I P0 Pcu Prot fp V2 n\n")
    for x in rows_v:
        f.write(f"{x['V']:.3f} {x['I']:.4f} {x['P0']:.3f} {x['Pcu']:.3f} {x['Prot']:.3f} "
                f"{x['fp']:.4f} {x['V']**2:.1f} {x['n']:.1f}\n")

# separacion de perdidas: P_rot = P_m + k V^2 en la zona de V >= 87 V
# (a tension baja el deslizamiento crece y la recta deja de valer)
sel = [x for x in rows_v if x["V"] >= 85]
xv = np.array([x["V"] ** 2 for x in sel])
yv = np.array([x["Prot"] for x in sel])
k, pm = np.polyfit(xv, yv, 1)
nom = min(rows_v, key=lambda x: abs(x["V"] - 120))
pfe_nom = nom["Prot"] - pm
with open(OUT / "res_valores.tex", "a") as f:
    f.write(f"\\newcommand{{\\Pmec}}{{{c(pm,1)}}}\n")
    f.write(f"\\newcommand{{\\kfe}}{{{c(k*1e3,3)}}}\n")
    f.write(f"\\newcommand{{\\VnomVac}}{{{c(nom['V'],1)}}}\n")
    f.write(f"\\newcommand{{\\InomVac}}{{{c(nom['I'],3)}}}\n")
    f.write(f"\\newcommand{{\\PceroNom}}{{{c(nom['P0'],1)}}}\n")
    f.write(f"\\newcommand{{\\PcuNom}}{{{c(nom['Pcu'],1)}}}\n")
    f.write(f"\\newcommand{{\\ProtNom}}{{{c(nom['Prot'],1)}}}\n")
    f.write(f"\\newcommand{{\\PfeNom}}{{{c(pfe_nom,1)}}}\n")
    f.write(f"\\newcommand{{\\FPnomVac}}{{{c(nom['fp'],3)}}}\n")
    # rama de magnetizacion aproximada (por fase, delta)
    zf = nom["V"] / (nom["I"] / SQ3)
    rfe = nom["V"] ** 2 / (pfe_nom / 3)
    f.write(f"\\newcommand{{\\Zvac}}{{{c(zf,1)}}}\n")
    f.write(f"\\newcommand{{\\Rfe}}{{{c(rfe,0)}}}\n")
with open(OUT / "vacio_ajuste.dat", "w") as f:
    f.write("V2 Prot\n")
    for v2 in [0, 4000, 8000, 12000, 16000, 18000]:
        f.write(f"{v2} {pm + k*v2:.3f}\n")

# ------------------------------------------------------------------ 2.2 carga
car = load("carga_raw.json")
rows_c = []
for r in car:
    vl, il = promedio_lineas(r)
    pin = g(r, 13) + g(r, 14)
    tau = g(r, 6)
    n = g(r, 12)
    pout = tau * n * 2 * math.pi / 60
    eta = pout / pin * 100
    s = (NS - n) / NS * 100
    fp = pin / (SQ3 * vl * il)
    rows_c.append(dict(V=vl, I=il, knob=r["knob"], tau=tau, n=n, Pin=pin, Pout=pout,
                       Pm=g(r, 18), eta=eta, s=s, fp=fp))

with open(OUT / "tab_carga.tex", "w") as f:
    for x in rows_c:
        f.write(f"{c(x['I'],3)} & {x['knob']} & {c(x['tau'],3)} & {c(x['n'],0)} & "
                f"{c(x['Pin'],1)} & {c(x['Pout'],1)} & {c(x['eta'],1)} & {c(x['s'],2)} & "
                f"{c(x['fp'],3)} \\\\\n")
with open(OUT / "carga.dat", "w") as f:
    f.write("I knob tau n Pin Pout eta s fp\n")
    for x in rows_c:
        f.write(f"{x['I']:.4f} {x['knob']} {x['tau']:.4f} {x['n']:.1f} {x['Pin']:.3f} "
                f"{x['Pout']:.3f} {x['eta']:.3f} {x['s']:.4f} {x['fp']:.4f}\n")

# punto mas cercano a la corriente nominal en delta (1,14*sqrt3 = 1,97 A)
inom = 1.14 * SQ3
pn = min(rows_c, key=lambda x: abs(x["I"] - inom))
pmax = max(rows_c, key=lambda x: x["eta"])
with open(OUT / "res_valores.tex", "a") as f:
    f.write(f"\\newcommand{{\\CnomI}}{{{c(pn['I'],3)}}}\n")
    f.write(f"\\newcommand{{\\CnomT}}{{{c(pn['tau'],3)}}}\n")
    f.write(f"\\newcommand{{\\Cnomn}}{{{c(pn['n'],0)}}}\n")
    f.write(f"\\newcommand{{\\CnomPin}}{{{c(pn['Pin'],1)}}}\n")
    f.write(f"\\newcommand{{\\CnomPout}}{{{c(pn['Pout'],1)}}}\n")
    f.write(f"\\newcommand{{\\Cnometa}}{{{c(pn['eta'],1)}}}\n")
    f.write(f"\\newcommand{{\\Cnoms}}{{{c(pn['s'],2)}}}\n")
    f.write(f"\\newcommand{{\\Cnomfp}}{{{c(pn['fp'],3)}}}\n")
    f.write(f"\\newcommand{{\\Cetamax}}{{{c(pmax['eta'],1)}}}\n")
    last = rows_c[-1]
    f.write(f"\\newcommand{{\\Cultn}}{{{c(last['n'],0)}}}\n")
    f.write(f"\\newcommand{{\\CultPout}}{{{c(last['Pout'],1)}}}\n")
    f.write(f"\\newcommand{{\\CultI}}{{{c(last['I'],3)}}}\n")
    f.write(f"\\newcommand{{\\Cults}}{{{c(last['s'],2)}}}\n")
    f.write(f"\\newcommand{{\\Culteta}}{{{c(last['eta'],1)}}}\n")
    nvac = rows_c[0]["n"]
    f.write(f"\\newcommand{{\\Cnvac}}{{{c(nvac,0)}}}\n")
    f.write(f"\\newcommand{{\\CRV}}{{{c((nvac-pn['n'])/pn['n']*100,2)}}}\n")
    # verificacion Pm(LVSIM) vs tau*omega
    err = max(abs(x["Pm"] - x["Pout"]) for x in rows_c)
    f.write(f"\\newcommand{{\\CerrPm}}{{{c(err,2)}}}\n")
    # balance en el punto nominal: Pin - Pout - Pcu1 - Prot(vacio) = P_rotor + adicionales
    pcu1 = 3 * R_FASE * (pn["I"] / SQ3) ** 2
    pag = pn["Pin"] - pcu1 - pfe_nom
    pcu2 = pn["s"] / 100 * pag
    f.write(f"\\newcommand{{\\CnomPcuu}}{{{c(pcu1,1)}}}\n")
    f.write(f"\\newcommand{{\\CnomPag}}{{{c(pag,1)}}}\n")
    f.write(f"\\newcommand{{\\CnomPcud}}{{{c(pcu2,1)}}}\n")
    resto = pn["Pin"] - pn["Pout"] - pcu1 - pfe_nom - pcu2 - pm
    f.write(f"\\newcommand{{\\CnomResto}}{{{c(resto,1)}}}\n")

print(f"R (V-I) = {pend:.3f} ohm, intercepto {inter:.4f} V, desviacion fases {desv:.2f} %")
print(f"Vacio @ {nom['V']:.1f} V: P0={nom['P0']:.1f} W, Pcu={nom['Pcu']:.1f} W, "
      f"Prot={nom['Prot']:.1f} W -> Pm={pm:.1f} W, Pfe={pfe_nom:.1f} W")
print(f"Carga nominal: I={pn['I']:.3f} A, tau={pn['tau']:.3f} N m, n={pn['n']:.0f}, "
      f"Pin={pn['Pin']:.1f}, Pout={pn['Pout']:.1f}, eta={pn['eta']:.1f} %, s={pn['s']:.2f} %")
print(f"Balance nominal: Pcu1={pcu1:.1f}, Pag={pag:.1f}, Pcu2={pcu2:.1f}, resto={resto:.1f} W")
