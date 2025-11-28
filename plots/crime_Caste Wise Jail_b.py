import pandas as pd, re

df = pd.read_csv("State_UT-wise Caste of Detenues as on 31st December, 2020.csv")
cols = ["SC","ST","OBC","Others","Total"]
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

x = df.copy()
x = x[~x["State/UT"].str.lower().str.contains("total")]
x = x[x["Total"]>0]
x = x[x["State/UT"].str.lower()!="maharashtra"]
x = x.reset_index(drop=True)

view = x[["State/UT","SC","ST","OBC","Others","Total"]]

print("\n-- state wise caste detenues table --\n")
print(view.to_string(index=False))

print("\n-- top 5 states per caste (detenues count) --\n")

for z in ["SC","ST","OBC","Others"]:
    t = x[["State/UT",z]].sort_values(z,ascending=False).head(5).reset_index(drop=True)
    print("\n*",z,"*")
    print(t.to_string(index=False))


def fix(n):
    n = re.sub(r'[\/\\\?\*\[\]\:]',"_",n).strip()
    return n[:27]+".." if len(n)>31 else n

f = "detenues_caste_analysis.xlsx"

with pd.ExcelWriter(f, engine="openpyxl") as w:

    view.to_excel(w, sheet_name=fix("States_Caste_Detenues"), index=False)

    for z in ["SC","ST","OBC","Others"]:
        tmp = x[["State/UT",z]].copy()
        top5 = tmp.sort_values(z,ascending=False).head(5).reset_index(drop=True)
        top5.to_excel(w, sheet_name=fix(z+"_Top5List"), index=False)

print(f)
