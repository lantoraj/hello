"""Builds index.html from the source files in data/: python3 build.py"""
import glob, json, math, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
KR = ["Bratislavský", "Trnavský", "Trenčiansky", "Nitriansky", "Žilinský", "Banskobystrický", "Prešovský", "Košický"]
SR = "Slovenská republika"

# id, name, ambulance specialties (NCZI CISR_ODB_POPIS), hospital programs (MZ SR name, column label)
G=[
 ("gastro","Gastroenterológia a hepatológia",["gastroenterológia","hepatológia","pediatrická gastroenterológia, hepatológia a výživa"],
  [("Program gastroenterológie a hepatológie","Gastro a hepat."),("Program brušnej chirurgie","Brušná chir."),("Onkochirurgický program","Onkochir."),("Program pediatrickej gastroenterológie, hepatológie a porúch výživy","Ped. gastro")]),
 ("kardio","Kardiológia a angiológia",["kardiológia","pediatrická kardiológia","angiológia"],
  [("Neinvazívny kardiovaskulárny program","Neinvaz. kardio"),("Program intervenčnej kardiológie","Interv. kardio"),("Program intervenčnej arytmológie","Arytmológia"),("Kardiochirurgický program","Kardiochir."),("Program cievnej chirurgie","Cievna chir."),("Program pediatrickej kardiológie","Ped. kardio")]),
 ("onko","Onkológia",["klinická onkológia","radiačná onkológia","onkológia v gynekológii","onkológia v chirurgii","onkológia v urológii","pediatrická hematológia a onkológia"],
  [("Program klinickej onkológie","Klin. onko"),("Program radiačnej onkológie","Radiačná onko"),("Onkochirurgický program","Onkochir."),("Program pediatrickej hematológie a onkológie","Ped. hemato-onko")]),
 ("chir","Chirurgia",["chirurgia","úrazová chirurgia","cievna chirurgia","plastická chirurgia","detská chirurgia"],
  [("Program brušnej chirurgie","Brušná chir."),("Traumatologický program","Traumatológia"),("Program cievnej chirurgie","Cievna chir."),("Program chirurgie kože, podkožia a prsníka","Koža a prsník"),("Program plastickej chirurgie","Plastická"),("Program detskej chirurgie","Detská chir.")]),
 ("orto","Ortopédia",["ortopédia","pediatrická ortopédia"],
  [("Ortopedický program","Ortopedický"),("Spondylochirurgický program","Spondylochir."),("Traumatologický program","Traumatológia"),("Ortopedický program pre deti","Ortop. deti")]),
 ("neuro","Neurológia a neurochirurgia",["neurológia","pediatrická neurológia","neurochirurgia"],
  [("Neurologický program","Neurologický"),("Neurochirurgický program","Neurochir."),("Program intervenčnej neurorádiológie","Interv. neurorad."),("Program pediatrickej neurológie","Ped. neuro")]),
 ("uro","Urológia",["urológia","pediatrická urológia"],[("Urologický program","Urologický"),("Urologický program pre deti","Urológia deti")]),
 ("gyn","Gynekológia a pôrodníctvo",["gynekológia a pôrodníctvo","reprodukčná medicína","pediatrická gynekológia"],
  [("Gynekologický program","Gynekologický"),("Pôrodnícky program","Pôrodnícky"),("Gynekologický program pre deti","Gyn. deti")]),
 ("oftal","Oftalmológia",["oftalmológia","pediatrická oftalmológia"],[("Oftalmologický program","Oftalmologický"),("Program detskej oftalmológie","Oftal. deti")]),
 ("orl","Otorinolaryngológia",["otorinolaryngológia","pediatrická otorinolaryngológia","foniatria"],[("Otorinolaryngologický program","ORL"),("Otorinolaryngologický program pre deti","ORL deti")]),
 ("diab","Diabetológia a endokrinológia",["diabetológia, poruchy látkovej premeny a výživy","endokrinológia","pediatrická endokrinológia a diabetológia, poruchy látkovej premeny a výživy"],
  [("Program endokrinológie, diabetológie a metabolických porúch","Endo a diabeto"),("Program pediatrickej endokrinológie, diabetológie a vrodených chýb metabolizmu","Ped. endo")]),
 ("pneumo","Pneumológia",["pneumológia a ftizeológia","pediatrická pneumológia a ftizeológia"],
  [("Program pneumológie a ftizeológie","Pneumológia"),("Program hrudníkovej chirurgie","Hrudníková chir."),("Program pediatrickej pneumológie a ftizeológie","Ped. pneumo")]),
 ("nefro","Nefrológia",["nefrológia","pediatrická nefrológia"],
  [("Nefrologický program","Nefrologický"),("Program pre orgánové transplantácie","Transplantácie"),("Program pediatrickej nefrológie","Ped. nefro")]),
 ("derma","Dermatovenerológia",["dermatovenerológia","detská dermatovenerológia"],[("Dermatovenerologický program","Dermato"),("Dermatovenerologický program pre deti","Dermato deti")]),
 ("psych","Psychiatria",["psychiatria","detská psychiatria","gerontopsychiatria","medicína drogových závislostí"],[("Psychiatrický program","Psychiatrický"),("Program pediatrickej psychiatrie","Ped. psychiatria")]),
 ("reuma","Reumatológia",["reumatológia","pediatrická reumatológia"],[("Reumatologický program","Reumatologický"),("Program pediatrickej reumatológie","Ped. reuma")]),
 ("imuno","Imunológia a alergológia",["klinická imunológia a alergológia","pediatrická imunológia a alergiológia"],
  [("Program klinickej imunológie a alergológie","Imuno a alergo"),("Program pediatrickej imunológie a alergológie","Ped. imuno")]),
 ("hema","Hematológia",["hematológia a transfuziológia"],[("Program hematológie a transfuziológie","Hematológia"),("Program pediatrickej hematológie a onkológie","Ped. hemato-onko")]),
 ("intern","Vnútorné lekárstvo a geriatria",["vnútorné lekárstvo","geriatria"],[("Program internej medicíny","Interná medicína"),("Program paliatívnej medicíny","Paliatívna")]),
]

