import os,json,pandas as pd

BD=os.getcwd()
OUT=os.path.join(BD,"_metadatasets_compact")
os.makedirs(OUT,exist_ok=True)

def sh(x):
    x=x.fillna("")
    return " | ".join(str(i).replace("\n"," ").strip() for i in x)

def go(p,n):
    z=os.path.join(p,"_raw_csv_data")
    if not os.path.exists(z):
        print("skip",n); return
    M={}
    for f in os.listdir(z):
        if not f.lower().endswith(".csv"): continue
        fp=os.path.join(z,f)
        try:
            d=pd.read_csv(fp)
            sm=[sh(r) for _,r in d.head(5).iterrows()]
            M[f]={"columns":d.columns.tolist(),"rows":sm}
        except Exception as e:
            M[f]={"err":str(e)}
    return M

def main():
    print("\nmake meta\n")
    for x in os.listdir(BD):
        p=os.path.join(BD,x)
        if os.path.isdir(p) and x.endswith("_data"):
            print("proc",x)
            r=go(p,x)
            if r:
                o=os.path.join(OUT,f"{x}_meta.json")
                with open(o,"w",encoding="utf-8") as F: json.dump(r,F,indent=2)
                print(" saved",o,"\n")
            else:
                print(" none",x,"\n")
    print("done\n")

if __name__=="__main__":
    main()
