import pandas as pd
import os

def split_csv_by_row(input_csv):
    
    df = pd.read_csv(input_csv)

    base_folder = os.path.dirname(input_csv)

    for idx, row in df.iterrows():

        state_name = str(row["State/UT"]).strip()

        safe_name = "".join(c for c in state_name if c.isalnum() or c in " _-").rstrip()
        out_path = os.path.join(base_folder, f"{safe_name}.csv")

        row_df = pd.DataFrame({
            "Religion": df.columns[1:],      
            "Value": row[df.columns[1:]].values
        })

        row_df.to_csv(out_path, index=False)
        print(f"Saved: {out_path}")

    print("All CSVs created.")

split_csv_by_row("Statewise_Percentages.csv")

pwd

import pandas as pd
import os

def split_csv_by_religion(input_csv):
    
    df = pd.read_csv(input_csv)

    base_folder = os.path.dirname(input_csv)

    religion_columns = df.columns[1:]

    for religion in religion_columns:

        safe_name = "".join(c for c in religion if c.isalnum() or c in " _-").rstrip()
        out_path = os.path.join(base_folder, f"{safe_name}.csv")

        rel_df = pd.DataFrame({
            "State/UT": df["State/UT"],
            "Value": df[religion]
        })

        rel_df.to_csv(out_path, index=False)
        print(f"Saved: {out_path}")

    print("All religion-wise CSVs created.")

split_csv_by_religion("Statewise_Percentages.csv")