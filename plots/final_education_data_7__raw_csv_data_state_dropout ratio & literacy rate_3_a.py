import pandas as pd, os

x="Literacy_Rate_In_India_(State_wise)_upto_2011.csv"
df=pd.read_csv(x)

a="1991 - Persons"
b="2001 - Persons"
r="2011 - Rural - Person"
u="2011 - Urban - Persons"

od="state_outputs"
os.makedirs(od,exist_ok=True)

for i,row in df.iterrows():
    st=row["All India/State/Union Territory"]
    if str(st).lower()=="all india": continue
    t=pd.DataFrame({
        "Y":["1991","2001","2011R","2011U"],
        "P":[row[a],row[b],row[r],row[u]]
    })
    fn=os.path.join(od,f"{st}_ts.csv")
    t.to_csv(fn,index=False)

L=[]
for i,row in df[df["All India/State/Union Territory"]!="All India"].iterrows():
    st=row["All India/State/Union Territory"]
    c=(row[r]+row[u])/2
    m=(row[a]+row[b]+c)/3
    L.append({"State":st,"1991":row[a],"2001":row[b],"2011R":row[r],"2011U":row[u],"2011C":c,"Avg":m})

R=pd.DataFrame(L).sort_values("Avg",False)
t10=R.head(10); b10=R.tail(10)

t10.to_csv("top10.csv",index=False)
b10.to_csv("bottom10.csv",index=False)

use=["State","1991","2001","2011R","2011U","2011C"]

t10[use].to_csv("top10_ts.csv",index=False)
b10[use].to_csv("bottom10_ts.csv",index=False)

print("done")
