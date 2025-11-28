import pandas as pd, re

p="Nature of Property-wise Value of Property Stolen & Recovered (in Crores) and Percentage Recovery during 2021.csv"
d=pd.read_csv(p)
d.columns=d.columns.str.strip()

a=d.columns[0]
b=d.columns[1]
s=[c for c in d.columns if "stolen" in c.lower()][0]
r=[c for c in d.columns if "recover" in c.lower()][0]

rm=["total","all india"]
d=d[~d[b].str.lower().str.contains("|".join(rm))].reset_index(drop=True)

def ok(x): return bool(re.fullmatch(r"\d+",str(x).strip()))
def sub(x): return bool(re.fullmatch(r"\d+\.\d+",str(x).strip()))

main=d[d[a].apply(ok)].copy()
ts=main[s].sum()
tr=main[r].sum()

main["st%"]=main[s]/ts*100
main["rec%"]=main[r]/tr*100

t4s=main.sort_values(s,ascending=False).head(4)
b3s=main.sort_values(s).head(3)
t4r=main.sort_values(r,ascending=False).head(4)
b4r=main.sort_values(r).head(4)

subd=d[d[a].apply(sub)].copy()
subd["G"]=subd[a].astype(str).str.extract(r"^(\d+)\.")
Gs=sorted(subd["G"].unique())
res={}

for g in Gs:
    gdf=subd[subd["G"]==g]
    st=gdf[s].sum(); rc=gdf[r].sum()
    gdf["st%"]=gdf[s]/st*100
    gdf["rc%"]=gdf[r]/rc*100
    if g=="1":
        res[g]={"t_s":gdf.sort_values(s,False).head(3),
                "b_s":gdf.sort_values(s).head(4),
                "t_r":gdf.sort_values(r,False).head(3),
                "b_r":gdf.sort_values(r).head(3)}
    if g=="2":
        res[g]={"t_s":gdf.sort_values(s,False).head(2),
                "b_s":gdf.sort_values(s).head(2),
                "t_r":gdf.sort_values(r,False).head(2),
                "b_r":gdf.sort_values(r).head(2)}

print("\nmain category\n")
print("\ntop stolen\n",t4s[[a,b,s,"st%"]])
print("\nbottom stolen\n",b3s[[a,b,s,"st%"]])
print("\ntop recovered\n",t4r[[a,b,r,"rec%"]])
print("\nbottom recovered\n",b4r[[a,b,r,"rec%"]])

print("\nsubcategory\n")
for g in Gs:
    print("\nG",g,"\n")
    print("top stolen")
    print(res[g]["t_s"][[a,b,s,"st%"]])
    print("\nbottom stolen")
    print(res[g]["b_s"][[a,b,s,"st%"]])
    print("\nTOP rec")
    print(res[g]["t_r"][[a,b,r,"rc%"]])
    print("\nbottom rec")
    print(res[g]["b_r"][[a,b,r,"rc%"]])


def fx(n):
    n=re.sub(r'[\/\\\?\*\[\]\:]','_',n).strip()
    return n[:28]+".." if len(n)>31 else n

out="property_stolen_recovered_analysis.xlsx"
with pd.ExcelWriter(out,engine="openpyxl") as w:
    t4s.to_excel(w,fx("M_T4_St"),index=False)
    b3s.to_excel(w,fx("M_B3_St"),index=False)
    t4r.to_excel(w,fx("M_T4_Rc"),index=False)
    b4r.to_excel(w,fx("M_B4_Rc"),index=False)

    g="1"
    res[g]["t_s"].to_excel(w,fx("G1_T3_St"),index=False)
    res[g]["b_s"].to_excel(w,fx("G1_B4_St"),index=False)
    res[g]["t_r"].to_excel(w,fx("G1_T3_Rc"),index=False)
    res[g]["b_r"].to_excel(w,fx("G1_B3_Rc"),index=False)

    g="2"
    res[g]["t_s"].to_excel(w,fx("G2_T2_St"),index=False)
    res[g]["b_s"].to_excel(w,fx("G2_B2_St"),index=False)
    res[g]["t_r"].to_excel(w,fx("G2_T2_Rc"),index=False)
    res[g]["b_r"].to_excel(w,fx("G2_B2_Rc"),index=False)

print("\nfile ->",out,"\n")