# ICD-10 chapter used for hospitalizations of each group; ALL = all chapters
CHAPTER = {"gastro": "XI", "kardio": "IX", "onko": "II", "chir": "XIX", "orto": "XIII", "neuro": "VI", "uro": "XIV", "gyn": "XV",
           "oftal": "VII", "orl": "VIII", "diab": "IV", "pneumo": "X", "nefro": "XIV", "derma": "XII", "psych": "V", "reuma": "XIII",
           "imuno": "III", "hema": "III", "intern": "ALL"}
ROMAN = {"I.": 1, "II.": 2, "III.": 3, "IV.": 4, "V.": 5}


def num(v):
    return None if str(v).strip() in ("–", "-", "x", "nan", "") else float(v)


def shapes():
    geo = json.loads((DATA / "kraje_natural_earth.geojson").read_text())
    rename = {"Prešov": "Prešovský", "Trenciansky": "Trenčiansky"}
    lon0, lat0, kx, scale = 16.8, 49.65, math.cos(math.radians(48.7)), 190
    out = {}
    for f in geo["features"]:
        name = rename.get(f["properties"]["name"], f["properties"]["name"])
        g = f["geometry"]
        rings = g["coordinates"] if g["type"] == "Polygon" else [r for poly in g["coordinates"] for r in poly]
        pts = [((lo - lon0) * kx * scale, (lat0 - la) * scale) for lo, la in max(rings, key=len)]
        a = cx = cy = 0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            cr = x1 * y2 - x2 * y1
            a += cr; cx += (x1 + x2) * cr; cy += (y1 + y2) * cr
        out[name] = {"d": "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z",
                     "cx": round(cx / (3 * a), 1), "cy": round(cy / (3 * a), 1)}
    return out


