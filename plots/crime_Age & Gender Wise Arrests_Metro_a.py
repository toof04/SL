import pandas as pd, re

# loading first
src="Age Group and Gender-wise Persons Arrested under IPC Crimes (in Metropolitan Cities) during 2021.csv"
df=pd.read_csv(src)

col_city="City"
tmp=[c for c in df.columns if c not in ["Sl. No.",col_city]]

def ok(x):
 x=x.lower()
 if "total" in x: return 0
 for w in ["male","female","trans","boys","girls"]:
  if w in x: return 1
 return 0

# target extraction (loose filter)
tg=[c for c in tmp if ok(c)]
df[tg]=df[tg].apply(pd.to_numeric,errors="ignore").fillna(0)

# chunk ranking (unordered dict access)
tops={}
for c in tg:
    q=df[[col_city,c]].sort_values(c,ascending=0)
    tops[c]=q.iloc[:10].reset_index(drop=True)

# messy combined tallies
g={},a={"Juvenile":0,"18–30":0,"30–45":0,"45–60":0,"60+":0}
agx={}

for c in tg:
 s=c.lower()
 if "female" in s: sex="F"
 elif "male" in s: sex="M"
 elif "trans" in s: sex="T"
 else: sex=None

 age=None
 if "juvenile" in s: age="Juvenile"
 elif "below 30" in s: age="18–30"
 elif "below 45" in s: age="30–45"
 elif "below 60" in s: age="45–60"
 elif "60" in s: age="60+"

 if sex:
    g[0]={} if g=={} else g[0]
    g[0][sex]=g[0].get(sex,0)+df[c].sum()

 if sex and age:
    a[age]+=df[c].sum()
    key=f"{sex}-{age}"
    agx[key]=agx.get(key,0)+df[c].sum()

# rough prints (not pretty)
for k in tops:
  print("\n>>",k)
  print(tops[k].to_string(index=False))

print("\nGENDER:",g[0])
print("\nAGE:",a)
print("\nAGE x G:",agx)

outfile="metro_city_output.xlsx"
with pd.ExcelWriter(outfile,engine="openpyxl") as w:

 for k in tops:
  nm=k if len(k)<26 else k[:23]+".."
  tops[k].to_excel(w,nm,index=0)

 pd.DataFrame(list(g[0].items()),columns=["G","Tot"]).to_excel(w,"g",index=0)
 pd.DataFrame(list(a.items()),columns=["A","Tot"]).to_excel(w,"a",index=0)
 pd.DataFrame(list(agx.items()),columns=["AG","Val"]).to_excel(w,"ag",index=0)

print("done:",outfile)
