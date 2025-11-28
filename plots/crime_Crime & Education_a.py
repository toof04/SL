import pandas as pd, re, numpy as np

p="State_UT-wise Education Profile of Convicts as on 31st December, 2020.csv"
df=pd.read_csv(p)
df.columns=df.columns.str.strip()

drop = ["Total (All-India)","Total (States)","Total (UTs)"]
df=df[~df["State/UT"].isin(drop)].reset_index(drop=True)

edu=[ "Educational Standard - Illiterate",
      "Educational Standard - Below Class X",
      "Educational Standard - Class X & above but below Graduation",
      "Educational Standard - Graduate",
      "Educational Standard - Holding Tech. Degree/ Diploma",
      "Educational Standard - Post Graduate"]

tot="Educational Standard - Total"

state_tables={}
for _,r in df.iterrows():
    st=r["State/UT"]; tt=r[tot]
    t=pd.DataFrame({"Edu":edu,
                    "Cnt":[r[c] for c in edu],
                    "Pct":[(r[c]/tt*100) if tt>0 else 0 for c in edu]})
    state_tables[st]=t

edu_tables={}
india={c:df[c].sum() for c in edu}
for c in edu:
    s=india[c]
    t=pd.DataFrame({"State":df["State/UT"],
                    "Cnt":df[c],
                    "PctIndia":df[c]/s*100 if s>0 else 0})
    t=t.sort_values("PctIndia",ascending=False)
    edu_tables[c]=t

print("\nstate-wise breakdown\n")
for st,t in state_tables.items():
    print("\n--",st,"--")
    print(t.to_string(index=False))

print("\neducation level -> state share view\n")
for ed,t in edu_tables.items():
    print("\n##",ed,"##")
    print(t.to_string(index=False))


top5_state={}
for c in edu:
    tmp=df.copy()
    tmp[c+" pct"]=tmp[c]/tmp[tot]*100
    top5_state[c]=tmp.sort_values(c+" pct",ascending=False).head(5)

print("\ntop 5 states per education level\n")
for c,t in top5_state.items():
    print("\n>>>",c,"<<<")
    print(t[["State/UT",c,c+" pct"]].to_string(index=False))


top5_edu={}
for c in edu:
    tmp=df.copy()
    totc=india[c]
    tmp[c+" india%"]=tmp[c]/totc*100 if totc>0 else 0
    top5_edu[c]=tmp.sort_values(c+" india%",ascending=False).head(5)

print("\ntop5 contribution to india by level\n")
for c,t in top5_edu.items():
    print("\n***",c,"***")
    print(t[["State/UT",c,c+" india%"]].to_string(index=False))


nat=pd.DataFrame({"Edu":edu,"Cnt":[df[c].sum() for c in edu]})
sum_all = nat["Cnt"].sum()
nat["India%"] = nat["Cnt"]/sum_all*100

print("\nnational trend\n")
print(nat.to_string(index=False))


#    outliers 
outs={}
for c in edu:
    z=df.copy()
    z[c+" pct"]=z[c]/z[tot]*100
    vals=z[c+" pct"]
    m=vals.mean();s=vals.std()
    hi=z[z[c+" pct"]>m+2*s][["State/UT",c+" pct"]]
    lo=z[z[c+" pct"]<m-2*s][["State/UT",c+" pct"]]
    outs[c]={"hi":hi,"lo":lo}

print("\noutlier states\n")
for c,v in outs.items():
    print("\n--",c,"--")
    print("high spikes:"); print(v["hi"].to_string(index=False) if not v["hi"].empty else "none")
    print("\nlow dips:");   print(v["lo"].to_string(index=False) if not v["lo"].empty else "none")


def fix(nm):
    nm=re.sub(r'[\/\\\?\*\[\]\:]',"_",nm).strip()
    return nm[:26]+"__" if len(nm)>31 else nm

out="convict_education_out.xlsx"

with pd.ExcelWriter(out,engine="openpyxl") as w:

    for st,t in state_tables.items():
        t.to_excel(w,sheet_name=fix("state_"+st),index=False)

    for ed,t in edu_tables.items():
        t.to_excel(w,sheet_name=fix("edu_"+ed),index=False)

    for c,t in top5_state.items():
        t.to_excel(w,sheet_name=fix("top_state_"+c),index=False)

    for c,t in top5_edu.items():
        t.to_excel(w,sheet_name=fix("top_india_"+c),index=False)

    nat.to_excel(w,sheet_name="NationalOverall",index=False)

print("\nfile generated ->",out,"\n")