def network():
    d = pd.concat(pd.read_excel(f, sheet_name="Dataset") for f in sorted(glob.glob(str(DATA / "nczi_siet" / "*_T2.xlsx"))))
    d["ROK_SPRAC"] = d["ROK_SPRAC"].astype(int)
    for c in ["UTV_POC", "NAVSTEVY_UTV", "PR_PP_MPP_UV_A01", "PR_PP_MPP_UV_D01", "PR_PP_MPP_UV_E01"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["kraj"] = d["UZEMIE_POPIS"].str.replace(" kraj", "", regex=False)
    d["odb"] = d["CISR_ODB_POPIS"].astype(str).str.strip()
    code = d["DRUH_ZZ"].astype(str).str[:4]
    d["typ"] = code.map(lambda c: "nem" if c.startswith("02") else "pol" if c == "0106" else "amb" if c == "0102" else "ine")
    amb = d[d.UTVAR_VYSTUP == "ambulancia_výstup"]
    jzs = d[d.UTVAR_VYSTUP == "útvar jednodňovej zdravotnej starostlivosti"]
    stats = {}
    for gid, _, specs, _ in G:
        a, j, out = amb[amb.odb.isin(specs)], jzs[jzs.odb.isin(specs)], {}
        for (y, k), s in a.groupby(["ROK_SPRAC", "kraj"]):
            t = s.groupby("typ")["UTV_POC"].sum()
            out.setdefault(k, {})[str(y)] = [
                int(s.UTV_POC.sum()), int(s.NAVSTEVY_UTV.sum()), round(float(s.PR_PP_MPP_UV_A01.sum()), 1),
                round(float(s.PR_PP_MPP_UV_D01.sum() + s.PR_PP_MPP_UV_E01.sum()), 1),
                int(j[(j.ROK_SPRAC == y) & (j.kraj == k)].UTV_POC.sum()),
                int(t.get("nem", 0)), int(t.get("pol", 0)), int(t.get("amb", 0)), int(t.get("ine", 0))]
        stats[gid] = out
    return stats, [str(y) for y in sorted(d.ROK_SPRAC.unique())]


def hospitals():
    xl = DATA / "Zoznam_kategorizovanych_nemocnic_2026_programy.xlsx"
    names = sorted({p for g in G for p, _ in g[3]})
    idx = {p: i for i, p in enumerate(names)}
    levels = {}
    for sheet in ["Povinné programy", "Doplnkové programy"]:
        p = pd.read_excel(xl, sheet_name=sheet, header=1)
        p["nm"] = p["Názov programu"].astype(str).str.strip()
        for _, r in p[p.nm.isin(idx)].iterrows():
            h = levels.setdefault(r["Kód nemocnice"], {})
            i = idx[r.nm]
            h[i] = max(h.get(i, 0), ROMAN.get(str(r["Úroveň programu"]).strip(), 0))
    hl = pd.read_excel(xl, sheet_name="Zoznam nemocníc", header=2).dropna(subset=["Kód PZS"])
    hosp = [{"k": str(r["Kraj"]).strip(), "c": r["Kód PZS"], "l": str(r["Úroveň"]).strip(),
             "n": " ".join(str(r["Názov nemocnice"]).split()), "t": str(r["Typ nemocnice"]).replace(" nemocnica", ""),
             "p": levels.get(r["Kód PZS"], {})} for _, r in hl.iterrows()]
    groups = [{"id": g[0], "name": g[1], "specs": g[2], "ch": CHAPTER[g[0]],
               "progs": [[idx[p], label, p] for p, label in g[3]]} for g in G]
    return hosp, groups


def chapter_key(s):
    s = str(s).strip()
    if s.startswith("Spolu"):
        return "ALL"
    m = re.match(r"^([IVXL]+)\.", s)
    return m.group(1) if m else None


def hospitalizations():
    hs, pop, flows, chn, dg = {}, {}, {}, {}, {}
    files = sorted(glob.glob(str(DATA / "nczi_hospitalizacie" / "*.xlsx")))
    for f in files:
        y = re.search(r"(\d{4})\.xlsx", f).group(1)
        x = pd.ExcelFile(f)
        # sheet names vary between years ("P3 ", "T4_(aktualizovany_grafG3)")
        sheet = lambda n: next(s for s in x.sheet_names if s.strip() == n or (n == "T4" and s.startswith("T4_(")))
        for i, k in enumerate([SR] + KR):
            t = pd.read_excel(x, sheet_name=sheet("T4") if k == SR else sheet(f"T4_{i}"), header=None)
            h4, h5 = [str(v) for v in t.iloc[4]], [str(v) for v in t.iloc[5]]
            col = lambda row, pat: next(j for j, v in enumerate(row) if pat in v)
            cp, ca, cl, cd = col(h5, "na 100 000"), col(h4, "Priemerný vek"), col(h4, "Priemerný ošetrova"), col(h5, "na 1 000 hosp")
            for r in t.itertuples(index=False):
                c = chapter_key(r[0])
                if not c:
                    continue
                if c != "ALL":
                    chn[c] = re.sub(r"\s+", " ", str(r[0])).strip()
                hs.setdefault(c, {}).setdefault(k, {})[y] = [num(r[1]), num(r[cp]), num(r[ca]), num(r[cl]), num(r[cd])]
        for r in pd.read_excel(x, sheet_name=sheet("P3"), header=None).itertuples(index=False):
            n = str(r[10]).strip().replace(" kraj", "")
            if (n in KR or n == SR) and n not in pop.get(y, {}):
                pop.setdefault(y, {})[n] = float(r[11])
        flows[y] = {}
        for r in pd.read_excel(x, sheet_name=sheet("T17"), header=None).itertuples(index=False):
            n = str(r[0]).strip().replace(" kraj", "")
            if n in KR:
                flows[y][n] = [int(float(v)) for v in r[1:12]]
        if f == files[-1]:
            cur = None
            for r in pd.read_excel(x, sheet_name=sheet("T5"), header=None).itertuples(index=False):
                c, s = chapter_key(r[0]), re.sub(r"\s+", " ", str(r[0])).strip()
                if c and c != "ALL":
                    cur = c
                elif cur and "(" in s and num(r[1]) is not None:
                    dg.setdefault(cur, []).append([s, num(r[1]), num(r[4]), num(r[7]), num(r[9])])
    dg = {c: sorted(v, key=lambda g: -g[1])[:10] for c, v in dg.items()}
    return hs, pop, flows, chn, dg


def main():
    stats, years = network()
    hosp, groups = hospitals()
    hs, pop, flows, chn, dg = hospitalizations()
    data = {"groups": groups, "stats": stats, "hosp": hosp, "shapes": shapes(), "years": years,
            "hs": hs, "popY": pop, "flows": flows, "chn": chn, "dg": dg, "hyears": sorted(pop)}
    html = (ROOT / "template.html").read_text().replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    (ROOT / "index.html").write_text(html)
    print(f"index.html: {len(html) // 1024} kB, years {years[0]}–{years[-1]} / {sorted(pop)[0]}–{sorted(pop)[-1]}, {len(hosp)} hospitals")


if __name__ == "__main__":
    main()
