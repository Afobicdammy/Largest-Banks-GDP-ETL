# importing libraries
import requests
import sqlite3
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime


# Criteria
url = 'https://web.archive.org/web/20230908091635 /https://en.wikipedia.org/wiki/List_of_largest_banks'
exchange_rate_url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv'

table_attribs = ['Name','MC_USD_Billion']
table_attribs_final = ['Name','MC_USD_Billion','MC_GBP_Billion','MC_EUR_Billion','MC_INR_Billion']
exchange_path = 'exchange_rate.csv'
table_name = 'Largest_banks'
db_name = 'Banks.db'
output_path = 'Largest_banks_gdp.csv'
log_file = 'code_log.txt'

# Step1: Write to log file
def log_progress(message):
    timestamp_format = "%Y-%h-%d-%H:%M:%S" # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now() # get current timestamp
    timestamp = now.strftime(timestamp_format)
    with open(log_file,"a") as f:
        f.write(timestamp + " : " + message + "\n")

# Step2: Extract data from url
def extract(url, table_attribs):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")

    df = pd.DataFrame(columns=table_attribs)

    tables = soup.find_all("tbody")
    rows = tables[0].find_all("tr")

    for row in rows:
        col = row.find_all("td")
        if len(col) != 0:
            data_dict = {"Name": col[1].find_all("a")[1]["title"],
                         "MC_USD_Billion": float(col[2].contents[0])}
            df1 = pd.DataFrame(data_dict, index=[0])
            df = pd.concat([df, df1], ignore_index=True)

    return df

# Step 3: Transform Data
def transform(df,exchange_path):
    exchange_rate = pd.read_csv(exchange_path)

    exchange_rate = exchange_rate.set_index("Currency").to_dict()["Rate"]
    df["MC_GBP_Billion"] = [np.round(x * exchange_rate["GBP"], 2) for x in df["MC_USD_Billion"]]
    df["MC_EUR_Billion"] = [np.round(x * exchange_rate["EUR"], 2) for x in df["MC_USD_Billion"]]
    df["MC_INR_Billion"] = [np.round(x * exchange_rate["INR"], 2) for x in df["MC_USD_Billion"]]

    return df

# Step 4: Loading to CSV
def load_to_csv(df, output_path):
    df.to_csv(output_path)

# Step 5: Loading to Database
def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

# Step 6: Function to Run queries on Database
def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)


log_progress("Initiating ETL process")

log_progress(" ")

log_progress("Extraction Process")

# Call extract() function
df = extract(url, table_attribs)
print(df)

log_progress("Transformation process")

# Call transform() function
df = transform(df, exchange_path)
print(df)

log_progress("Loading process")

# Call load_to_csv()
load_to_csv(df, output_path)

log_progress("Data loaded to CSV")

# Initiate SQLite3 connection
sql_connection = sqlite3.connect(db_name)

log_progress("SQL Connection initiated")

# Call load_to_db()
load_to_db(df, sql_connection, table_name)

log_progress("Data loaded to Database")

# Call run_query()
# 1. Print the contents of the entire table
query_statement = f"SELECT * from {table_name}"
run_query(query_statement, sql_connection)

# 2. Print the average market capitalization of all the banks in Billion GBP
query_statement = f"SELECT AVG(MC_GBP_Billion) FROM {table_name}"
run_query(query_statement, sql_connection)

# 3. Print only the names of the top 5 banks
query_statement = f"SELECT Name from {table_name} LIMIT 5"
run_query(query_statement, sql_connection)

log_progress("Process Complete")

log_progress(" ")

log_progress("Data query") 

log_progress("Data query: Print the contents of the entire table")
query_statement = f"SELECT * from {table_name}"
run_query(query_statement, sql_connection)

log_progress("Print the average market capitalization of all the banks in Billion GBP")
query_statement = f"SELECT AVG(MC_GBP_Billion) FROM {table_name}"
run_query(query_statement, sql_connection)

log_progress("Print only the names of the top 5 banks")
query_statement = f"SELECT Name from {table_name} LIMIT 5"
run_query(query_statement, sql_connection)

log_progress(" ")

log_progress("Query Complete")

# Close SQLite3 connection
sql_connection.close()

# Step 7: Verify log entries
with open(log_file, "r") as log:
    LogContent = log.read()
    print(LogContent)