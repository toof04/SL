Directory Structure:
Plots/  - containing the csvs file split into their respective categorized folders
static/
      script.js
templates/
      index.html
app.py 


script.js 
  - Handles all the dynamic buttons of the web app.
  - Converts JSON format of the converted CSVs to plots.
  - Uses Chart.JS to plot graphs

app.py
  - Acts as the server for hosting our web app.
  - loads index.html
  - Routes all the requests properly.
  - Recieves request from JS buttons, fetches csv files and converts them to JSON format to send them to script.js

index.html:
  - Loads the template and structure of our website.
  - All the required buttons, divs and sections to hide/unhide are created here.


DATA ANalysis folder contains, code used to clean and process the raw csv fetched
the code was initially ipynb converted to python file for the purpose of submission to academic integrity
