import pandas as pd
import os

def split_statewise_crime(input_csv):

    df = pd.read_csv(input_csv)

    base_folder = os.path.dirname(input_csv)

    crime_cols = df.columns[1:]

    for _, row in df.iterrows():
        
        state = str(row["State"]).strip()

        safe_name = "".join(c for c in state if c.isalnum() or c in " _-").rstrip()
        out_path = os.path.join(base_folder, f"{safe_name}.csv")

        out_df = pd.DataFrame({
            "Crime Type": crime_cols,
            "Value": [row[c] for c in crime_cols]
        })

        out_df.to_csv(out_path, index=False)
        print(f"Saved: {out_path}")

    print("All state-wise CSVs created successfully.")

split_statewise_crime("State_Crime.csv")