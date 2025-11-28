import pandas as pd, re, os

file = "Crime Head-wise Age Group and Gender-wise Persons Arrested under IPC Crimes in Metropolitan Cities during 2021.csv"
df = pd.read_csv(file)

ex = r"(total|other|misc)"
df = df[~df["Crime Head"].str.lower().str.contains(ex)]

df["Sl. No."] = df["Sl. No."].astype(str)

cols = [c for c in df.columns if c not in ["Sl. No.","Crime Head"]]

def pick(c):
    x = c.lower()
    return "male" in x or "female" in x or "trans" in x or "boys" in x or "girls" in x

target = [c for c in cols if pick(c)]
df[target] = df[target].apply(pd.to_numeric, errors="coerce").fillna(0)

df["P"] = df["Sl. No."].str.split(".").str[0]
out = df.groupby("P")[target].sum().reset_index()

names = df[df["Sl. No."]==df["P"]][["Sl. No.","Crime Head"]].rename(columns={"Sl. No.":"P"})
out = out.merge(names, on="P", how="left")
out = out.rename(columns={"P":"Sl. No."})

fillmap = df.groupby("P")["Crime Head"].first()
out["Crime Head"] = out["Crime Head"].fillna(out["Sl. No."].map(fillmap))

rank = {}
for c in target:
    x = out.sort_values(c,ascending=False)[["Crime Head",c]].head(10).reset_index(drop=True)
    rank[c]=x

g_total, a_total, ag = {}, {"Juvenile":0,"18–30":0,"30–45":0,"45–60":0,"60+":0}, {}

def lab(col):
    s = col.lower()
    if "male" in s and "female" not in s: sex="Male"
    elif "female" in s: sex="Female"
    elif "trans" in s: sex="Transgender"
    else: return None,None
    
    if "juvenile" in s: age="Juvenile"
    elif "below 30" in s: age="18–30"
    elif "below 45" in s: age="30–45"
    elif "below 60" in s: age="45–60"
    elif "60" in s: age="60+"
    else: age=None

    return sex,age

for c in target:
    s,a = lab(c)
    if not s: continue
    g_total[s] = g_total.get(s,0)+out[c].sum()
    if a: a_total[a] += out[c].sum()
    if a and s:
        key = f"{s} | {a}"
        ag[key] = ag.get(key,0)+out[c].sum()

for k,v in rank.items():
    print("\n>>",k,"\n",v.to_string(index=False))

print("\nGENDER:",g_total)
print("\nAGE:",a_total)
print("\nAGE x GENDER:",ag)

save = "crime_results.xlsx"
with pd.ExcelWriter(save,engine="openpyxl") as w:

    for k,t in rank.items():
        nm = k[:28]+"..." if len(k)>30 else k
        t.to_excel(w,nm,index=False)

    pd.DataFrame(list(g_total.items()),columns=["Gender","Total"]).to_excel(w,"Gender Totals",index=False)
    pd.DataFrame(list(a_total.items()),columns=["Age","Total"]).to_excel(w,"Age Totals",index=False)
    pd.DataFrame(list(ag.items()),columns=["Age|Gender","Total"]).to_excel(w,"Age-Gender Totals",index=False)

print("\nSaved:",save)
