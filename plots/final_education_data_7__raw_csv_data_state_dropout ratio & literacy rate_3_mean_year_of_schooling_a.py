import pandas as pd
import os

df = pd.read_csv("mean_years_schooling_plfs_2022_23.csv")

outdir = "statewise_outputs"

    os.makedirs(outdir, exist_ok=True)

for _, row in df.iterrows():
    state = row["State_UT"]
    row_df = pd.DataFrame([row])
    row_df.to_csv(f"{outdir}/{state}.csv", index=False)

cols = ["15+_Male", "15+_Female", "25+_Male", "25+_Female"]

df["AverageScore"] = df[cols].mean(axis=1)

df_sorted = df.sort_values("AverageScore", ascending=False)

top10 = df_sorted.head(10)
bottom10 = df_sorted.tail(10)

top10.to_csv("top10_states.csv", index=False)
bottom10.to_csv("bottom10_states.csv", index=False)

print("Statewise files + Top/Bottom 10 files generated.")

import pandas as pd

top10 = pd.read_csv("top10_states.csv")
bottom10 = pd.read_csv("bottom10_states.csv")

if "AverageScore" in top10.columns:
    top10 = top10.drop(columns=["AverageScore"])

if "AverageScore" in bottom10.columns:
    bottom10 = bottom10.drop(columns=["AverageScore"])

top10.to_csv("top10_states.csv", index=False)
bottom10.to_csv("bottom10_states.csv", index=False)

print("AverageScore column removed successfully.")import pandas as pd

d=pd.read_csv("State_UT-wise_Number_of_Schools_by_Management_and_Availability_of_Computer_Facility_during_2021-22.csv")
x=d[["India/ State/ UT","Percentage of Schools with Computer Facility - All Management","Total Schools - All Management"]]
x=x.rename(columns={"India/ State/ UT":"State"})
x.to_csv("state_computer_facility_summary.csv",index=False)
print("ok file1")

import pandas as pd,os

z=pd.read_csv("mean_years_schooling_plfs_2022_23.csv")
o="statewise_outputs"; os.makedirs(o,exist_ok=True)

for _,r in z.iterrows():
    n=r["State_UT"]
    pd.DataFrame([r]).to_csv(f"{o}/{n}.csv",index=False)

C=["15+_Male","15+_Female","25+_Male","25+_Female"]
z["m"]=z[C].mean(axis=1)
q=z.sort_values("m",False)
t=q.head(10); b=q.tail(10)
t.to_csv("top10_states.csv",index=False)
b.to_csv("bottom10_states.csv",index=False)
print("ok file2")

T=pd.read_csv("top10_states.csv")
B=pd.read_csv("bottom10_states.csv")
if "m" in T.columns: T=T.drop(columns=["m"])
if "m" in B.columns: B=B.drop(columns=["m"])
T.to_csv("top10_states.csv",index=False)
B.to_csv("bottom10_states.csv",index=False)
print("removed avg col")
