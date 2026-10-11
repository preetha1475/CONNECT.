
import pandas as pd

path = r"C:\CONNECT\data\hospital_directory.csv"

df = pd.read_csv(path, low_memory=False)
df.columns = df.columns.str.strip()

print("Total records:", len(df))
print("Non-empty coordinates:",
      df["Location_Coordinates"].notna().sum())

print("\nSample records with coordinates:")
print(
    df.loc[
        df["Location_Coordinates"].notna(),
        ["Hospital_Name", "State", "District", "Location_Coordinates"]
    ].head(15).to_string(index=False)
)

print("\nChennai records with coordinates:")
mask = (
    df["State"].fillna("").astype(str).str.contains("Tamil Nadu", case=False)
    & df["District"].fillna("").astype(str).str.contains("Chennai", case=False)
)
print(df.loc[mask, "Location_Coordinates"].notna().sum())
