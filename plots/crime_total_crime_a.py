import pandas as pd, numpy as np, matplotlib.pyplot as plt, os, re

p="State_UT-wise Number of Indian Penal Code (IPC) Crimes from 2020 to 2022.csv"
od="plot_ready"; os.makedirs(od,exist_ok=True)
pp=os.path.join(od,"plots"); os.makedirs(pp,exist_ok=True)

df=pd.read_csv(p); df.columns=df.columns.str.strip()
sc=[c for c in df.columns if re.search("state|ut|region",c,re.I)]
if sc: s=sc[0]
elif "State/UT" in df.columns: s="State/UT"
else: s=df.columns[0]

cc=[c for c in df.columns if re.search("crime|ipc|head|offen",c,re.I)]
cr=cc[0] if cc else None

rm=["total","all india","all-india","india","grand total"]
def bad(x):
    if pd.isna(x):return False
    return any(k in str(x).lower().strip() for k in rm)

df=df[~df[s].apply(bad)]
if cr: df=df[~df[cr].apply(bad)]
df=df.reset_index(drop=True)

yrs=[c for c in df.columns if re.match(r"^20(20|21|22)$",str(c))]
if not yrs:
    yrs=[c for c in df.columns if re.match(r"^20\d{2}$",str(c)) and 2015<=int(str(c)[:4])<=2025]
if not yrs: raise Exception("year error")

idv=[s]; 
if cr: idv.append(cr)
m=df.melt(id_vars=idv,value_vars=yrs,var_name="Y",value_name="N")
m["Y"]=m["Y"].astype(str).str.extract("(\d{4})").astype(int)
m["N"]=pd.to_numeric(m["N"],errors="coerce").fillna(0).astype(int)

if not cr: 
    m["Crime"]="ALL"
    cr="Crime"
else:
    m=m.rename(columns={cr:"Crime"})
    cr="Crime"

m=m.rename(columns={s:"State"})

nat=m.groupby("Y",as_index=False)["N"].sum().rename(columns={"N":"Tot"})
nat.to_csv(os.path.join(od,"nat_year.csv"),index=False)

plt.plot(nat["Y"],nat["Tot"],marker='o')
plt.tight_layout()
plt.savefig(os.path.join(pp,"nat.png")); plt.close()

st=m.groupby("State",as_index=False)["N"].sum().rename(columns={"N":"T2020_22"})
st=st.sort_values("T2020_22",False)
st.to_csv(os.path.join(od,"state_total.csv"),index=False)

tops=st.head(12)["State"].tolist()
for x in tops:
    g=m[m["State"]==x].groupby("Y",as_index=False)["N"].sum()
    fn=re.sub(r'[^0-9a-zA-Z]+','_',x)[:40]
    g.to_csv(os.path.join(od,f"s_ts_{fn}.csv"),index=False)
    plt.plot(g["Y"],g["N"],marker='o'); plt.title(x); plt.tight_layout()
    plt.savefig(os.path.join(pp,f"s_ts_{fn}.png")); plt.close()

for y in sorted(m["Y"].unique()):
    A=m[m["Y"]==y].groupby("State",as_index=False)["N"].sum().sort_values("N",False)
    A.head(10).to_csv(os.path.join(od,f"top10_{y}.csv"),index=False)
    A.tail(10).to_csv(os.path.join(od,f"bot10_{y}.csv"),index=False)
    plt.barh(A.head(10)["State"][::-1],A.head(10)["N"][::-1]); plt.title(str(y))
    plt.tight_layout(); plt.savefig(os.path.join(pp,f"top10_{y}.png")); plt.close()

crT=m.groupby("Crime",as_index=False)["N"].sum().sort_values("N",False)
crT.to_csv(os.path.join(od,"crime_nat.csv"),index=False)

mc=8; big=crT.head(mc)["Crime"].tolist()
t=m[m["Crime"].isin(big)].groupby(["Crime","Y"],as_index=False)["N"].sum()
t.to_csv(os.path.join(od,"crime_ts.csv"),index=False)

plt.figure(figsize=(7,4))
for cX in big:
    z=t[t["Crime"]==cX].sort_values("Y")
    plt.plot(z["Y"],z["N"],marker="o",label=cX)
plt.legend(fontsize=7,ncol=2); plt.tight_layout()
plt.savefig(os.path.join(pp,"crime_ts.png")); plt.close()

H=st.head(20)["State"].tolist()
h=m[m["State"].isin(H)].groupby(["State","Y"],as_index=False)["N"].sum()
pv=h.pivot("State","Y","N").fillna(0)
pv.to_csv(os.path.join(od,"heat.csv"))

plt.imshow(pv.values,aspect='auto',cmap='viridis')
plt.colorbar(); plt.yticks(range(len(pv.index)),pv.index)
plt.xticks(range(len(pv.columns)),pv.columns)
plt.tight_layout()
plt.savefig(os.path.join(pp,"heat.png")); plt.close()

pv2=m.pivot_table("N","State","Y",sum,fill_value=0)
yrs_ok=sorted(pv2.columns.tolist())
if len(yrs_ok)>1:
    y0,y2=yrs_ok[0],yrs_ok[-1]
    pv2["abs"]=pv2[y2]-pv2[y0]
    pv2["pct"]=pv2["abs"]/pv2[y0].replace({0:np.nan})*100
    G=pv2[["abs","pct"]].sort_values("pct",False).reset_index()
    G.to_csv(os.path.join(od,"grow_all.csv"),index=False)
    G.head(20).to_csv(os.path.join(od,"grow_top.csv"),index=False)
    G.tail(20).to_csv(os.path.join(od,"grow_low.csv"),index=False)

print("\nready")
print(os.path.abspath(od))
print(os.path.abspath(pp))
print("sample:")
for f in sorted(os.listdir(od))[:20]: print("->",f)
