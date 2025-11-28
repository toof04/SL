import pandas as pd, re

fp = "State_City-wise Disposal of Persons Arrested under Indian Penal Code and Special & Local Laws (IPC & SLL) Crimes (in Metropolitan Cities) during 2021.csv"
df = pd.read_csv(fp)

df.columns = df.columns.str.strip()
if "Sl. No." in df.columns:
    df = df.drop(columns=["Sl. No."])

df = df[~df["City"].str.contains("total", case=False, na=False)]
df["City"] = df["City"].str.strip()

print("\n city – total arrests (abs + %) \n")

ts = df["Persons Arrested - Total"].sum()
df["Arrest_pct"] = df["Persons Arrested - Total"] / ts * 100

print(
    df[["City","Persons Arrested - Total","Arrest_pct"]]
    .sort_values("Persons Arrested - Total",ascending=False)
    .to_string(index=False)
)

gender = pd.DataFrame({
    "Gender":["Male","Female","Transgender"],
    "Arrests":[df["Persons Arrested - Male"].sum(),df["Persons Arrested - Female"].sum(),df["Persons Arrested - Transgender"].sum()],
    "CS":[df["Persons Charge sheeted - Male"].sum(),df["Persons Charge sheeted - Female"].sum(),df["Persons Charge sheeted - Transgender"].sum()],
    "Conv":[df["Persons Convicted - Male"].sum(),df["Persons Convicted - Female"].sum(),df["Persons Convicted - Transgender"].sum()],
    "Acq":[df["Persons Acquitted - Male"].sum(),df["Persons Acquitted - Female"].sum(),df["Persons Acquitted - Transgender"].sum()]
})

for c in ["Arrests","CS","Conv","Acq"]:
    t = gender[c].sum()
    gender[c+" pct"] = gender[c]/t*100

print("\n gender split table \n")
print(gender.to_string(index=False))

df["ConvictRate"] = df["Persons Convicted - Total"] / (df["Persons Convicted - Total"] + df["Persons Acquitted - Total"]) * 100

print("\n conviction rate by city \n")
print(df[["City","ConvictRate"]].sort_values("ConvictRate",ascending=False).to_string(index=False))

print("\ndef: convicted_total / (convicted_total + acquitted_total) *100\n")

pipe = pd.DataFrame()
pipe["City"] = df["City"]
pipe["Arr"] = df["Persons Arrested - Total"]
pipe["CS"] = df["Persons Charge sheeted - Total"]
pipe["Conv"] = df["Persons Convicted - Total"]
pipe["Acq"] = df["Persons Acquitted - Total"]
pipe["CS%"] = pipe["CS"]/pipe["Arr"]*100
pipe["Conv%"] = pipe["Conv"]/pipe["Arr"]*100
pipe["Acq%"] = pipe["Acq"]/pipe["Arr"]*100
pipe = pipe.sort_values("Arr",ascending=False)

print("\n justice pipeline % based on arrests \n")
print(pipe.to_string(index=False))


def rank(df_,col):
    print(f"\n top 5 — {col} \n")
    print(df_[['City',col]].sort_values(col,ascending=False).head(5).to_string(index=False))
    print(f"\n bottom 5 — {col} \n")
    print(df_[['City',col]].sort_values(col,ascending=True).head(5).to_string(index=False))

rank(pipe,"CS%")
rank(pipe,"Conv%")
rank(pipe,"Acq%")


def clean(x):
    x = re.sub(r'[\/\\\?\*\[\]\:]',"_",x).strip()
    if len(x)>31: x = x[:25]+"__"
    return x

out="crime_analysis_full_report.xlsx"

with pd.ExcelWriter(out,engine="openpyxl") as w:

    df[["City","Persons Arrested - Total","Arrest_pct"]]\
       .sort_values("Persons Arrested - Total",ascending=False)\
       .to_excel(w,sheet_name=clean("City_Arrests"),index=False)

    gender.to_excel(w,sheet_name=clean("Gender_View"),index=False)

    df[["City","ConvictRate"]].sort_values("ConvictRate",ascending=False)\
       .to_excel(w,sheet_name=clean("City_Conv_Rank"),index=False)

    pipe.to_excel(w,sheet_name=clean("Pipeline"),index=False)

    for met in ["CS%","Conv%","Acq%"]:
        b = pipe[['City',met]].sort_values(met,ascending=False).head(5)
        wst = pipe[['City',met]].sort_values(met,ascending=True).head(5)
        b.to_excel(w,sheet_name=clean("Top5_"+met),index=False)
        wst.to_excel(w,sheet_name=clean("Bottom5_"+met),index=False)

print("\nfile generated ->",out,"\n")
