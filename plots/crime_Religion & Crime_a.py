import pandas as pd, re

p="State_UT-wise Religion of Convicts as on 31st December, 2020.csv"
df=pd.read_csv(p)
df.columns=df.columns.str.strip()

bad=["total","all india","india"]
def chk(x):
    x=str(x).lower()
    return any(w in x for w in bad)

df=df[~df["State/UT"].apply(chk)].reset_index(drop=True)

cols=[c for c in df.columns if c not in ["Sl. No.","State/UT","Total"]]

if "Total" not in df.columns:
    df["Total"]=df[cols].sum(axis=1)
tcol="Total"

for c in cols:
    df[c+"%"]=df[c]/df[tcol]*100

hi={}
lo={}
for c in cols:
    pc=c+"%"
    s=df[["State/UT",c,pc]].sort_values(pc,ascending=False)
    hi[c]=s.head(5)
    lo[c]=s.tail(5)

print("\ntop 5 states by religion\n")
for c in cols:
    print("\n>>",c)
    print(hi[c].to_string(index=False))

print("\nbottom 5 states by religion\n")
for c in cols:
    print("\n>>",c)
    print(lo[c].to_string(index=False))

tot=df[cols].sum().reset_index()
tot.columns=["Religion","Count"]
g=tot["Count"].sum()
tot["India%"]=tot["Count"]/g*100

print("\nIndia total religion breakdown\n")
print(tot.to_string(index=False))


def fx(n):
    n=re.sub(r'[\/\\\?\*\[\]\:]','_',n).strip()
    return n[:28]+".." if len(n)>31 else n

out="religion_convicts_analysis.xlsx"
with pd.ExcelWriter(out,engine="openpyxl") as w:
    df.to_excel(w,"Clean",index=False)
    tot.to_excel(w,"AllIndia",index=False)
    for k,v in hi.items(): v.to_excel(w,fx("T5_"+k),index=False)
    for k,v in lo.items(): v.to_excel(w,fx("B5_"+k),index=False)
    pc=[c for c in df.columns if c.endswith("%")]
    pd.concat([df["State/UT"],df[pc]],axis=1).to_excel(w,"Percents",index=False)

print("\nwritten ->",out,"\n")
