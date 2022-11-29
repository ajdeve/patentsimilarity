import os
import sqlite3

import pandas as pd
from tqdm import tqdm

tqdm.pandas()

os.chdir(os.path.abspath(os.path.dirname(__file__)))

## Read CPC file
## Results in 2-column dataframe (patent_id, cpc_group)
## Sample output:
## |---------------------------------------------------------------|
## | patent_id |                                         cpc_group |
## |---------------------------------------------------------------|
## |  11399447 | [H05K7/20172, G11B33/142, H05K7/20145, H05K7/2... |
## |  11399448 | [H05K7/20327, H05K7/20318, H05K7/20781, H05K7/... |
## |  11399449 | [H05K7/20345, H05K7/20781, H05K7/20318, H05K7/... |
## |  11399450 | [H05K9/0041, G05B2219/31071, H05K7/1487, G05B1... |
## |  11399451 | [H05K13/0419, G05B19/042, H05K13/0417, H05K13/... |
## |---------------------------------------------------------------|

print("Reading CPC file.")
cpc = pd.read_csv(
    "./data/g_cpc_current.tsv.zip", sep="\t", usecols=["patent_id", "cpc_group"],
)

print("Processing CPC file.")
cpc_group = cpc.groupby("patent_id").agg(list)
cpc_group.reset_index(inplace=True)
cpc_group["patent_id"] = cpc_group["patent_id"].astype(str)

patent_list = cpc_group["patent_id"].to_list()

## Read Patent info file
## Results in 3-column dataframe (patent_id, patent_date, patent_title)
## Sample output:
## |-----------------------------------------------------------------------------|
## | patent_id | patent_date |                                      patent_title |
## |-----------------------------------------------------------------------------|
## |  10000000 |  2018-06-19 | Coherent LADAR using intra-pixel quadrature de... |
## |  10000001 |  2018-06-19 | Injection molding machine and mold thickness c... |
## |  10000002 |  2018-06-19 | Method for manufacturing polymer film and co-e... |
## |  10000003 |  2018-06-19 | Method for producing a container from a thermo... |
## |  10000004 |  2018-06-19 | Process of obtaining a double-oriented film, c... |
## |-----------------------------------------------------------------------------|

print("Reading Patents file.")
patents = pd.read_csv(
    "./data/g_patent.tsv.zip",
    sep="\t",
    usecols=["patent_id", "patent_date", "patent_title"],
    dtype={"patent_id": str, "patent_date": str, "patent_title": str},
)


## Read Claims files
## Results in 2-column dataframe (patent_id, claim_text)
## Claims text are separated by newline (\n)
## Sample output:
## |---------------------------------------------------------------|
## | patent_id |                                        claim_text |
## |---------------------------------------------------------------|
## |  11212952 | 1. A drive over mower deck automatic locking m... |
## |  11212953 | 1. A vehicle attachment carrier loading guidan... |
## |  11212954 | 1. An apparatus comprising: a guidance line ge... |
## |  11212955 | 1. A system for monitoring soil composition wi... |
## |  11212956 | 1. A method of making a seed quilt, the method... |
## |---------------------------------------------------------------|

print("Processing Claims files.")
claims = []
files = [file for file in os.listdir("./data/") if "claim" in file]
for file in tqdm(files):
    claims.append(
        pd.read_csv(
            "./data/" + file,
            sep="\t",
            usecols=["patent_id", "claim_text"],
            dtype={"patent_id": str, "claim_text": str},
        )
        .groupby("patent_id")
        .agg(" \n ".join)
    )

print("Concatenating Claims Files.")
claims = pd.concat(claims)
claims.reset_index(inplace=True)

