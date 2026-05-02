import sys
#print('argumets',sys.argv)

month = int(sys.argv[1])
#print(f"Running pipeline for month {month}")

import pandas as pd
df = pd.DataFrame({"A":[1,2], "B":[3,4]})
df['month']=month
print(df.head())
print(f"hello pipeline, month={month}")
df.to_parquet(f"output_{month}.parquet")
print(f"Pipeline for month {month} completed successfully. Parquet file saved as output_{month}.parquet")