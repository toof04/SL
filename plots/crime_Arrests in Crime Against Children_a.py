import pandas as pd

source = "Crime head-wise persons arrested under crime against children during 2013.csv"
df = pd.read_csv(source)
df["2013"] = pd.to_numeric(df["2013"], errors="coerce").fillna(0)

all_india = df[df["STATE/UT"].str.lower().str.contains("all-india")]
crime_tot = {k:int(v) for k,v in all_india.groupby("CRIME HEAD")["2013"].sum().items()}

mask = ~df["STATE/UT"].str.contains("Total", case=False, na=False)
usable = df.loc[mask].copy()

states_by_crime = {}
for label in sorted(df["CRIME HEAD"].dropna().unique(), key=lambda x: str(x)):
    block = usable.loc[usable["CRIME HEAD"].eq(label), ["STATE/UT","2013"]]
    head10 = block.sort_values(by="2013", ascending=False).reset_index(drop=True)[:10]
    if len(head10)>0:
        states_by_crime[label] = head10

crime_by_state = {}
for st in usable["STATE/UT"].unique():
    blk = usable[usable["STATE/UT"]==st][["CRIME HEAD","2013"]]
    chunk = blk.sort_values("2013", ascending=False).reset_index(drop=True)
    crime_by_state[st] = chunk.iloc[:10]

print("\n@@@@ TOP 10 STATES FOR EACH CRIME HEAD @@@@@@@n")
for head,datax in states_by_crime.items():
    total = crime_tot[head] if head in crime_tot else 0
    print(f"\n--- {head} (Total = {total}) ---")
    print(datax.to_string(index=False))

print("\n####### TOP 10 CRIME HEADS FOR EACH STATE \n")
for st,datax in crime_by_state.items():
    total = usable.loc[usable["STATE/UT"]==st,"2013"].sum()
    print(f"\n--- {st} (Total = {total}) ---")
    print(datax.to_string(index=False))

out = "crime_children_analysis.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as xl:
    for head,frame in states_by_crime.items():
        name = head if len(head)<=31 else head[:28]+"..."
        frame.to_excel(xl, sheet_name="C-"+name, index=False)
    for st,frame in crime_by_state.items():
        nm = st if len(st)<=31 else st[:28]+"..."
        frame.to_excel(xl, sheet_name="S-"+nm, index=False)
    pd.DataFrame(list(crime_tot.items()), columns=["Crime Head","National Total"]).to_excel(xl,"Crime Totals",index=False)
    vals = [(s,int(usable.loc[usable["STATE/UT"]==s,"2013"].sum())) for s in usable["STATE/UT"].unique()]
    pd.DataFrame(vals, columns=["State/UT","Total"]).to_excel(xl,"State Summary",index=False)

out
