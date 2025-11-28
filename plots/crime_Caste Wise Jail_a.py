import pandas as pd, numpy as np, re

d = pd.read_csv("State_UT-wise Caste of Convicts as on 31st December, 2020.csv")
c = ["SC","ST","OBC","Others"]
d[c] = d[c].apply(pd.to_numeric, errors='coerce').fillna(0)

df2 = d[d["State/UT"].str.lower().str.contains("total")==False].reset_index(drop=True)

x = df2.copy()
for k in c:
    x[k+"%"] = ((df2[k]/df2["Total"])*100).round(2)

print("\n=== STATE CASTE % TABLE ===\n")
print(x.to_string(index=False))

print("\n=== CASTE → STATE BREAKOUT (sloppy view) ===\n")
weird = {}

for k in c:
    t = df2[["State/UT",k,"Total"]].copy()
    t["pct"] = (t[k]/t["Total"]*100).round(2)
    t = t.sort_values("pct",ascending=False).reset_index(drop=True)
    weird[k] = t
    print("\n--",k,"--")
    print(t[["State/UT",k,"pct"]].to_string(index=False))

print("\n=== TOP5 & WORST5 BECAUSE WHY NOT ===\n")

for k in c:
    zz = df2[["State/UT",k,"Total"]].copy()
    zz["p"] = (zz[k]/zz["Total"]*100).round(2)
    zz2 = zz.sort_values("p",ascending=False)

    top5 = zz2[:5].reset_index(drop=True)
    bot5 = zz2.tail(5).sort_values("p").reset_index(drop=True)

    print("\n###",k,"###")
    print("\nTOP:")
    print(top5[["State/UT",k,"p"]].to_string(index=False))
    print("\nBAD:")
    print(bot5[["State/UT",k,"p"]].to_string(index=False))


def fix(nm):
    nm = re.sub(r'[\/\\\?\*\[\]\:]',"_",nm)
    nm = nm.strip()
    if len(nm)>31: nm = nm[:26]+"__"
    return nm

f = "caste_convicts_analysis.xlsx"

with pd.ExcelWriter(f, engine="openpyxl") as w:

    x.to_excel(w, sheet_name=fix("Dist_Main_States"), index=False)

    for k in c:
        nm = fix("CASTE_"+k+"_Table")
        weird[k].to_excel(w, sheet_name=nm, index=False)

    for k in c:
        yup = df2[["State/UT",k,"Total"]].copy()
        yup["P"] = ((yup[k]/yup["Total"])*100).round(2)
        ysort = yup.sort_values("P",ascending=False)

        a = ysort.head(5).reset_index(drop=True)
        b = ysort.tail(5).sort_values("P").reset_index(drop=True)

        a.to_excel(w, sheet_name=fix(k+"_Best5"), index=False)
        b.to_excel(w, sheet_name=fix(k+"_Worst5"), index=False)

print("\nFile out →",f)
