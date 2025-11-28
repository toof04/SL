import pandas as pd

df= pd.read_csv(
    "State_UT-wise_Number_of_Schools_by_Management_and_Availability_of_Computer_Facility_during_2021-22.csv"
)

output= df[
    [
        "India/ State/ UT",
        "Percentage of Schools with Computer Facility - All Management",
        "Total Schools - All Management"
    ]
]

output = output.rename(columns={"India/ State/ UT": "State"})

output.to_csv("state_computer_facility_summary.csv", index=False)

print("Generated: state_computer_facility_summary.csv")