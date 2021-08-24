"""
Convert excel file with budget kpis https://docs.google.com/spreadsheets/d/1tN3NUNsDV-If6NqcNOKYTNxvODD5vsqBUnz6VQckhDE/edit#gid=1719544968
to sql statement
"""

#%% init
import os
import pandas as pd
import csv

data_path = "~/Documents/DataVault/kpi/"
excel_name = "budget_kpi_20210823.xlsx"
src_excel = data_path + excel_name
dest_filename = os.path.expanduser(data_path + os.path.splitext(excel_name)[0] + ".sql")
dest_table_name = "DAILY_BUDGET"

tmp_csv_name = 'tmp_file.csv'

#%% convert file to csv
rdf = pd.read_excel(src_excel, sheet_name="Plik wsadowy")

df = (rdf.iloc[:,8:]
      .assign(created_at="$insert_ts")
    #   .assign(active_buyer_l1d=None, active_buyer_l7d=None, active_buyer_mtd=None, active_buyer_ytd=None)
)
df.columns = (x.lower() for x in df.columns.tolist())

df.to_csv(tmp_csv_name, index=False, date_format="%Y-%m-%d", quoting=csv.QUOTE_NONNUMERIC, float_format='%.4f', quotechar="'", na_rep="NULL")

#%% convert csv to sql statment
with open(tmp_csv_name, "r") as rf:
    csv_content =  rf.readlines()

with open(dest_filename, "w") as wf:

    wf.writelines((
    "USE ROLE DEVOPS_ROLE_{ENV_NAME};\n",
    "USE DATABASE ALLEGRO_PAY_{ENV_NAME};\n",
    "USE SCHEMA KPI;\n",
    "\n",
    "SET insert_ts = CURRENT_TIMESTAMP;\n",
    "\n",
    ))

    for n, line in enumerate(csv_content, start=1):
        if n == 1:
            nline = line.replace("'", "").replace(",", ", ").lower().strip()
            wf.write(f"INSERT INTO {dest_table_name} ({nline}) VALUES\n")
        else:
            nline = "(" + line.strip().replace("'$insert_ts'", "$insert_ts").replace(",", ", ").replace("'NULL'", "NULL")

            if n < len(csv_content):
                nline = nline + "),\n"
            else:
                nline = nline + ")\n;"
            wf.write(nline)


print("DONE")

# %%
