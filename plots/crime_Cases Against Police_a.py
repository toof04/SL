import pandas as pd
import numpy as np
import re

df = pd.read_csv("State_UT-wise Cases Registered against State Police Personnel during 2021.csv")
cols = df.columns.drop(["Sl. No.", "State/UT"])
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

s1 = df[df["State/UT"].str.contains("Total State \(S\)", case=False, na=False)]
s2 = df[df["State/UT"].str.contains("Total UT \(S\)", case=False, na=False)]
s3 = df[df["State/UT"].str.contains("Total All India", case=False, na=False)]

all_tot = {c:s3[c].sum() for c in cols}
st_tot = {c:s1[c].sum() for c in cols}
ut_tot = {c:s2[c].sum() for c in cols}

clean = df[~df["State/UT"].str.contains("Total", case=False, na=False)]

tops = {}
for c in cols:
    t = clean[["State/UT", c]].sort_values(c, ascending=False).head(10)
    tops[c] = t.reset_index(drop=True)

def rate_block(states, n, d, name):
    pct = (n/d).replace([np.inf,-np.inf],0).fillna(0)
    absx = n.astype(int).astype(str) + " / " + d.astype(int).astype(str)
    pcx = (pct*100).round(2).astype(str)+"%"
    x = pd.DataFrame({"State/UT":states, "Absolute":absx, "Percent":pcx})
    x = x.sort_values("Percent", ascending=False).reset_index(drop=True)
    print(f"\n======== {name} ========\n")
    print(x.to_string(index=False))
    return pct

c1 = rate_block(clean["State/UT"], clean["Number of Cases - Charge-Sheeted"], clean["Number of Cases - Registered"], "CASE CHARGE-SHEET")
c2 = rate_block(clean["State/UT"], clean["Number of Cases - Final Report Submitted"], clean["Number of Cases - Registered"], "CASE FINAL REPORT")
c3 = rate_block(clean["State/UT"], clean["Number of Cases - Quashed / Stayed by Courts"], clean["Number of Cases - Registered"], "CASE QUASHED")
p1 = rate_block(clean["State/UT"], clean["Number of Police Personnel - Charge-Sheeted"], clean["Number of Police Personnel - Arrested"], "PERSONNEL CS")
p2 = rate_block(clean["State/UT"], clean["Number of Police Personnel - Convicted"], clean["Number of Police Personnel - Arrested"], "PERSONNEL CONVICTION")
p3 = rate_block(clean["State/UT"], clean["Number of Police Personnel - Acquitted or Discharged"], clean["Number of Police Personnel - Arrested"], "PERSONNEL ACQUITTAL")
p4 = rate_block(clean["State/UT"], clean["Number of Police Personnel - Trials were Completed"], clean["Number of Police Personnel - Charge-Sheeted"], "TRIAL COMPLETION")

rank = pd.DataFrame({"State/UT":clean["State/UT"], "Trial Completion %":(p4*100).round(2)})
t5 = rank.sort_values("Trial Completion %", ascending=False).head(5)
w5 = rank.sort_values("Trial Completion %", ascending=True).head(5)

print("\n===== TOP 5 (TRIAL COMPLETION) =====\n")
print(t5.to_string(index=False))
print("\n===== WORST 5 (TRIAL COMPLETION) =====\n")
print(w5.to_string(index=False))

print("\n===== TOP 10 PER INDICATOR =====\n")
for c,t in tops.items():
    print("\n--",c)
    print("All India:",all_tot[c])
    print("States   :",st_tot[c])
    print("UT       :",ut_tot[c])
    print(t.to_string(index=False))

def n_sheet(x):
    x = re.sub(r'[\/\\\?\*\[\]\:]', '_', x).strip()
    return x[:28]+"..." if len(x)>31 else x

path = "police_personnel_analysis.xlsx"
with pd.ExcelWriter(path, engine="openpyxl") as w:
    for c,t in tops.items():
        nm = n_sheet("Top10_"+c)
        t.to_excel(w, sheet_name=nm, index=False)

    sum_df = pd.DataFrame({"Indicator":list(all_tot.keys()),"All India":list(all_tot.values()),"States":list(st_tot.values()),"UT":list(ut_tot.values())})
    sum_df.to_excel(w, sheet_name="Totals", index=False)

    def pack(s,n,d,p):
        return pd.DataFrame({"State/UT":s,"Num":n,"Den":d,"Percent":(p*100).round(2)})

    pack(clean["State/UT"], clean["Number of Cases - Charge-Sheeted"], clean["Number of Cases - Registered"], c1).to_excel(w, n_sheet("Case_CS"), index=False)
    pack(clean["State/UT"], clean["Number of Cases - Final Report Submitted"], clean["Number of Cases - Registered"], c2).to_excel(w, n_sheet("Case_FR"), index=False)
    pack(clean["State/UT"], clean["Number of Cases - Quashed / Stayed by Courts"], clean["Number of Cases - Registered"], c3).to_excel(w, n_sheet("Case_Quashed"), index=False)
    pack(clean["State/UT"], clean["Number of Police Personnel - Charge-Sheeted"], clean["Number of Police Personnel - Arrested"], p1).to_excel(w, n_sheet("Pers_CS"), index=False)
    pack(clean["State/UT"], clean["Number of Police Personnel - Convicted"], clean["Number of Police Personnel - Arrested"], p2).to_excel(w, n_sheet("Pers_Conv"), index=False)
    pack(clean["State/UT"], clean["Number of Police Personnel - Acquitted or Discharged"], clean["Number of Police Personnel - Arrested"], p3).to_excel(w, n_sheet("Pers_Acq"), index=False)
    pack(clean["State/UT"], clean["Number of Police Personnel - Trials were Completed"], clean["Number of Police Personnel - Charge-Sheeted"], p4).to_excel(w, n_sheet("Trial_Comp"), index=False)

    t5.to_excel(w, n_sheet("Trial_Top5"), index=False)
    w5.to_excel(w, n_sheet("Trial_Worst5"), index=False)

print(path)