## Merge files
## Results in 5-column dataframe (patent_id, patent_date, patent_title, cpc_group, claim_text)
## Sample output:
## |----------------------------------------------------------------------------------------------------------------------|
## | patent_id | patent_date |                patent_title |                  cpc_group |                      claim_text |
## |----------------------------------------------------------------------------------------------------------------------|
## |  11212952 |  2022-01-04 | Drive over mower deck au... | [A01B63/104, A01D2101/0... | 1. A drive over mower deck a... |
## |  11212953 |  2022-01-04 |       Vehicle attachment... | [A01B59/067, A01B69/001... | 1. A vehicle attachment carr... |
## |  11212954 |  2022-01-04 | Apparatus and methods fo... | [A01B69/001, A01B69/007... | 1. An apparatus comprising: ... |
## |  11212955 |  2022-01-04 | System and method for mo... | [A01C7/203, G01N33/24, ... | 1. A system for monitoring s... |
## |  11212956 |  2022-01-04 |         Growing seed quilts | [A01C1/044, A01G9/0293,... | 1. A method of making a seed... |
## |----------------------------------------------------------------------------------------------------------------------|

print("Merging Patents and CPC Files.")
df = patents.merge(cpc_group, on="patent_id", how="inner")

print("Adding Claims Text.")
df = df.merge(claims, on="patent_id", how="inner")

## Save file as checkpoint
filepath = "./data/all_claims.tsv.gz"
print(f"Saving File to {filepath}.")
df.to_csv(filepath, sep="\t", index=False, compression="gzip")

## Create new SQLite DB
## Database is a 2-table db.
## Table 1: Patents -- contains all basic patent excluding claims text (patent_id, patent_date, patent_title, cpc_group)
## Sample query -- "SELECT * FROM patents LIMIT 5":
## |----------------------------------------------------------------------------------------------------------------------|
## | patent_id | patent_date |                                      patent_title |                              cpc_group |
## |----------------------------------------------------------------------------------------------------------------------|
## |  11212952 |  2022-01-04 | Drive over mower deck automatic locking mechanism | ['A01B63/104', 'A01D2101/00', 'A01D... |
## |  11212953 |  2022-01-04 |       Vehicle attachment carrier loading guidance | ['A01B59/067', 'A01B69/001', 'H04N7... |
## |  11212954 |  2022-01-04 | Apparatus and methods for field operations bas... | ['A01B69/001', 'A01B69/007', 'A01B7... |
## |  11212955 |  2022-01-04 | System and method for monitoring soil conditio... | ['A01C7/203', 'G01N33/24', 'A01B79/... |
## |  11212956 |  2022-01-04 |                               Growing seed quilts | ['A01C1/044', 'A01G9/0293', 'A01G24... |
## |----------------------------------------------------------------------------------------------------------------------|
##
## Table 2: Claims -- contains all claims text and patent_id (patent_id, claim_text)
## Sample query -- "SELECT * FROM claims LIMIT 5":
## |---------------------------------------------------------------|
## | patent_id |                                        claim_text |
## |---------------------------------------------------------------|
## |  11212952 | 1. A drive over mower deck automatic locking m... |
## |  11212953 | 1. A vehicle attachment carrier loading guidan... |
## |  11212954 | 1. An apparatus comprising: a guidance line ge... |
## |  11212955 | 1. A system for monitoring soil composition wi... |
## |  11212956 | 1. A method of making a seed quilt, the method... |
## |---------------------------------------------------------------|

## Rename db here
dbpath = "../streamlit app/data/all_patents.db"
connex = sqlite3.connect(dbpath)
cur = connex.cursor()
print(f"Creating DB at {dbpath}.")

for chunk in tqdm(pd.read_csv(filepath, chunksize=100000, sep="\t")):
    chunk[["patent_id", "patent_date", "patent_title", "cpc_group"]].to_sql(
        name="patents", con=connex, if_exists="append", index=False
    )
    chunk[["patent_id", "claim_text"]].to_sql(
        name="claims", con=connex, if_exists="append", index=False
    )
cur.execute("CREATE INDEX patent_id_index ON claims (patent_id);")
