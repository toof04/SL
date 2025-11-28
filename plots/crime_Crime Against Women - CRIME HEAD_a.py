import pandas as pd, numpy as np, matplotlib.pyplot as plt, re, os

p="Crime against Women during 2001-2012.csv"
df=pd.read_csv(p)
df.columns=df.columns.str.strip()

drop=["total","all india","india"]
def bad(x):
    if pd.isna(x):return False
    s=str(x).lower().strip()
    return any(w in s for w in drop)

sc=[c for c in df.columns if re.search("state|ut|region",c,re.I)]
cc=[c for c in df.columns if re.search("crime|head|desc|type",c,re.I)]

scol=sc[0] if sc else "State/UT"
ccol=cc[0] if cc else "Crime"

df=df.rename(columns={scol:"State",ccol:"Crime"})
df=df[~df["State"].apply(bad)]
df=df[~df["Crime"].apply(bad)]
df=df.reset_index(drop=True)

df=df.loc[:,~df.columns.str.contains("total",case=False)]
df=df.loc[:,~df.columns.str.contains("all india",case=False)]

yrs=[c for c in df.columns if re.fullmatch(r"\d{4}",str(c))]
if not yrs:
    yrs=[c for c in df.columns if re.search(r"20\d{2}",str(c))]

long=df.melt(id_vars=["State","Crime"],value_vars=yrs,var_name="Year",value_name="Count")
long["Year"]=long["Year"].astype(str).str.extract(r"(\d{4})").astype(int)
long["Count"]=pd.to_numeric(long["Count"],errors="coerce").fillna(0).astype(int)

nat=long.groupby("Year",as_index=False)["Count"].sum().rename(columns={"Count":"Tot"})
crime_tot=long.groupby("Crime",as_index=False)["Count"].sum().rename(columns={"Count":"Tot"})
state_tot=long.groupby("State",as_index=False)["Count"].sum().rename(columns={"Count":"Tot"})

mx_state=long.groupby(["State","Crime"])["Count"].sum().unstack(fill_value=0)
mx_crime=long.groupby(["Crime","Year"])["Count"].sum().unstack(fill_value=0)

top_s={}
for s,g in long.groupby("State"):
    top_s[s]=g.groupby("Crime",as_index=False)["Count"].sum().sort_values("Count",ascending=False)

top_c={}
for c,g in long.groupby("Crime"):
    top_c[c]=g.groupby("State",as_index=False)["Count"].sum().sort_values("Count",ascending=False)

nat["YoY%"]=nat["Tot"].pct_change()*100

shr=long.groupby(["Year","Crime"],as_index=False)["Count"].sum()
shr=shr.merge(nat,on="Year",how="left")
shr["Share%"]=shr["Count"]/shr["Tot"]*100
shr_m=shr.pivot(index="Year",columns="Crime",values="Share%").fillna(0)

print("\nnational year trend\n")
print(nat)

print("\nstate totals\n")
print(state_tot.sort_values("Tot",ascending=False))

print("\ncrime totals\n")
print(crime_tot.sort_values("Tot",ascending=False))

print("\ncrime x year\n")
print(mx_crime)

print("\nstate x crime\n")
print(mx_state)

print("\nTop crimes per state\n")
for s,t in top_s.items():
    print("\n",s)
    print(t.head(5))

print("\nTop states per crime\n")
for c,t in top_c.items():
    print("\n",c)
    print(t.head(5))

print("\nCrime share each year\n")
print(shr_m)


def fix(n):
    n=re.sub(r'[\/\\\?\*\[\]\:]',"_",n)
    return n[:30]

out="Crime_Women_Analysis.xlsx"
with pd.ExcelWriter(out,engine="openpyxl") as w:
    long.to_excel(w,"Long",index=False)
    nat.to_excel(w,"NatYear",index=False)
    state_tot.to_excel(w,"StateTotal",index=False)
    crime_tot.to_excel(w,"CrimeTotal",index=False)
    mx_state.to_excel(w,"Mx_State",index=True)
    mx_crime.to_excel(w,"Mx_Crime",index=True)
    shr_m.to_excel(w,"Share",index=True)
    for s,t in top_s.items(): t.head(20).to_excel(w,fix("TopCrime_"+s),index=False)
    for c,t in top_c.items(): t.head(20).to_excel(w,fix("TopState_"+c),index=False)

print("\nsaved:",out)

def xls_to_csv(x):
    base=os.path.splitext(os.path.basename(x))[0]
    new=os.path.join(os.path.dirname(x),base)
    os.makedirs(new,exist_ok=True)
    xl=pd.ExcelFile(x)
    for sh in xl.sheet_names:
        d=pd.read_excel(x,sheet_name=sh)
        safe="".join(ch for ch in sh if ch.isalnum() or ch in " _-").rstrip()
        fp=os.path.join(new,f"{safe}.csv")
        d.to_csv(fp,index=False)
        print("ok →",fp)
    print("\nAll in:",new)

xls_to_csv(out)
