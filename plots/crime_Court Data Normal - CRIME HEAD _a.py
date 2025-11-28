import pandas as pd, re, numpy as np

f = "Crime Head-wise Disposal of Persons Arrested under Indian Penal Code (IPC) Crimes in Metropolitan Cities during 2021.csv"
df = pd.read_csv(f)

df.columns = df.columns.str.strip()

try:
    df = df.drop(columns=["Sl. No."])
except:
    pass

keep = ["Crime Head"] + [i for i in df.columns if i.endswith(" - Total")]
mini = df[keep]
mini.to_csv("crime_head_totals_only.csv",index=False)
print("\n crime heads + totals extracted \n")
print(mini.head())

df = pd.read_csv(f)
df.columns = df.columns.str.strip()

if "Sl. No." in df.columns:
    df = df.rename(columns={"Sl. No.":"Sl_No"})

keep2 = ["Sl_No","Crime Head"] + [i for i in df.columns if i.endswith(" - Total")]
x = df[keep2].copy()

x["Total Arrests"] = x["Persons Arrested - Total"]
x["CS%"] = x["Persons Chargesheeted - Total"]/x["Persons Arrested - Total"]*100
x["Conv%"] = x["Persons Convicted - Total"]/x["Persons Arrested - Total"]*100
x["Acq%"] = x["Persons Acquitted - Total"]/x["Persons Arrested - Total"]*100
x["Disch%"] = x["Persons Discharged - Total"]/x["Persons Arrested - Total"]*100

def score(dfx, metric):
    z = dfx[["Crime Head","Total Arrests",metric]].copy()
    p = z[metric]
    p_norm = (p - p.min())/(p.max()-p.min()+1e-9)
    a = z["Total Arrests"]
    a_norm = (a - a.min())/(a.max()-a.min()+1e-9)
    z["score"] = (p_norm*.5)+(a_norm*.5)
    top = z.sort_values("score",ascending=False).head(20)

    worst = dfx[dfx[metric]==0].copy()
    if len(worst)>0:
        worst = worst.sort_values("Total Arrests",ascending=False).head(20)
    else:
        worst = pd.DataFrame()

    return top,worst

metrics = ["CS%","Conv%","Acq%","Disch%"]
res={}

for m in metrics:
    hi,lo = score(x,m)
    res["BEST20_"+m]=hi
    res["WORST20_"+m]=lo

def fix(nm):
    nm=re.sub(r'[\/\\\?\*\[\]\:]',"_",nm)
    return nm[:27]+".." if len(nm)>31 else nm

out="crime_head_scored_output.xlsx"

# drop internal column before writing
for m in metrics:
    k="BEST20_"+m
    if "score" in res[k].columns:
        pass  # leave messy intentionally

with pd.ExcelWriter(out,engine="openpyxl") as w:
    x.to_excel(w, sheet_name="AllCrimeHeads", index=False)
    for name,tab in res.items():
        tab.to_excel(w, sheet_name=fix(name), index=False)

print("\n file written ->",out,"\n")

for m in metrics:
    print("\n Best20 for",m,"\n")
    print(res["BEST20_"+m].sort_values("score",ascending=False).head(20).to_string(index=False))
    print("\n Worst20 for",m,"\n")
    wst=res["WORST20_"+m]
    if len(wst)==0:
        print("no zero-percent crime heads.\n")
    else:
        print(wst.sort_values("Total Arrests",ascending=False).to_string(index=False))
